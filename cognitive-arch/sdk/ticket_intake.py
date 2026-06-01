# sdk/ticket_intake.py
# PURPOSE: Convert free-text ticket description into a corporate block manifest (kind: intake).
#          Output: manifests/block-<next_id>-<slug>.md with kind: ticket fields.
#          Saves Piloto from manually templating manifest fields.
# INPUTS:  --ticket <text>, --client <name>, --arch-root <path>
# OUTPUTS: manifests/block-<NNN>-<slug>.md (kind: ticket, size: XS)
# DEPS:    stdlib only
# USAGE:   python sdk/ticket_intake.py --ticket "implementar refresh de JWT" --client visagio --arch-root .
# SEE:     design/block-phase-redesign.md §1.7, templates/manifest-intake.md

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def _fix_utf8() -> None:
    import io as _io
    if sys.platform == "win32":
        if hasattr(sys.stdout, "buffer") and not (
            isinstance(sys.stdout, _io.TextIOWrapper) and sys.stdout.encoding.lower() == "utf-8"
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


_fix_utf8()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _next_block_id(arch_root: Path) -> int:
    """Return next available block number by reading BLOCK_LOG.md + manifests/."""
    seen: set[int] = set()
    log = arch_root / "blocks" / "BLOCK_LOG.md"
    if log.exists():
        for m in re.finditer(r"block-(\d+)", log.read_text(encoding="utf-8", errors="replace")):
            seen.add(int(m.group(1)))
    manifests_dir = arch_root / "manifests"
    if manifests_dir.exists():
        for mf in manifests_dir.glob("block-*.md"):
            m = re.match(r"block-(\d+)", mf.name)
            if m:
                seen.add(int(m.group(1)))
    return max(seen, default=0) + 1


def _slugify(text: str) -> str:
    """Convert text to a short kebab-case slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text[:40].rstrip("-")


def _infer_acceptance_criteria(ticket_text: str) -> list[str]:
    """Extract or infer acceptance criteria from ticket text."""
    criteria = []
    # Look for explicit acceptance criteria patterns
    for line in ticket_text.splitlines():
        line = line.strip()
        if re.match(r"^(?:ac\d*|acceptance|criteri[ao]|deve|deve[- ]|should|must)[\s:]+", line, re.IGNORECASE):
            criteria.append(line)
    if not criteria:
        # Generate a minimal criterion from the ticket text (first sentence)
        first_sentence = re.split(r"[.!?]", ticket_text.strip())[0].strip()
        criteria.append(f"{first_sentence} — conforme especificado no ticket  # NEEDS_REVIEW")
    return criteria


def _infer_phase_from_state(arch_root: Path) -> str:
    """Read current phase from STATE.md."""
    state = arch_root / "STATE.md"
    if not state.exists():
        return "phase-??"
    text = state.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\bphase:(phase-\d+)", text)
    return m.group(1) if m else "phase-??"


# ---------------------------------------------------------------------------
# Manifest generation
# ---------------------------------------------------------------------------

_MANIFEST_TEMPLATE = """\
---
id: block-{block_id}
size: XS
importance: normal
kind: intake
phase: {phase}
scope: phase-bound
status: pending
wip_stage: ~
paused_reason: ~
security: false
dependencies: []
# [corporate fields — required when kind is promoted to ticket]
ticket_id: {ticket_id}   # NEEDS_REVIEW — set actual ticket ID
acceptance_criteria:
{acceptance_criteria_yaml}
reviewer: ~   # NEEDS_REVIEW — set reviewer name
client_id: {client_id}
files:
  read:
    - governance/project-profile-{client_id}.md   # scan profile for context
  modify: []
  create: []   # intake never modifies client code
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-{block_id}-{slug}.md]
  - name: scope-clean
    type: fmod-check
created_at: {date}
---

# Block {block_id} — Intake: {title}

- **Size:** XS | **Importance:** normal
- **Kind:** intake (→ will become ticket block after Piloto review)
- **Client:** {client_id}
- **Status:** pending

## 1. Purpose

Ticket intake para: "{ticket_text}"

## 2. Acceptance Criteria (NEEDS_REVIEW)

{acceptance_criteria_md}

## 3. Next Step

Piloto revisa este manifest, preenche campos marcados com `# NEEDS_REVIEW`,
promove kind para `ticket`, e executa block-start.

## 4. Out of Scope

- Implementação de qualquer código de cliente neste bloco (intake = só leitura + geração de manifest)
"""


def generate_manifest(
    ticket_text: str,
    client_id: str,
    arch_root: Path,
) -> Path:
    """Generate a manifest file from a ticket description. Returns the created path."""
    block_num = _next_block_id(arch_root)
    slug = _slugify(ticket_text)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    phase = _infer_phase_from_state(arch_root)

    criteria = _infer_acceptance_criteria(ticket_text)
    criteria_yaml = "\n".join(f"  - \"{c}\"" for c in criteria)
    criteria_md = "\n".join(f"- {c}" for c in criteria)

    # Title: first 60 chars of ticket text
    title = ticket_text.strip()[:60]
    if len(ticket_text.strip()) > 60:
        title += "..."

    content = _MANIFEST_TEMPLATE.format(
        block_id=block_num,
        slug=slug,
        phase=phase,
        client_id=client_id,
        ticket_id=f"to-define-{block_num}",
        acceptance_criteria_yaml=criteria_yaml,
        acceptance_criteria_md=criteria_md,
        title=title,
        ticket_text=ticket_text.strip()[:120],
        date=date_str,
    )

    manifests_dir = arch_root / "manifests"
    manifests_dir.mkdir(exist_ok=True)
    out_path = manifests_dir / f"block-{block_num}-{slug}.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ticket_intake",
        description="Convert ticket text to a corporate block manifest (kind: intake → ticket).",
    )
    parser.add_argument("--ticket", required=True, help="Free-text ticket description")
    parser.add_argument("--client", required=True, help="Client/project name (e.g. visagio)")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()
    out = generate_manifest(args.ticket, args.client, arch_root)
    print(f"[ticket_intake] Created: {out.relative_to(arch_root)}")
    print(f"  Review and fill NEEDS_REVIEW fields, then promote kind: ticket → block-start")
    return 0


if __name__ == "__main__":
    sys.exit(main())
