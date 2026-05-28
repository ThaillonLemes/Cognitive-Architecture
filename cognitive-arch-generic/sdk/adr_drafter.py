# PURPOSE: Generate ADR scaffold files from brainstorm synthesis decisions
# INPUTS:  synthesis JSON (dict with decisions list), arch-root directory
# OUTPUTS: design/adrs/YYYY-MM-DD-<slug>.md per significant decision; governance/adrs/index.md updated
# DEPS:    stdlib only (pathlib, re, json, datetime, argparse)
# SEE:     phases/phase-19.md block-117, templates/ADR-auto.md, sdk/brainstorm_synthesis.py

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Synthesis decision schema
# ---------------------------------------------------------------------------
# Expected synthesis JSON structure (one decision entry):
# {
#   "title": "Use FastAPI for REST layer",
#   "significance": "high",          # "high" | "medium" | "low"
#   "recommended_option": "FastAPI",
#   "options_considered": ["FastAPI", "Flask", "Django"],
#   "confidence_band": "high",       # "high" | "medium" | "low"
#   "context": "Chosen during phase-X brainstorm",
#   "synthesis_source": "design/api-design.md"
# }
#
# Significance "high" or "medium" → auto-generate ADR draft.
# "low" or absent → skip.

_SIGNIFICANT = {"high", "medium"}


# ---------------------------------------------------------------------------
# Slug helper
# ---------------------------------------------------------------------------

def _make_slug(title: str) -> str:
    """Convert decision title to a filesystem-safe kebab-case slug (max 50 chars)."""
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return slug[:50]


def _unique_path(base_dir: Path, date_str: str, slug: str) -> Path:
    """Return a path that doesn't yet exist; appends -1, -2 etc. as needed."""
    candidate = base_dir / f"{date_str}-{slug}.md"
    if not candidate.exists():
        return candidate
    counter = 1
    while True:
        candidate = base_dir / f"{date_str}-{slug}-{counter}.md"
        if not candidate.exists():
            return candidate
        counter += 1


# ---------------------------------------------------------------------------
# ADR template render
# ---------------------------------------------------------------------------

def _render_adr(decision: dict[str, Any], date_str: str) -> str:
    title = decision.get("title", "Untitled Decision")
    sig = decision.get("significance", "medium")
    source = decision.get("synthesis_source", "unknown")
    recommended = decision.get("recommended_option", "_see context_")
    confidence = decision.get("confidence_band", "medium")
    options = decision.get("options_considered", [])
    context = decision.get("context", "_extracted from brainstorm synthesis_")
    phase = decision.get("context_phase", "")
    block = decision.get("context_block", "")

    options_table = "\n".join(
        f"| {opt} | synthesis | {'AI recommendation ✓' if opt == recommended else '—'} |"
        for opt in options
    ) if options else f"| {recommended} | synthesis | AI recommendation ✓ |"

    phase_line = f"context_phase: {phase}" if phase else ""
    block_line = f"context_block: {block}" if block else ""

    return f"""---
id: ADR-auto-{_make_slug(title)}
title: {title}
status: draft
created_at: {date_str}
synthesis_source: {source}
significance: {sig}
confidence_band: {confidence}
recommended_option: {recommended}
{phase_line}
{block_line}
auto_generated: true
---

# ADR-auto — {title}

## 1. Context

{context}

_Synthesis source: `{source}`_

## 2. Decision

> **AI Recommended:** `{recommended}` (confidence: `{confidence}`)
>
> _[HUMAN REQUIRED] Replace this with the final accepted decision._

## 3. Alternatives considered

| Option | Source | Notes |
|--------|--------|-------|
{options_table}

## 4. Consequences

- **Positive:** _[HUMAN REQUIRED — fill before accepting]_
- **Negative:** _[HUMAN REQUIRED — fill before accepting]_
- **Neutral / Trade-off:** _[HUMAN REQUIRED — fill before accepting]_

## 5. Rationale

_[HUMAN REQUIRED — explain why `{recommended}` was chosen over alternatives]_

## 6. References

- Synthesis source: `{source}`
- ADR index: `governance/adrs/index.md`
- Template: `templates/ADR-auto.md`

---

End of auto-generated ADR draft. Change `status: draft` → `status: accepted` when rationale is filled.
"""


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

def _update_adr_index(arch_root: Path, adr_path: Path, title: str, date_str: str) -> None:
    """Append entry to governance/adrs/index.md (append-only)."""
    index_dir = arch_root / "governance" / "adrs"
    index_dir.mkdir(parents=True, exist_ok=True)
    index_path = index_dir / "index.md"

    rel_path = adr_path.relative_to(arch_root).as_posix()
    entry = f"| {date_str} | [{title}]({rel_path}) | draft |\n"

    if not index_path.exists():
        index_path.write_text(
            "# ADR Index — Auto-generated\n\n"
            "| Date | Title | Status |\n"
            "|------|-------|--------|\n"
            + entry,
            encoding="utf-8",
        )
    else:
        with open(index_path, "a", encoding="utf-8") as f:
            f.write(entry)


