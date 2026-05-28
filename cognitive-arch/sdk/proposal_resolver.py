# PURPOSE: Accept or reject governance proposals by ID. Updates proposal file + index.md.
# INPUTS:  governance/proposals/<id>.md, governance/proposals/index.md, PROTOCOLS.md
# OUTPUTS: Updated status in proposal file + index; optional target_file patch
# DEPS:    stdlib only (pathlib, re, datetime, argparse, shutil)
# SEE:     sdk/protocol_updater.py, templates/proposal.md, phases/phase-20.md block-125

from __future__ import annotations

import argparse
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Front-matter helpers
# ---------------------------------------------------------------------------

def _update_frontmatter_field(text: str, field: str, value: str) -> str:
    """Replace or insert a YAML front-matter field."""
    pattern = rf"^({re.escape(field)}:).*$"
    new_text, n = re.subn(pattern, f"{field}: {value}", text, flags=re.MULTILINE)
    if n == 0:
        pos = text.rfind("\n---")
        if pos >= 0:
            new_text = text[:pos] + f"\n{field}: {value}" + text[pos:]
        else:
            new_text = text + f"\n{field}: {value}\n"
    return new_text


def _get_frontmatter_field(text: str, field: str) -> Optional[str]:
    """Return value of a YAML front-matter field, or None."""
    m = re.search(rf"^{re.escape(field)}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip().strip("\"'") if m else None


# ---------------------------------------------------------------------------
# Index helpers
# ---------------------------------------------------------------------------

def _update_index_status(index_path: Path, proposal_id: str, new_status: str) -> bool:
    """Update status column for proposal_id row in index.md. Returns True on match."""
    if not index_path.exists():
        return False
    text = index_path.read_text(encoding="utf-8", errors="replace")
    pattern = (
        rf"(\|\s*\S+\s*\|\s*\[{re.escape(proposal_id)}\][^|]*\|[^|]*\|[^|]*\|)"
        rf"\s*\S+\s*(\|)"
    )
    new_text, n = re.subn(pattern, rf"\g<1> {new_status} \g<2>", text)
    if n > 0:
        index_path.write_text(new_text, encoding="utf-8")
    return n > 0


# ---------------------------------------------------------------------------
# Immutability check
# ---------------------------------------------------------------------------

def _is_immutable(target_file: str, arch_root: Path) -> bool:
    """Return True if target_file is protected as immutable."""
    protocols_path = arch_root / "PROTOCOLS.md"
    if protocols_path.exists():
        ptext = protocols_path.read_text(encoding="utf-8", errors="replace")
        fname = Path(target_file).name
        if re.search(rf"immutable[^\n]*{re.escape(fname)}", ptext, re.IGNORECASE):
            return True
        if re.search(rf"{re.escape(fname)}[^\n]*immutable", ptext, re.IGNORECASE):
            return True
    candidate = arch_root / target_file
    if candidate.exists():
        header = candidate.read_text(encoding="utf-8", errors="replace")[:500]
        if re.search(r"protection:\s*immutable", header, re.IGNORECASE):
            return True
    return False


# ---------------------------------------------------------------------------
# Core resolver
# ---------------------------------------------------------------------------

class ProposalResolver:
    def __init__(self, arch_root: Path) -> None:
        self.arch_root = arch_root
        self.proposals_dir = arch_root / "governance" / "proposals"

    def _find_proposal(self, proposal_id: str) -> Optional[Path]:
        path = self.proposals_dir / f"{proposal_id}.md"
        return path if path.exists() else None

    def accept(self, proposal_id: str, apply: bool = False) -> tuple[bool, str]:
        """Accept a proposal. apply=True also patches target_file (with .bak)."""
        path = self._find_proposal(proposal_id)
        if path is None:
            return False, f"Proposal not found: {proposal_id}"

        text = path.read_text(encoding="utf-8", errors="replace")
        status = _get_frontmatter_field(text, "status")
        if status not in ("pending", None):
            return False, f"Proposal already {status} — cannot accept"

        today = date.today().isoformat()
        text = _update_frontmatter_field(text, "status", "accepted")
        text = _update_frontmatter_field(text, "resolved_at", today)
        text = _update_frontmatter_field(text, "resolved_by", "proposal_resolver")
        text = re.sub(r"\*\*Status:\*\* pending", "**Status:** accepted", text)
        path.write_text(text, encoding="utf-8")

        _update_index_status(self.proposals_dir / "index.md", proposal_id, "accepted")

        if not apply:
            return True, f"Accepted: {proposal_id}"

        target_file = _get_frontmatter_field(text, "target_file")
        if not target_file or "<target>" in target_file:
            return False, f"Cannot apply: target_file is a placeholder in {proposal_id}"

        if _is_immutable(target_file, self.arch_root):
            return False, f"Cannot apply: {target_file} is immutable — manual edit required"

        target_path = self.arch_root / target_file
        if not target_path.exists():
            return False, f"Cannot apply: {target_file} not found"

        bak_path = target_path.with_suffix(target_path.suffix + ".bak")
        shutil.copy2(str(target_path), str(bak_path))

        annotation = (
            f"\n<!-- Applied from proposal {proposal_id} on {today} "
            f"— review and update this section -->\n"
        )
        target_path.write_text(
            target_path.read_text(encoding="utf-8") + annotation, encoding="utf-8"
        )
        return True, f"Accepted: {proposal_id} | Applied to {target_file} (.bak created)"

    def reject(self, proposal_id: str, note: str = "") -> tuple[bool, str]:
        """Reject a proposal with an optional note."""
        path = self._find_proposal(proposal_id)
        if path is None:
            return False, f"Proposal not found: {proposal_id}"

        text = path.read_text(encoding="utf-8", errors="replace")
        status = _get_frontmatter_field(text, "status")
        if status not in ("pending", None):
            return False, f"Proposal already {status} — cannot reject"

        today = date.today().isoformat()
        text = _update_frontmatter_field(text, "status", "rejected")
        text = _update_frontmatter_field(text, "resolved_at", today)
        text = _update_frontmatter_field(text, "resolved_by", "proposal_resolver")
        text = re.sub(r"\*\*Status:\*\* pending", "**Status:** rejected", text)
        if note:
            text += f"\n## Resolution Note\n\n{note}\n"
        path.write_text(text, encoding="utf-8")

        _update_index_status(self.proposals_dir / "index.md", proposal_id, "rejected")

        return True, f"Rejected: {proposal_id}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Accept or reject governance proposals")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--accept", metavar="ID", help="Accept a proposal by ID")
    group.add_argument("--reject", metavar="ID", help="Reject a proposal by ID")
    parser.add_argument("--apply", action="store_true", help="(--accept only) Patch the target_file")
    parser.add_argument("--note", default="", help="(--reject only) Rejection reason")
    args = parser.parse_args(argv)

    root = Path(args.arch_root).resolve()
    resolver = ProposalResolver(root)

    if args.accept:
        ok, msg = resolver.accept(args.accept, apply=args.apply)
    else:
        ok, msg = resolver.reject(args.reject, note=args.note)

    print(f"[proposal_resolver] {'OK' if ok else 'ERROR'} — {msg}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
