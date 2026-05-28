# PURPOSE: Generate governance proposals from patterns that exceed threshold (D1 ≥ 3)
# INPUTS:  governance/patterns.md, governance/proposals/index.md (for dedup check)
# OUTPUTS: governance/proposals/<date>-<pattern-id>.md, updated index.md
# DEPS:    stdlib only (pathlib, re, datetime, argparse)
# SEE:     phases/phase-20.md block-122, templates/proposal.md, sdk/pattern_analyzer.py

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


# Minimum signal count to trigger a proposal
PROPOSAL_THRESHOLD = 3


# ---------------------------------------------------------------------------
# Pattern reader (parses governance/patterns.md)
# ---------------------------------------------------------------------------

def _parse_patterns_md(text: str) -> list[dict[str, Any]]:
    """Parse governance/patterns.md and return list of pattern dicts.

    Each dict: {name, severity, description, occurrences, evidence, rule_id}
    """
    patterns: list[dict[str, Any]] = []

    # Split on pattern sections: "## <emoji> <SEVERITY> — <name>"
    sections = re.split(r"^## ", text, flags=re.MULTILINE)
    for section in sections[1:]:  # skip header
        lines = section.strip().splitlines()
        if not lines:
            continue

        # Header line: "🟡 WARN — scope-expansion-recurring"
        header = lines[0]
        name_m = re.search(r"—\s+(.+)$", header)
        if not name_m:
            continue
        name = name_m.group(1).strip().strip("`")

        severity = "warn"
        if "CRITICAL" in header.upper():
            severity = "critical"
        elif "INFO" in header.upper():
            severity = "info"

        body = "\n".join(lines[1:])

        desc_m = re.search(r"\*\*Description:\*\*\s*(.+)", body)
        description = desc_m.group(1).strip() if desc_m else ""

        occ_m = re.search(r"\*\*Occurrences:\*\*\s*(\d+)", body)
        occurrences = int(occ_m.group(1)) if occ_m else 0

        rule_m = re.search(r"\*\*Rule:\*\*\s*(R\d+)", body)
        rule_id = rule_m.group(1) if rule_m else "unknown"

        ev_m = re.search(r"\*\*Evidence blocks:\*\*\s*(.+)", body)
        evidence = []
        if ev_m:
            evidence = re.findall(r"block-\d+", ev_m.group(1))

        patterns.append({
            "name": name,
            "severity": severity,
            "description": description,
            "occurrences": occurrences,
            "rule_id": rule_id,
            "evidence": evidence,
        })

    return patterns


# ---------------------------------------------------------------------------
# Proposal helpers
# ---------------------------------------------------------------------------

def _make_proposal_id(pattern_id: str, date_str: str) -> str:
    """Deterministic proposal ID: date-pattern-slug."""
    slug = re.sub(r"[^\w-]", "-", pattern_id.lower()).strip("-")
    return f"{date_str}-{slug}"


def _already_proposed(proposals_dir: Path, pattern_id: str) -> bool:
    """Return True if a proposal for this pattern_id already exists (any date)."""
    slug = re.sub(r"[^\w-]", "-", pattern_id.lower()).strip("-")
    return bool(list(proposals_dir.glob(f"*-{slug}.md")))


def _render_proposal(pattern: dict, proposal_id: str, date_str: str) -> str:
    evidence_list = "\n".join(
        f"- `{b}`" for b in pattern.get("evidence", [])
    ) or "- _(no specific blocks identified)_"

    name = pattern["name"]
    description = pattern["description"]
    occurrences = pattern["occurrences"]
    severity = pattern["severity"]
    rule_id = pattern["rule_id"]

    # Suggest a target file based on pattern type heuristic
    if "axiom" in name.lower():
        target_file = "PROTOCOLS.md"
    elif "duration" in name.lower() or "velocity" in name.lower():
        target_file = "protocols/block-complexity-estimator.md"
    elif "gate" in name.lower():
        target_file = "protocols/block-close-checklist.md"
    elif "scope" in name.lower():
        target_file = "templates/manifest-medium.md"
    elif "token" in name.lower() or "budget" in name.lower():
        target_file = "governance/token-budget.md"
    else:
        target_file = "protocols/<target>.md"

    return f"""---
id: {proposal_id}
status: pending
pattern_id: {name}
target_file: {target_file}
proposed_change: |
  [AI suggestion] Review and update {target_file} to address the recurring pattern '{name}'.
  Pattern detected {occurrences} times. See evidence blocks below.
  Specific change: human should review the pattern and propose a concrete protocol amendment.
rationale: |
  Pattern '{name}' ({severity.upper()}, Rule {rule_id}) has been detected {occurrences} time(s),
  exceeding the governance threshold of {PROPOSAL_THRESHOLD}.
  Description: {description}
created_at: {date_str}
resolved_at: ~
resolved_by: ~
signal_count_d1: {occurrences}
---

# Proposal — {name}

## 1. Pattern

**Pattern ID:** `{name}`
**Signal count (D1):** {occurrences}
**Severity:** {severity}
**Rule:** {rule_id}

## 2. Proposed change

> Target file: `{target_file}`

Review and update `{target_file}` to address the recurring pattern. The AI has identified
this pattern is above threshold. A human should propose the specific protocol text change.

## 3. Rationale

{description}

This pattern has occurred {occurrences} times, which exceeds the governance threshold ({PROPOSAL_THRESHOLD}).
A protocol update may reduce future recurrence.

## 4. Evidence

Blocks affected:
{evidence_list}

## 5. Resolution

**Status:** pending

_Human: set status to `accepted` or `rejected`, fill `resolved_at` and `resolved_by`._

_To apply: `python sdk/proposal_resolver.py --accept {proposal_id} [--apply]`_
"""


