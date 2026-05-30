# PURPOSE: Forecast when the CURRENT phase will finish, from remaining blocks x measured
#          velocity. The `phase-forecast` registry entry pointed here for ages but the
#          script never existed -- the math lived inline in health_report._section_phase_progress.
#          This is the single source now: health_report + session_start both call forecast().
# INPUTS:  arch-root directory -> STATE.md (current phase, via project_state), the current
#          phase-N.md block table (remaining blocks), and completed retros (measured velocity).
# OUTPUTS: Forecast(remaining_blocks, est_days, confidence['MEASURED'|'ESTIMATED'],
#          completion_estimate). CLI prints a dated completion estimate + the label. ASCII-safe.
# DEPS:    stdlib only (re, math, argparse, datetime, statistics) + project_state,
#          velocity_inference, safe_io. NEVER imports health_report (would cycle).
# SEE:     phases/phase-26.md sec.2 (phase-completion forecast), manifests/block-151-phase-forecast.md,
#          sdk/velocity_inference.py (MEASURED/ESTIMATED discipline, block-138), sdk/project_state.py

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from statistics import mean
from typing import Optional

# Ensure sibling modules importable when run as a script (python sdk/phase_forecast.py).
sys.path.insert(0, str(Path(__file__).resolve().parent))

import project_state
import velocity_inference
from safe_io import force_utf8


# Tier-mean fallbacks when a tier has no measured retro samples. Mirrors
# health_report._VELOCITY_DEFAULTS so the shared forecast reads the same hours
# whichever caller drives it.
VELOCITY_DEFAULTS = {"S": 1.0, "M": 3.5, "L": 9.0}

# block-138 discipline: a tier mean is MEASURED only with >= this many real
# samples; below it the number is an ESTIMATE and must be labelled as such.
MEASURED_MIN_SAMPLES = 3

# Hours of focused block work assumed per calendar day (the inline math used /4).
HOURS_PER_DAY = 4


@dataclass
class Forecast:
    """A phase-completion projection plus the confidence it is allowed to claim.

    `remaining_blocks` is how many blocks of the current phase are not yet done.
    `est_days` is the projected calendar days to finish them (None only when there
    is nothing to forecast -- e.g. no phase file). `confidence` is the block-138
    label: 'MEASURED' when the velocity used rests on >= MEASURED_MIN_SAMPLES real
    retro samples, else 'ESTIMATED' (thin history must never be dressed as certain).
    `completion_estimate` is the ISO date the phase is projected to close (or a
    short reason string like 'phase complete' / 'unknown' when no date applies).
    """

    remaining_blocks: int
    est_days: Optional[float]
    confidence: str            # 'MEASURED' | 'ESTIMATED'
    completion_estimate: str   # ISO date 'YYYY-MM-DD', or a reason when no date


# ---------------------------------------------------------------------------
# Shared building blocks (used by forecast() AND health_report's section)
# ---------------------------------------------------------------------------

def phase_block_counts(arch_root: Path) -> tuple[int, int]:
    """(done_count, total_count) of blocks in the CURRENT phase's block table.

    Counts the same way the original inline health_report logic did: `| done |`
    status cells for done, `| block-NNN` rows for total (falling back to a
    "N blocks" header phrase if the table has no rows). Reads the current phase
    file via project_state (the single source of truth), so health_report and the
    forecaster agree on "how many blocks are left". Defensive: any failure -> (0, 0).
    """
    try:
        phase_file = project_state.current_phase_file(arch_root)
        if phase_file is None or not phase_file.exists():
            return 0, 0
        content = phase_file.read_text(encoding="utf-8")
    except Exception:
        return 0, 0

    done_count = len(re.findall(r"\|\s*done\s*\|", content, re.IGNORECASE))
    total_count = max(done_count, len(re.findall(r"\|\s*block-\d+", content, re.IGNORECASE)))
    if total_count == 0:
        m = re.search(r"(\d+)\s+blocks?", content, re.IGNORECASE)
        if m:
            total_count = int(m.group(1))
    return done_count, total_count


