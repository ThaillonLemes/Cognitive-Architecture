---
id: block-114
phase: phase-18
tier: S
status: done
actual_duration_hours: 0.5
duration_source: estimated
tok_actual: 2100
gates_passed: 1/1
created_at: 2026-05-28
---

# Block 114 Retrospective — token-budget.md + Axiom P-TOK-1

## 1. What was built

- `governance/token-budget.md`: per-phase token budgets table + overrun protocol + revision history
- Axiom **P-TOK-1** added to PROTOCOLS.md: "Track actual token cost on every block..."
- Budgets labeled "estimated" — Phase 18 token-report.md provides retroactive calibration baseline
- Overrun protocol defined: token_tracker detects → session_start warns → dashboard badge

## 2. Gates

- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- PROTOCOLS.md is `immutable` but manifest block-114 explicitly declares the modification as the governed override
- Budgets are advisory (warn-only) at phase level; hard only at block-close per block_close.py

## 4. DX updated

`PROTOCOLS.md` — P-TOK-1 added. `governance/token-budget.md` created.
