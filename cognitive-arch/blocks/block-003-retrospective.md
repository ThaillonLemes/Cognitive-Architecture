---
id: block-003
status: done
tier: M
kind: refactor
opened_at: 2026-05-20
closed_at: 2026-05-20
duration_actual: <1h
---

# Block 003 — Retrospective

## What was built

Resolved naming inconsistency between "Comment Charter" and "Charter" across the architecture.

**Files modified (4):**
- `CLAUDE.md` line 24: "Comment Charter" → "Charter"
- `INDEX.md` line 10: "Comment Charter" → "Charter"
- `README.md` line 43: "Comment Charter" → "Charter"
- `phase-0/02-domain-overview.md`: vocab entry updated (reference to ADR-002); two resolved open questions closed with strikethrough

**Files created (1):**
- `decisions/ADR-002-charter-naming.md` — records decision, alternatives, consequences

## Gates result

| Gate | Result | Notes |
|------|--------|-------|
| no-comment-charter-remaining | PASS | 0 matches in canonical files; matches only in ADR/manifests/retrospectives/roadmap (expected) |
| files-updated (4 modify + 1 create) | PASS | All declared files changed |
| files-updated (STATE, NEXT, BLOCK_LOG) | PASS | Updated at block-close |

## Process notes

Third block under ADR-001. Tier M was correct — 4 files modified is above Tier S limit of 2. The extra files were discovered during Grep (README.md was not in the original plan from session 1 report). Manifest correctly listed README.md after the Grep confirmed it.

Bonus: closed two resolved open questions in `phase-0/02-domain-overview.md`:
- Charter naming → resolved by this block / ADR-002
- Axiom count → resolved by block-001

## Next recommended

`block-004` — Audit.sh ↔ audit-protocol parity check. `audit.sh` implements 5 checks; `commands/audit.md` declares 8. Either extend script OR clarify which are script vs Governor-only. Tier M.
