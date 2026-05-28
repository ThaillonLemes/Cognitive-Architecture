# Token Budget — Governance

BRIEF: Per-phase token budgets (advisory). Overrun triggers governance review per Axiom P-TOK-1. Baseline established from Phase 18 token-report.

---

## Policy

Token budgets are **advisory** — they warn, not block. The only hard enforcement point is at block-close (block_close.py checks tok_actual presence). Phase-level budget overruns surface in session_start.py and the dashboard token widget.

Axiom reference: **P-TOK-1** (see PROTOCOLS.md)

---

## Per-Phase Token Budgets

| Phase | Name | Block Count | Budget (tokens) | Basis |
|-------|------|-------------|-----------------|-------|
| phase-12 | Foundation Fix | 4 | 60,000 | estimated |
| phase-13 | Architecture Integrity | 4 | 60,000 | estimated |
| phase-14 | Retrospective Mining | 4 | 80,000 | estimated |
| phase-15 | Master Agent v1 | 5 | 100,000 | estimated |
| phase-16 | Visibility & Dashboard | 5 | 100,000 | estimated |
| phase-17 | Assertive Brainstorm v2 | 4 | 80,000 | estimated |
| phase-18 | Token Intelligence | 5 | 60,000 | estimated |
| phase-19 | Auto-ADR | 4 | 50,000 | estimated |
| phase-20 | Learning Loop | 5 | 70,000 | estimated |
| phase-21 | Governor Persistent | 4 | 60,000 | estimated |
| phase-22 | UX / Observability | 5 | 80,000 | estimated |

_Budget basis: "estimated" until token-report.md provides historical actuals. Phase 18 token-report.md will retroactively calibrate these figures._

---

## Overrun Protocol

1. `token_tracker.py` detects phase total tok_actual > budget
2. `session_start.py` emits `[WARN] Token budget overrun: phase-N (actual X > budget Y)`
3. Dashboard token widget shows red badge on overrun phases
4. Governance review: add block to next phase addressing the overrun source, or revise budget in this file

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-05-28 | Initial baselines established (Phase 18) | block-114 |

---

End of token-budget.md.
