# PURPOSE: Generate a composite project health report (audit, velocity, forecast, coverage, tracks)
# INPUTS:  arch-root directory, BLOCK_LOG.md, phases/, design/, tracks/PRIORITY.md
# OUTPUTS: governance/health-report-YYYY-MM-DD.md
# DEPS:    stdlib (pathlib, datetime, argparse, re, math, statistics) + project_state, safe_io,
#          health_model (the ONE canonical score — block-149; same number audit.py reports)
# SEE:     commands/health-report.md, sdk/project_state.py (single source of truth),
#          sdk/health_model.py, manifests/block-149-reconcile-health.md

"""
Health Report Generator for cognitive-arch projects.

Usage:
  python sdk/health_report.py --arch-root .
  python sdk/health_report.py --arch-root . --dry-run
  python sdk/health_report.py --arch-root . --output-dir governance/
"""

import argparse
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import mean

# Ensure sibling modules importable when run as script
sys.path.insert(0, str(Path(__file__).resolve().parent))

import health_model
import phase_forecast
import project_state
import velocity_inference
from safe_io import force_utf8
force_utf8()


# ---------------------------------------------------------------------------
# Section 1 — Audit Score
# ---------------------------------------------------------------------------

def _section_audit(arch_root: Path) -> str:
    """Render the audit score section from the ONE canonical health_model (block-149).

    This used to run its own `100 - errors*20 - warnings*5` formula — a SECOND,
    divergent scorer that produced a different number from sdk/audit.py's
    `100 - e*15 - w*2`. That contradiction is dead: both instruments now read
    `health_model.compute(arch_root).score`, so the report's headline score is
    identical to a fresh `python sdk/audit.py` run, by construction.

    The model's `top_drags(3)` (each with its point cost and a one-line fix)
    becomes the explanatory notes — Phase 26 Exit Criterion 2 surfaces drags here.

    Defensive: if the model can't run for any reason, fall back to a clearly-labelled
    UNKNOWN line rather than crash the whole report.
    """
    try:
        health = health_model.compute(arch_root)
    except Exception as exc:  # the report must never die on the score section
        return (
            "Score: UNKNOWN — health_model.compute failed\n"
            f"- ERROR: {exc}\n"
            "- run: python sdk/health_model.py --arch-root . to diagnose"
        )

    score = health.score
    try:
        import health_model as _hm
        status = _hm.label_for(score)
    except Exception:
        status = "HEALTHY" if score >= 90 else "DEGRADED" if score >= 70 else "CRITICAL"

    drags = health.top_drags(3)
    lines = [
        f"Score: {score}/100 — {status}",
        f"Source: sdk/health_model.py (canonical; same score as `python sdk/audit.py`)",
    ]
    if drags:
        lines.append("")
        lines.append(f"Top drags (worst {len(drags)}):")
        for f in drags:
            lines.append(f"- -{f.cost} [{f.key}] {f.detail} — fix: {f.fix}")
    else:
        lines.append("")
        lines.append("- No factor is costing points (100/100).")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section 2 — Velocity
# ---------------------------------------------------------------------------

def _parse_block_log(arch_root: Path) -> list[str]:
    """Return list of done block IDs — delegates to the single source of truth.

    Kept as a thin wrapper so existing call sites (velocity, the report header)
    all count blocks the same way project_state does (deduped, first-seen order).
    """
    return project_state.completed_block_ids(arch_root)


def _parse_retro_frontmatter(content: str) -> dict:
    """Extract key:value pairs from YAML frontmatter."""
    result = {}
    in_fm = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "---":
            if not in_fm:
                in_fm = True
                continue
            else:
                break
        if in_fm and ":" in stripped:
            key, _, val = stripped.partition(":")
            result[key.strip()] = val.strip().strip("\"'#").strip()
    return result


