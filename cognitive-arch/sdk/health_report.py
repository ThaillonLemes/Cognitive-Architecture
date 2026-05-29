# PURPOSE: Generate a composite project health report (audit, velocity, forecast, coverage, tracks)
# INPUTS:  arch-root directory, BLOCK_LOG.md, phases/, design/, tracks/PRIORITY.md
# OUTPUTS: governance/health-report-YYYY-MM-DD.md
# DEPS:    stdlib (pathlib, datetime, argparse, re, math, statistics) + project_state, safe_io
# SEE:     commands/health-report.md, sdk/project_state.py (single source of truth)

"""
Health Report Generator for cognitive-arch projects.

Usage:
  python sdk/health_report.py --arch-root .
  python sdk/health_report.py --arch-root . --dry-run
  python sdk/health_report.py --arch-root . --output-dir governance/
"""

import argparse
import math
import re
import sys
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from statistics import mean

# Ensure sibling modules importable when run as script
sys.path.insert(0, str(Path(__file__).resolve().parent))

import project_state
from safe_io import force_utf8
force_utf8()


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------

def _read(arch_root: Path, rel: str, default: str = "") -> str:
    """Read a file relative to arch_root. Returns default if not found."""
    p = arch_root / rel
    if not p.exists():
        return default
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return default


def _exists(arch_root: Path, rel: str) -> bool:
    return (arch_root / rel).exists()


# ---------------------------------------------------------------------------
# Section 1 — Audit Score
# ---------------------------------------------------------------------------

def _section_audit(arch_root: Path) -> str:
    """Compute audit score from audit.sh-style output or heuristic file checks."""
    errors = 0
    warnings = 0
    notes: list[str] = []

    # Check essential files exist
    essential = ["STATE.md", "NEXT.md", "PROTOCOLS.md", "INDEX.md", "blocks/BLOCK_LOG.md"]
    for f in essential:
        if not _exists(arch_root, f):
            errors += 1
            notes.append(f"ERROR: {f} missing")

    # Check for phases/ directory
    phases_dir = arch_root / "phases"
    if not phases_dir.exists():
        warnings += 1
        notes.append("WARN: phases/ directory missing")

    # Check for tracks/ directory
    if not _exists(arch_root, "tracks/PRIORITY.md"):
        warnings += 1
        notes.append("WARN: tracks/PRIORITY.md missing — no Tracks defined yet")

    # Check PROTOCOLS.md has S axioms (Phase 10)
    protocols = _read(arch_root, "PROTOCOLS.md")
    if "S1:" not in protocols:
        warnings += 1
        notes.append("WARN: Security axioms (S1-S5) missing from PROTOCOLS.md")

    score = max(0, 100 - (errors * 20) - (warnings * 5))

    if score >= 90:
        status = "HEALTHY"
    elif score >= 70:
        status = "DEGRADED"
    else:
        status = "CRITICAL"

    lines = [
        f"Score: {score}/100 — {status}",
        f"Errors: {errors} | Warnings: {warnings}",
    ]
    if notes:
        lines.append("")
        for note in notes:
            lines.append(f"- {note}")

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
    """Collect (tier, actual_duration_hours) pairs from retrospectives."""
    by_tier: dict[str, list[float]] = {"S": [], "M": [], "L": []}

    blocks_dir = arch_root / "blocks"
    if not blocks_dir.exists():
        return by_tier

    for block_id in done_ids:
        # Find retro file: blocks/block-NNN-*.md
        candidates = list(blocks_dir.glob(f"{block_id}-*.md"))
        if not candidates:
            # Also try just block_id.md
            candidates = list(blocks_dir.glob(f"{block_id}.md"))
        if not candidates:
            continue
        retro_file = candidates[0]
        try:
            content = retro_file.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = _parse_retro_frontmatter(content)
        tier = fm.get("tier", "").upper()
        if tier not in by_tier:
            continue
        try:
            duration = float(fm.get("actual_duration_hours", "0"))
        except (ValueError, TypeError):
            continue
        if duration > 0:
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
    by_tier = _collect_velocity_data(arch_root, done_ids)

    rows = []
    velocity_means = {}
    for tier in ("S", "M", "L"):
        data = by_tier[tier]
        count = len(data)
        confidence = _velocity_confidence(count)
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
        rows.append(f"| {tier}    | {count:5} | {m:8} | {mn:7} | {mx:7} | {conf_label} |")

    # Trend: compare last 5 vs previous 5 blocks with duration data
    all_durations = [d for tier in by_tier.values() for d in tier]
    trend = "INSUFFICIENT DATA"
    if len(all_durations) >= 10:
        prev5 = mean(all_durations[-10:-5])
        last5 = mean(all_durations[-5:])
        if last5 < prev5 * 0.9:
            trend = "IMPROVING (blocks completing faster)"
        elif last5 > prev5 * 1.1:
            trend = "DECLINING (blocks taking longer)"
        else:
            trend = "STABLE"

    table_header = (
        "| Tier | Count | Mean (h) | Min (h) | Max (h) | Confidence |\n"
        "|------|-------|----------|---------|---------|------------|\n"
    )
    section = table_header + "\n".join(rows) + f"\n\nTrend (last 5 vs previous 5): {trend}"
    return section, velocity_means


# ---------------------------------------------------------------------------
# Section 3 — Phase Progress + Forecast
# ---------------------------------------------------------------------------

def _section_phase_progress(arch_root: Path, velocity_means: dict) -> str:
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
    content = current_phase_file.read_text(encoding="utf-8") if current_phase_file.exists() else ""

    # Count done vs total blocks by looking for status in block index table
    done_count = len(re.findall(r"\|\s*done\s*\|", content, re.IGNORECASE))
    total_count = max(done_count, len(re.findall(r"\|\s*block-\d+", content, re.IGNORECASE)))

    if total_count == 0:
        # Try counting from phase file header
        remaining_match = re.search(r"(\d+)\s+blocks?", content, re.IGNORECASE)
        if remaining_match:
            total_count = int(remaining_match.group(1))

    pct = round(done_count / total_count * 100) if total_count > 0 else 0

    # Phase-forecast
    remaining_s = max(0, total_count - done_count)  # Simplified: treat unknowns as S
    remaining_hours = remaining_s * velocity_means.get("S", _VELOCITY_DEFAULTS["S"])
    est_days = math.ceil(remaining_hours / 4)
    est_completion = (date.today() + timedelta(days=est_days)).isoformat()

    # Confidence from velocity
    all_confident = all(v > _VELOCITY_DEFAULTS[t] * 0.5 for t, v in velocity_means.items())
    confidence = "MEDIUM" if all_confident else "LOW"

    lines = [
        f"Current phase: {phase_name}",
        f"Blocks complete: {done_count}/{total_count} ({pct}%)",
        f"Estimated completion: {est_completion} (Confidence: {confidence})",
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
        stagnation = int(row.get("stagnation_count", "0") or "0")
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
    tracks_section = _section_track_health(arch_root)

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
