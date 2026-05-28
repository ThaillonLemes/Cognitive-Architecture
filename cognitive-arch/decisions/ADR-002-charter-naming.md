---
id: ADR-002
title: Canonical name for C-axioms is "Charter" (not "Comment Charter")
status: accepted
created_at: 2026-05-20
decided_at: 2026-05-20
deciders: [user, AI]
context_phase: phase-1
context_block: block-003
---

# ADR-002 — Canonical name for C-axioms is "Charter"

## 1. Context

The C-axiom group (C1–C6, documentation rules) had two names in use:

- **"Charter"** — used in `PROTOCOLS.md` (source of truth): line 3 "19 axioms (P/Q/C) + Charter" and section header "## C — Charter (documentation rules)"
- **"Comment Charter"** — used in `CLAUDE.md`, `INDEX.md`, `README.md`, and `phase-0/02-domain-overview.md`

`PROTOCOLS.md` is the single source of truth for axiom definitions (P3). The discrepancy violates P3.

The "Comment" prefix likely originated from C1 (code header/comment rule) but does not accurately describe C2–C6, which cover speculation, BRIEF headers, AI-only format, ADRs, and retrospective style — not comments.

## 2. Decision

The canonical name is **"Charter"**. All references across `CLAUDE.md`, `INDEX.md`, `README.md`, and `phase-0/02-domain-overview.md` are updated to match `PROTOCOLS.md`.

## 3. Alternatives considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Keep "Comment Charter" everywhere | No renames | Violates P3; "Comment" misleads (C2–C6 are not comment rules) | Rejected |
| Rename PROTOCOLS.md to "Comment Charter" | Preserves old name | Changes the source of truth; wider impact | Rejected |
| **Use "Charter" everywhere** | Matches source of truth; accurate for C1–C6 | 4-file rename (minor) | ✓ Accepted |

## 4. Consequences

- **Positive:** single consistent name; PROTOCOLS.md is authoritative per P3.
- **Negative:** minor diff noise across 4 files.
- **Neutral:** "Comment Charter" never appeared in user-facing runtime — all uses were in AI-facing internal files.

## 5. References

- Source of truth: `PROTOCOLS.md` lines 3, 47
- Block manifest: `manifests/block-003-charter-naming.md`