def _collect_velocity_data(arch_root: Path, done_ids: list[str]) -> dict:
    """Collect (tier, actual_duration_hours) pairs from retrospectives.

    Tier source priority: retro frontmatter `tier:` → manifest `tier:` fallback.
    The 26 retros for blocks 086-111 carry `actual_duration_hours` but omit
    the `tier:` field; without the fallback they're silently dropped and the
    velocity table reports ~half the samples it should.
    """
    by_tier: dict[str, list[float]] = {"S": [], "M": [], "L": []}

    blocks_dir = arch_root / "blocks"
    if not blocks_dir.exists():
        return by_tier

    for block_id in done_ids:
        # Find retro file: blocks/block-NNN-*.md
        candidates = list(blocks_dir.glob(f"{block_id}-*.md"))
        if not candidates:
            candidates = list(blocks_dir.glob(f"{block_id}.md"))
        if not candidates:
            continue
        retro_file = candidates[0]
        try:
            content = retro_file.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = _parse_retro_frontmatter(content)
        try:
            duration = float(fm.get("actual_duration_hours", "0"))
        except (ValueError, TypeError):
            continue
        if duration <= 0:
            continue
        tier = fm.get("tier", "").upper()
        if tier not in by_tier:
            manifest_path = velocity_inference._locate_manifest(block_id, arch_root)
            if manifest_path is None:
                continue
            tier = velocity_inference._tier_from_manifest(manifest_path)
            if tier not in by_tier:
                continue
        by_tier[tier].append(duration)

    return by_tier


_VELOCITY_DEFAULTS = {"S": 1.0, "M": 3.5, "L": 9.0}


def _velocity_confidence(count: int) -> str:
    if count >= 10:
        return "HIGH"
    if count >= 3:
        return "MEDIUM"
    return "INSUFFICIENT DATA"


def _section_velocity(arch_root: Path, done_ids: list[str]) -> tuple[str, dict]:
    """Build velocity section. Returns (markdown, velocity_means dict)."""
    # Collect per-tier data AND a chronological list (BLOCK_LOG order) in one pass.
    by_tier: dict[str, list[float]] = {"S": [], "M": [], "L": []}
    # Build durations in BLOCK_LOG order (chronological) for trend computation,
    # rather than grouping by tier (which puts all S then M then L, not time-ordered).
    all_durations_chron: list[float] = []

    blocks_dir = arch_root / "blocks"
    if blocks_dir.exists():
        for block_id in done_ids:
            candidates = list(blocks_dir.glob(f"{block_id}-*.md"))
            if not candidates:
                candidates = list(blocks_dir.glob(f"{block_id}.md"))
            if not candidates:
                continue
            retro_file = candidates[0]
            try:
                content = retro_file.read_text(encoding="utf-8")
            except OSError:
                continue
            fm = _parse_retro_frontmatter(content)
            try:
                duration = float(fm.get("actual_duration_hours", "0"))
            except (ValueError, TypeError):
                continue
            if duration <= 0:
                continue
            tier = fm.get("tier", "").upper()
            if tier not in by_tier:
                manifest_path = velocity_inference._locate_manifest(block_id, arch_root)
                if manifest_path is None:
                    continue
                tier = velocity_inference._tier_from_manifest(manifest_path)
                if tier not in by_tier:
                    continue
            by_tier[tier].append(duration)
            all_durations_chron.append(duration)

    rows = []
    velocity_means = {}
    for tier in ("S", "M", "L"):
        data = by_tier[tier]
        count = len(data)
        confidence = _velocity_confidence(count)
        if count >= 3:
            source = "MEASURED"
        else:
            source = "ESTIMATED"
        if count > 0:
            m = round(mean(data), 1)
            mn = round(min(data), 1)
            mx = round(max(data), 1)
            velocity_means[tier] = m
        else:
            m = _VELOCITY_DEFAULTS[tier]
            mn = mx = m
            velocity_means[tier] = _VELOCITY_DEFAULTS[tier]
        conf_label = confidence if count >= 3 else f"INSUFFICIENT DATA — {count} block(s)"
        rows.append(
            f"| {tier}    | {count:5} | {m:8} | {mn:7} | {mx:7} | {conf_label} | {source} |"
        )

    # Trend: compare last 5 vs previous 5 blocks in chronological (BLOCK_LOG) order.
    trend = "INSUFFICIENT DATA"
    if len(all_durations_chron) >= 10:
        prev5 = mean(all_durations_chron[-10:-5])
        last5 = mean(all_durations_chron[-5:])
        if last5 < prev5 * 0.9:
            trend = "IMPROVING (blocks completing faster)"
        elif last5 > prev5 * 1.1:
            trend = "DECLINING (blocks taking longer)"
        else:
            trend = "STABLE"

    table_header = (
        "| Tier | Count | Mean (h) | Min (h) | Max (h) | Confidence | Source |\n"
        "|------|-------|----------|---------|---------|------------|--------|\n"
    )
    section = table_header + "\n".join(rows) + f"\n\nTrend (last 5 vs previous 5): {trend}"
    return section, velocity_means


