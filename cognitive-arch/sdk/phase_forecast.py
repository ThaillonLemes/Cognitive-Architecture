# PURPOSE: Forecast remaining time in the current phase from velocity + open blocks.
# INPUTS:  arch-root, phases/phase-*.md, blocks/BLOCK_LOG.md, blocks/*.md retros
# OUTPUTS: governance/phase-forecast-YYYY-MM-DD.md
# DEPS:    stdlib only (argparse, datetime, math, re, pathlib, statistics)
# SEE:     commands/phase-forecast.md, sdk/health_report.py (_section_phase_progress)

"""
Phase Forecast for cognitive-arch projects.

Estimates remaining time in the current (highest-numbered) phase based on
historical block velocity and the count of open blocks in that phase. The
estimate is velocity-based and refreshes on every run.

Usage:
  python sdk/phase_forecast.py --arch-root .
  python sdk/phase_forecast.py --arch-root . --dry-run
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from statistics import mean

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252-safe output

_VELOCITY_DEFAULTS = {"S": 1.0, "M": 3.5, "L": 9.0}
WORK_HOURS_PER_DAY = 4


def _read(arch_root: Path, rel: str, default: str = "") -> str:
    p = arch_root / rel
    if not p.exists():
        return default
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return default


def _parse_block_log(arch_root: Path) -> list[str]:
    """Return done block IDs from BLOCK_LOG.md ('<id> done ...' lines)."""
    done = []
    for line in _read(arch_root, "blocks/BLOCK_LOG.md").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "done":
            done.append(parts[0])
    return done


def _parse_frontmatter(content: str) -> dict:
    result: dict = {}
    in_fm = False
    for line in content.splitlines():
        s = line.strip()
        if s == "---":
            if not in_fm:
                in_fm = True
                continue
            break
        if in_fm and ":" in s:
            k, _, v = s.partition(":")
            result[k.strip()] = v.strip().strip("\"'#").strip()
    return result


def _velocity_by_tier(arch_root: Path, done_ids: list[str]) -> dict:
    """Mean actual_duration_hours per tier from done-block retros (+ sample size)."""
    by_tier: dict[str, list[float]] = {"S": [], "M": [], "L": []}
    blocks_dir = arch_root / "blocks"
    if blocks_dir.exists():
        for bid in done_ids:
            cands = list(blocks_dir.glob(f"{bid}-*.md")) or list(blocks_dir.glob(f"{bid}.md"))
            if not cands:
                continue
            try:
                fm = _parse_frontmatter(cands[0].read_text(encoding="utf-8"))
            except OSError:
                continue
            tier = fm.get("tier", "").upper()
            if tier not in by_tier:
                continue
            try:
                dur = float(fm.get("actual_duration_hours", "0"))
            except (ValueError, TypeError):
                continue
            if dur > 0:
                by_tier[tier].append(dur)
    means = {t: (round(mean(by_tier[t]), 2) if by_tier[t] else _VELOCITY_DEFAULTS[t])
             for t in ("S", "M", "L")}
    return {"means": means, "sample": sum(len(v) for v in by_tier.values())}


def _current_phase(arch_root: Path):
    phases_dir = arch_root / "phases"
    if not phases_dir.exists():
        return None, ""
    files = sorted(
        phases_dir.glob("phase-[0-9]*.md"),
        key=lambda p: int(re.search(r"phase-(\d+)", p.stem).group(1)),
    )
    if not files:
        return None, ""
    f = files[-1]
    try:
        return f.stem, f.read_text(encoding="utf-8")
    except OSError:
        return f.stem, ""


def _block_counts(phase_content: str):
    done = len(re.findall(r"\|\s*done\s*\|", phase_content, re.IGNORECASE))
    refs = len(re.findall(r"block-\d+", phase_content, re.IGNORECASE))
    total = max(done, refs)
    if total == 0:
        m = re.search(r"(\d+)\s+blocks?", phase_content, re.IGNORECASE)
        if m:
            total = int(m.group(1))
    return done, total


def forecast(arch_root: Path) -> str:
    today = date.today().isoformat()
    done_ids = _parse_block_log(arch_root)
    vel = _velocity_by_tier(arch_root, done_ids)
    means = vel["means"]
    phase_name, phase_content = _current_phase(arch_root)

    if phase_name is None:
        body = "No phases/ directory or phase files found — cannot forecast."
    else:
        done, total = _block_counts(phase_content)
        remaining = max(0, total - done)
        pct = round(done / total * 100) if total else 0
        # Unknown-tier remaining blocks are costed at the median (M) velocity.
        remaining_hours = remaining * means["M"]
        est_days = math.ceil(remaining_hours / WORK_HOURS_PER_DAY) if remaining_hours else 0
        eta = (date.today() + timedelta(days=est_days)).isoformat() if remaining else today
        if vel["sample"] >= 10:
            confidence = "HIGH"
        elif vel["sample"] >= 3:
            confidence = "MEDIUM"
        else:
            confidence = "LOW (insufficient velocity data — using tier defaults)"
        body = (
            f"- Current phase: **{phase_name}**\n"
            f"- Blocks complete: {done}/{total} ({pct}%)\n"
            f"- Remaining blocks: {remaining}\n"
            f"- Velocity mean h/block: S={means['S']} M={means['M']} L={means['L']} "
            f"(sample={vel['sample']})\n"
            f"- Est. remaining effort: {remaining_hours:.1f}h "
            f"(~{est_days} working day(s) @ {WORK_HOURS_PER_DAY}h/day)\n"
            f"- **Estimated completion: {eta}** (confidence: {confidence})"
        )

    return f"""# Phase Forecast — {today}

Generated by: sdk/phase_forecast.py
Architecture root: {arch_root.resolve()}

{body}

*Velocity-based estimate; refreshes each run. "Unknown" remaining blocks are
costed at the median (M) tier velocity. Generated {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")}.*
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="phase_forecast",
        description="Forecast remaining time in the current phase from velocity + open blocks.",
    )
    p.add_argument("--arch-root", metavar="PATH", default=".",
                   help="Path to the cognitive-arch root (default: current directory).")
    p.add_argument("--dry-run", action="store_true",
                   help="Validate inputs are readable and output is writable. No file written.")
    p.add_argument("--output-dir", metavar="PATH", default="governance",
                   help="Directory to write the forecast to (default: governance/).")
    return p


def main() -> None:
    args = build_parser().parse_args()
    arch_root = Path(args.arch_root).resolve()
    if not arch_root.exists():
        print(f"ERROR: arch-root not found: {arch_root}", file=sys.stderr)
        sys.exit(1)
    out_dir = arch_root / args.output_dir
    if args.dry_run:
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(f"ERROR: cannot create output dir {out_dir}: {exc}", file=sys.stderr)
            sys.exit(1)
        print("Phase forecast dry-run passed.")
        sys.exit(0)
    report = forecast(arch_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"phase-forecast-{date.today().isoformat()}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Phase forecast written to: {out_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