def _rebuild_index(arch_root: Path) -> int:
    """Rebuild governance/adrs/index.md from all ADR files in design/adrs/. Returns count."""
    adrs_dir = arch_root / "design" / "adrs"
    if not adrs_dir.exists():
        return 0

    index_dir = arch_root / "governance" / "adrs"
    index_dir.mkdir(parents=True, exist_ok=True)
    index_path = index_dir / "index.md"

    lines = [
        "# ADR Index — Auto-generated\n\n",
        "| Date | Title | Status |\n",
        "|------|-------|--------|\n",
    ]
    count = 0
    for adr_file in sorted(adrs_dir.glob("*.md")):
        text = adr_file.read_text(encoding="utf-8", errors="replace")
        title_m = re.search(r"^title:\s*(.+)", text, re.MULTILINE)
        status_m = re.search(r"^status:\s*(\S+)", text, re.MULTILINE)
        date_m = re.search(r"^created_at:\s*(\S+)", text, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else adr_file.stem
        status = status_m.group(1).strip() if status_m else "unknown"
        date_str = date_m.group(1).strip() if date_m else ""
        rel = adr_file.relative_to(arch_root).as_posix()
        lines.append(f"| {date_str} | [{title}]({rel}) | {status} |\n")
        count += 1

    index_path.write_text("".join(lines), encoding="utf-8")
    return count


# ---------------------------------------------------------------------------
# Core generator
# ---------------------------------------------------------------------------

class AdrDrafter:
    def __init__(self, arch_root: Path) -> None:
        self.arch_root = arch_root
        self.adrs_dir = arch_root / "design" / "adrs"

    def generate(self, synthesis_data: dict[str, Any] | list[dict[str, Any]]) -> list[Path]:
        """Generate ADR drafts from synthesis data.

        synthesis_data: either a list of decision dicts, or a dict with a "decisions" key.
        Returns list of created file paths.
        """
        decisions: list[dict[str, Any]]
        if isinstance(synthesis_data, list):
            decisions = synthesis_data
        elif isinstance(synthesis_data, dict):
            decisions = synthesis_data.get("decisions", [])
        else:
            return []

        self.adrs_dir.mkdir(parents=True, exist_ok=True)
        date_str = date.today().isoformat()
        created: list[Path] = []

        for decision in decisions:
            sig = decision.get("significance", "low")
            if sig not in _SIGNIFICANT:
                continue

            title = decision.get("title", "Untitled")
            slug = _make_slug(title)
            out_path = _unique_path(self.adrs_dir, date_str, slug)
            content = _render_adr(decision, date_str)
            out_path.write_text(content, encoding="utf-8")
            _update_adr_index(self.arch_root, out_path, title, date_str)
            created.append(out_path)

        return created

    def generate_from_file(self, synthesis_path: Path) -> list[Path]:
        """Load synthesis JSON from file and generate ADRs."""
        data = json.loads(synthesis_path.read_text(encoding="utf-8"))
        return self.generate(data)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate ADR scaffolds from brainstorm synthesis")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--synthesis", help="Path to synthesis JSON file")
    parser.add_argument("--rebuild-index", action="store_true", help="Rebuild governance/adrs/index.md from design/adrs/")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing")
    args = parser.parse_args(argv)

    root = Path(args.arch_root).resolve()
    drafter = AdrDrafter(root)

    if args.rebuild_index:
        count = _rebuild_index(root)
        print(f"[adr_drafter] Index rebuilt: {count} ADRs indexed at governance/adrs/index.md")
        return

    if not args.synthesis:
        print("[adr_drafter] --synthesis <path> required (or --rebuild-index)")
        sys.exit(1)

    synth_path = Path(args.synthesis)
    data = json.loads(synth_path.read_text(encoding="utf-8"))

    decisions: list[dict] = data if isinstance(data, list) else data.get("decisions", [])
    significant = [d for d in decisions if d.get("significance") in _SIGNIFICANT]

    if args.dry_run:
        print(f"[adr_drafter] dry-run: {len(significant)} significant decisions found")
        for d in significant:
            slug = _make_slug(d.get("title", "untitled"))
            print(f"  would create: design/adrs/{date.today().isoformat()}-{slug}.md")
        return

    created = drafter.generate_from_file(synth_path)
    print(f"[adr_drafter] Created {len(created)} ADR draft(s):")
    for p in created:
        print(f"  {p.relative_to(root)}")


if __name__ == "__main__":
    main()
