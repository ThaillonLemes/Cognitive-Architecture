---
id: phase-1
status: complete
version: v1.1
prev_phase: none
exit_criteria_count: 6
blocks_count: 6
estimated_duration_days: 3
created_at: 2026-05-20
last_updated: 2026-05-22
owner: implementer
---

# Phase 1 — Consistency (v1.1)

BRIEF: **Retroactive reconstruction** — this doc was written during Phase 6 from BLOCK_LOG.md and `phase-0/03-roadmap-draft.md`. Phase 1 fixed six internal inconsistencies discovered during the first full read-through of v1: axiom count, CLAUDE.md line budget, Charter naming, audit script parity, step-count references, and `_syntax.md` completeness.

## 1. Purpose

The initial v1 cognitive architecture (Phase 0) had several internal inconsistencies: files referenced different axiom counts, CLAUDE.md exceeded its own Q2 line budget, naming for the Comment Charter varied across files, `audit.sh` and `commands/audit.md` diverged on check counts, step counts in protocols were inconsistent, and `_syntax.md` was missing keys that appeared in examples. Phase 1 resolved all six categories of inconsistency in ≤ Tier S/M blocks, establishing a consistent v1.1 baseline for subsequent phases.

## 2. Goals

- PROTOCOLS.md axiom count consistent with all files that reference it
- CLAUDE.md within Q2 line budget (≤ 60 lines or refactored to slim entry)
- Charter naming unified (one canonical name used everywhere)
- `audit.sh` and `commands/audit.md` aligned (same check count or divergence documented)
- All numbered-step references (block-close, retrofit, bootstrap) have consistent counts across files
- `_syntax.md` alphabetical vocabulary includes all keys used in any example in the repo

## 3. Invariants

- No protocol or template files deleted — only corrected or supplemented
- `audit.sh` exit code 0 after every block close

## 4. Dependencies

- Phase 0 complete — all meta-project onboarding docs filled in `phase-0/`
- `PROJECT.md` status changed from `bootstrap` to `active`

## 7. Exit Criteria

1. `PROTOCOLS.md` BRIEF and body state the same axiom count (19)
2. `CLAUDE.md` line count ≤ 60 lines or trigger-phrase tables moved to sub-protocol
3. "Charter" naming is identical in `CLAUDE.md`, `INDEX.md`, and `PROTOCOLS.md`
4. `audit.sh` check count matches `commands/audit.md` declared checks, or difference is documented with rationale
5. Block-close (8 steps), retrofit flow, and bootstrap flow all reference consistent numbered-step counts in their respective protocol files
6. `_syntax.md` alphabetical list contains every key used in AI-only file examples across the repo

## 8. Block Index

| Block | Title | Status | Manifest |
|-------|-------|--------|----------|
| block-001 | Fix axiom-count inconsistency | done | `manifests/block-001-fix-axiom-count.md` |
| block-002 | Bring CLAUDE.md within Q2 budget | done | `manifests/block-002-claude-md-budget.md` |
| block-003 | Disambiguate Charter naming | done | `manifests/block-003-charter-naming.md` |
| block-004 | Audit.sh ↔ audit-protocol parity check | done | `manifests/block-004-audit-parity.md` |
| block-005 | Step-count audit pass | done | `manifests/block-005-step-count-audit.md` |
| block-006 | `_syntax.md` completeness sweep | done | `manifests/block-006-syntax-completeness.md` |

## 10. Out of Scope

- PowerShell port of `audit.sh` (deferred to Phase 2 or later)
- Token cost visibility (deferred to Phase 2)
- Formal frontmatter schema validation (deferred to Phase 3)
- Governor automation (deferred to Phases 4–5)

---

End of phase-1.md. (Retroactive reconstruction — Phase 6, block-041.)