def _update_proposals_index(proposals_dir: Path, proposal_id: str, pattern_id: str, target_file: str, date_str: str) -> None:
    """Append entry to governance/proposals/index.md."""
    index_path = proposals_dir / "index.md"
    if not index_path.exists():
        index_path.write_text(
            "# Proposals Index — Governance\n\n"
            "| Date | ID | Pattern | Target File | Status |\n"
            "|------|----|---------|-------------|--------|\n",
            encoding="utf-8",
        )
    rel = f"governance/proposals/{proposal_id}.md"
    entry = f"| {date_str} | [{proposal_id}]({rel}) | {pattern_id} | {target_file} | pending |\n"
    with open(index_path, "a", encoding="utf-8") as f:
        f.write(entry)


# ---------------------------------------------------------------------------
# Core updater
# ---------------------------------------------------------------------------

class ProtocolUpdater:
    def __init__(self, arch_root: Path) -> None:
        self.arch_root = arch_root
        self.proposals_dir = arch_root / "governance" / "proposals"

    def run(self, dry_run: bool = False, threshold: int = PROPOSAL_THRESHOLD) -> list[Path]:
        """Scan patterns.md, generate proposals for qualifying patterns. Returns created paths."""
        patterns_path = self.arch_root / "governance" / "patterns.md"
        if not patterns_path.exists():
            print("[protocol_updater] governance/patterns.md not found — run pattern_analyzer first")
            return []

        text = patterns_path.read_text(encoding="utf-8", errors="replace")
        patterns = _parse_patterns_md(text)

        qualifying = [p for p in patterns if p["occurrences"] >= threshold]

        if not qualifying:
            print(f"[protocol_updater] No patterns above threshold ({threshold}). No proposals generated.")
            return []

        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        date_str = date.today().isoformat()
        created: list[Path] = []

        for pattern in qualifying:
            pattern_id = pattern["name"]

            if _already_proposed(self.proposals_dir, pattern_id):
                print(f"  [skip] Proposal already exists for: {pattern_id}")
                continue

            proposal_id = _make_proposal_id(pattern_id, date_str)

            if dry_run:
                print(f"  [dry-run] Would create: governance/proposals/{proposal_id}.md")
                continue

            target_file = (
                "PROTOCOLS.md" if "axiom" in pattern_id.lower() else
                "protocols/<target>.md"
            )
            content = _render_proposal(pattern, proposal_id, date_str)
            out_path = self.proposals_dir / f"{proposal_id}.md"
            out_path.write_text(content, encoding="utf-8")
            _update_proposals_index(self.proposals_dir, proposal_id, pattern_id, target_file, date_str)
            created.append(out_path)
            print(f"  [created] governance/proposals/{proposal_id}.md")

        return created


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate governance proposals from patterns")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created; do not write files")
    parser.add_argument("--threshold", type=int, default=PROPOSAL_THRESHOLD,
                        help=f"Minimum signal_count_d1 to trigger proposal (default: {PROPOSAL_THRESHOLD})")
    args = parser.parse_args(argv)

    root = Path(args.arch_root).resolve()
    updater = ProtocolUpdater(root)

    created = updater.run(dry_run=args.dry_run, threshold=args.threshold)
    if not args.dry_run:
        print(f"[protocol_updater] Done. {len(created)} proposal(s) created.")


if __name__ == "__main__":
    main()
