# sdk/patterns_report.py
# PURPOSE: Render Pattern records to governance/patterns.md (markdown).
# INPUTS:  list[Pattern] from pattern_analyzer.analyze(), arch root
# OUTPUTS: governance/patterns.md (overwritten each run)
# DEPS:    stdlib only (pathlib, datetime), sdk/pattern_schema
# SEE:     sdk/pattern_analyzer.py, sdk/recommendation_engine.py, commands/pattern-mining.md

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pattern_schema import Pattern

OUTPUT_PATH = "governance/patterns.md"
SEVERITY_ORDER = {"critical": 0, "warn": 1, "info": 2}
SEVERITY_EMOJI = {"critical": "🔴", "warn": "🟡", "info": "🔵"}


def _severity_label(s: str) -> str:
    return f"{SEVERITY_EMOJI.get(s, '⚪')} {s.upper()}"


def render(patterns: list[Pattern], generated_at: Optional[str] = None) -> str:
    """Return the full markdown content for governance/patterns.md."""
    ts = generated_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    total = len(patterns)
    critical = sum(1 for p in patterns if p.severity == "critical")
    warn = sum(1 for p in patterns if p.severity == "warn")
    info = sum(1 for p in patterns if p.severity == "info")

    lines = [
        "# governance/patterns.md",
        "",
        f"BRIEF: Auto-generated pattern report. Re-run: `python sdk/patterns_report.py --arch-root .`",
        "",
        f"**Generated:** {ts}  ",
        f"**Total patterns:** {total} (🔴 critical: {critical} · 🟡 warn: {warn} · 🔵 info: {info})",
        "",
        "---",
        "",
    ]

    if not patterns:
        lines += [
            "## No patterns detected",
            "",
            "All detection rules returned below-threshold results. Architecture appears healthy.",
            "",
        ]
        lines.append("---\n\nEnd of patterns.md.")
        return "\n".join(lines)

    # Sort by severity then name
    sorted_patterns = sorted(patterns, key=lambda p: (SEVERITY_ORDER.get(p.severity, 9), p.name))

    # Top 5 summary table
    lines += [
        "## Summary (top patterns by severity)",
        "",
        "| Severity | Pattern | Occurrences | Last seen |",
        "|----------|---------|-------------|-----------|",
    ]
    for p in sorted_patterns[:5]:
        lines.append(
            f"| {_severity_label(p.severity)} | `{p.name}` | {p.occurrences} | {p.last_detected} |"
        )
    lines += ["", "---", ""]

    # Full detail section per pattern
    for p in sorted_patterns:
        lines += [
            f"## {_severity_label(p.severity)} — {p.name}",
            "",
            f"**Rule:** {p.rule_id}  ",
            f"**Description:** {p.description}  ",
            f"**First detected:** {p.first_detected}  ",
            f"**Last detected:** {p.last_detected}  ",
            f"**Occurrences:** {p.occurrences}",
            "",
            f"**Evidence blocks:** {', '.join(f'`{b}`' for b in p.evidence)}",
            "",
        ]
        if p.recommendation:
            lines += [
                f"**Recommendation:** {p.recommendation}",
                "",
            ]
        else:
            lines += [
                "_No recommendation yet. Run `sdk/recommendation_engine.py` to populate._",
                "",
            ]
        lines.append("---")
        lines.append("")

    lines.append("End of patterns.md.")
    return "\n".join(lines)


def write_report(patterns: list[Pattern], arch_root: Path) -> Path:
    """Write rendered patterns to governance/patterns.md and return the path."""
    out = arch_root / OUTPUT_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(patterns), encoding="utf-8")
    return out


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    from retro_signals import extract_all
    from pattern_analyzer import analyze

    arch_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent
    signals = extract_all(arch_root)
    patterns = analyze(signals)
    out = write_report(patterns, arch_root)
    print(f"Written {len(patterns)} patterns to {out.relative_to(arch_root)}")