# ---------------------------------------------------------------------------
# Section 3 — Phase Progress + Forecast
# ---------------------------------------------------------------------------

def _section_phase_progress(arch_root: Path, velocity_means: dict) -> str:
    """Render the Phase Progress + Forecast section.

    The forecast math (remaining blocks x per-block velocity -> est_days -> dated
    completion) used to live inline here; it now lives ONCE in
    sdk/phase_forecast.forecast() so session_start and this report share a single
    definition. We pass the velocity_means the velocity table already computed so
    the report's two views can never drift, and read the block counts via the same
    shared helper the forecaster uses.
    """
    phases_dir = arch_root / "phases"
    if not phases_dir.exists():
        return "No phases/ directory found."

    # Find current phase via project_state (canonical). The old logic,
    # `sorted(glob("phase-[0-9]*.md"))[-1]`, sorted lexically (phase-9 landed
    # after phase-22) and also matched phase-N-retro.md.
    current_phase_file = project_state.current_phase_file(arch_root)
    if current_phase_file is None:
        return "No phase files found in phases/."

    phase_name = current_phase_file.stem

    # Block counts + forecast come from phase_forecast (the single source).
    done_count, total_count = phase_forecast.phase_block_counts(arch_root)
    pct = round(done_count / total_count * 100) if total_count > 0 else 0

    fc = phase_forecast.forecast(arch_root, velocity_means=velocity_means)
    est_completion = fc.completion_estimate

    lines = [
        f"Current phase: {phase_name}",
        f"Blocks complete: {done_count}/{total_count} ({pct}%)",
        f"Estimated completion: {est_completion} (Confidence: {fc.confidence})",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section 4 — Design Coverage
# ---------------------------------------------------------------------------

def _section_design_coverage(arch_root: Path) -> str:
    design_dir = arch_root / "design"
    if not design_dir.exists():
        return "No design/ directory found."

    design_files = [f for f in design_dir.glob("*.md") if f.is_file()]
    total = len(design_files)
    if total == 0:
        return "No design documents found in design/."

    # Search phases/ and manifests/ for references to each design file stem
    search_content = ""
    for search_dir in ["phases", "manifests"]:
        d = arch_root / search_dir
        if d.exists():
            for f in d.rglob("*.md"):
                try:
                    search_content += f.read_text(encoding="utf-8")
                except OSError:
                    pass

    covered = []
    gaps = []
    for df in design_files:
        stem = df.stem
        if stem in search_content or df.name in search_content:
            covered.append(stem)
        else:
            gaps.append(stem)

    cov_pct = round(len(covered) / total * 100) if total > 0 else 0

    lines = [
        f"Design concepts: {total}",
        f"Covered by phases/manifests: {len(covered)} ({cov_pct}%)",
    ]
    if gaps:
        lines.append("\nGaps:")
        for g in gaps[:10]:  # Limit to first 10
            lines.append(f"- {g}")
        if len(gaps) > 10:
            lines.append(f"- ... and {len(gaps) - 10} more")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section 5 — Track Health
# ---------------------------------------------------------------------------

def _safe_int(value, default=0):
    """Parse value as int, returning default on any error."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _section_track_health(arch_root: Path) -> str:
    priority_path = arch_root / "tracks" / "PRIORITY.md"
    if not priority_path.exists():
        return "No tracks/PRIORITY.md found. Create Tracks via protocols/track-generation.md."

    content = priority_path.read_text(encoding="utf-8")

    # Parse table rows
    rows = []
    in_table = False
    headers: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        if not headers:
            headers = [h.lower().replace(" ", "_") for h in cells]
            in_table = True
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if len(cells) < len(headers):
            continue
        row = dict(zip(headers, cells[:len(headers)]))
        tid = row.get("track_id", "")
        if not tid or tid.startswith("_") or "no tracks" in tid.lower():
            continue
        rows.append(row)

    if not rows:
        return "No Tracks defined yet. Create Tracks using protocols/track-generation.md."

    today_str = date.today().isoformat()
    header = "| Track | Priority | Last Improvement | Status |\n|-------|----------|-----------------|--------|\n"
    table_rows = []
    for row in rows:
        tid = row.get("track_id", "?")
        priority = row.get("total_priority", "?")
        last_imp = row.get("last_improved_at", "—")
        # Check stagnation
        stagnation = _safe_int(row.get("stagnation_count", "0"))
        if stagnation >= 9:
            status = "⚠️ STAGNANT — escalate"
        elif stagnation >= 3:
            status = "⚠️ STUCK — brainstorm needed"
        else:
            status = "OK"
        table_rows.append(f"| {tid} | {priority} | {last_imp} | {status} |")

    return header + "\n".join(table_rows)


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def generate_report(arch_root: Path) -> str:
    today = date.today().isoformat()
    done_ids = _parse_block_log(arch_root)

    audit_section = _section_audit(arch_root)
    velocity_section, velocity_means = _section_velocity(arch_root, done_ids)
    progress_section = _section_phase_progress(arch_root, velocity_means)
    coverage_section = _section_design_coverage(arch_root)
    try:
        tracks_section = _section_track_health(arch_root)
    except Exception as exc:
        tracks_section = f"Error generating track health: {exc}"

    report = f"""# Project Health Report — {today}

Generated by: sdk/health_report.py
Architecture root: {arch_root.resolve()}
Blocks completed: {len(done_ids)}

---

## 1. Audit Score

{audit_section}

---

## 2. Velocity

{velocity_section}

---

## 3. Phase Progress

{progress_section}

---

## 4. Design Coverage

{coverage_section}

---

## 5. Track Health

{tracks_section}

---

*Report generated {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")}. Re-run to refresh.*
"""
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="health_report",
        description="Generate a composite project health report for a cognitive-arch project.",
    )
    parser.add_argument(
        "--arch-root",
        metavar="PATH",
        default=".",
        help="Path to the cognitive-arch root directory (default: current directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs are readable and output is writable. No file written.",
    )
    parser.add_argument(
        "--output-dir",
        metavar="PATH",
        default="governance",
        help="Directory to write the health report to (default: governance/).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    arch_root = Path(args.arch_root).resolve()
    output_dir = arch_root / args.output_dir

    # Validate arch_root exists
    if not arch_root.exists():
        print(f"ERROR: arch-root not found: {arch_root}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        # Validate essential readable files
        missing = []
        for f in ["blocks/BLOCK_LOG.md", "PROTOCOLS.md"]:
            if not (arch_root / f).exists():
                missing.append(f)
        if missing:
            print(f"WARNING: dry-run — some files missing: {', '.join(missing)}")
        # Validate output dir writable (or creatable)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(f"ERROR: cannot create output dir {output_dir}: {exc}", file=sys.stderr)
            sys.exit(1)
        print("Health report dry-run passed.")
        sys.exit(0)

    # Generate and write report
    report = generate_report(arch_root)
    today = date.today().isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"health-report-{today}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Health report written to: {out_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