def measured_velocity(arch_root: Path) -> tuple[dict, dict]:
    """Per-tier mean active hours from completed retros, plus per-tier sample counts.

    Returns (means, counts) where means[T] is the mean measured duration for tier T
    (or VELOCITY_DEFAULTS[T] when no samples) and counts[T] is how many real samples
    backed it. Tier source priority mirrors health_report._collect_velocity_data:
    retro frontmatter `tier:` then a manifest-tier fallback (the 086-111 cohort omit
    `tier:` in their retros). Reuses velocity_inference helpers; never raises.
    """
    by_tier: dict[str, list[float]] = {"S": [], "M": [], "L": []}
    try:
        done_ids = project_state.completed_block_ids(arch_root)
        blocks_dir = arch_root / "blocks"
        if blocks_dir.exists():
            for block_id in done_ids:
                candidates = list(blocks_dir.glob(f"{block_id}-*.md")) or \
                    list(blocks_dir.glob(f"{block_id}.md"))
                if not candidates:
                    continue
                try:
                    content = candidates[0].read_text(encoding="utf-8")
                except OSError:
                    continue
                fm = _retro_frontmatter(content)
                try:
                    duration = float(fm.get("actual_duration_hours", "0"))
                except (ValueError, TypeError):
                    continue
                if duration <= 0:
                    continue
                tier = fm.get("tier", "").upper()
                if tier not in by_tier:
                    mp = velocity_inference._locate_manifest(block_id, arch_root)
                    if mp is None:
                        continue
                    tier = velocity_inference._tier_from_manifest(mp)
                    if tier not in by_tier:
                        continue
                by_tier[tier].append(duration)
    except Exception:
        # Defensive: a malformed arch yields no samples, never a crash.
        by_tier = {"S": [], "M": [], "L": []}

    means: dict = {}
    counts: dict = {}
    for tier in ("S", "M", "L"):
        data = by_tier[tier]
        counts[tier] = len(data)
        means[tier] = round(mean(data), 1) if data else VELOCITY_DEFAULTS[tier]
    return means, counts


def _retro_frontmatter(content: str) -> dict:
    """key:value pairs from a retro's YAML frontmatter (same parse as health_report)."""
    result: dict = {}
    in_fm = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "---":
            if not in_fm:
                in_fm = True
                continue
            break
        if in_fm and ":" in stripped:
            key, _, val = stripped.partition(":")
            result[key.strip()] = val.strip().strip("\"'#").strip()
    return result


def _per_block_hours(velocity_means: dict) -> float:
    """Hours to budget per remaining (unknown-tier) block.

    The inline forecast treated every remaining block as tier S (the conservative,
    smallest unit); kept identical here so health_report's number is unchanged.
    """
    return velocity_means.get("S", VELOCITY_DEFAULTS["S"])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def forecast(arch_root, velocity_means: Optional[dict] = None) -> Forecast:
    """Project the current phase's completion date from remaining blocks x velocity.

    The ONE definition of the phase-completion forecast: health_report's Phase
    Progress section and session_start's `Forecast:` line both call this. When
    `velocity_means` is supplied (health_report passes the exact means it already
    rendered), it is used as-is so the report's velocity table and its forecast can
    never drift; otherwise velocity is measured here from completed retros.

    Confidence is the block-138 label: MEASURED when the S-tier mean (the per-block
    unit the projection multiplies) rests on >= MEASURED_MIN_SAMPLES real samples,
    else ESTIMATED -- thin history is never presented as a hard date.

    NEVER raises (Phase 26 sec.3): any failure degrades to a conservative
    ESTIMATED Forecast with completion 'unknown'.
    """
    try:
        arch_root = Path(arch_root)
    except Exception:
        return Forecast(0, None, "ESTIMATED", "unknown")

    try:
        done_count, total_count = phase_block_counts(arch_root)
        remaining = max(0, total_count - done_count)

        # Velocity: caller-supplied (health_report) wins; else measure here.
        if velocity_means is not None:
            means = velocity_means
            # We don't know the sample backing of a supplied dict -> measure the
            # S-tier count separately so the confidence label is honest.
            _, counts = measured_velocity(arch_root)
        else:
            means, counts = measured_velocity(arch_root)

        s_samples = counts.get("S", 0)
        confidence = "MEASURED" if s_samples >= MEASURED_MIN_SAMPLES else "ESTIMATED"

        if total_count == 0:
            # No phase block table to read -> nothing to forecast.
            return Forecast(remaining, None, confidence, "unknown")
        if remaining == 0:
            return Forecast(0, 0.0, confidence, "phase complete")

        remaining_hours = remaining * _per_block_hours(means)
        est_days = math.ceil(remaining_hours / HOURS_PER_DAY)
        today = datetime.now(timezone.utc).date()
        completion = (today + timedelta(days=est_days)).isoformat()
        return Forecast(remaining, float(est_days), confidence, completion)
    except Exception:
        # Belt-and-braces: the forecast must never abort a session or a report.
        return Forecast(0, None, "ESTIMATED", "unknown")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phase_forecast",
        description="Forecast the current phase's completion date from velocity + open blocks.",
    )
    parser.add_argument(
        "--arch-root",
        metavar="PATH",
        default=".",
        help="Path to the cognitive-arch root directory (default: current directory).",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    force_utf8()
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()

    fc = forecast(arch_root)
    phase = project_state.current_phase_name(arch_root)

    print(f"Phase forecast for {phase}:")
    print(f"  Remaining blocks: {fc.remaining_blocks}")
    if fc.est_days is not None:
        print(f"  Estimated days:   {fc.est_days:g}")
    print(f"  Completion:       {fc.completion_estimate} [{fc.confidence}]")
    return 0  # forecaster is advisory: ALWAYS exit 0


if __name__ == "__main__":
    sys.exit(main())
