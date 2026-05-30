---
id: block-148
phase: phase-26
tier: M
status: done
actual_duration_hours: 0.7
duration_source: estimated
gates_passed: 2/2
created_at: 2026-05-30
---

# Block 148 Retrospective — Canonical health model + self-explaining top_drags

## 1. What was built

- `sdk/health_model.py`:
  - `Factor(key, cost, detail, fix)` — every point deduction carries a one-line fix.
  - `HealthScore(score, factors)` — `score == max(0, 100 - sum(costs))`; `top_drags(n=3)`
    returns the worst non-zero factors sorted desc.
  - `compute(arch_root)` — builds factors from real signals (audit errors/warnings via
    `audit.run_audit`, invariant criticals/warns via `invariant_check.run_all`, HOT-boot
    over-budget). Reuses existing checkers (no re-walk). Invariant import is defensive
    (missing/erroring → 0-cost factor, never crashes).
  - ASCII-safe CLI (`--arch-root`, `--top`).
- `sdk/tests/test_health_model.py` — 22 tests; load-bearing `score == 100 - sum(costs)`.

## 2. Weighting

| Factor | Unit | Source |
|--------|------|--------|
| audit.errors | 15/err | audit.run_audit |
| audit.warnings | 2/warn | audit.run_audit |
| invariant.critical | 15/crit | invariant_check |
| invariant.warn | 2/warn | invariant_check |
| hot.boot_over_budget | 10 one-shot | bytes/4 vs 4000 |

Audit units (15/2) mirror audit.py's historical formula so the familiar number maps on.

## 3. Gates

- tests-pass: 893 passed, 0 failed (22 new) ✓
- model-cli-clean: `python sdk/health_model.py --arch-root .` exits 0, prints score + drags ✓

## 4. Real-root finding (calibration → block-149)

The model honestly sums BOTH instruments → score floors at **0/100** (35 audit warns ×2
+ 29 invariant warns ×2 = 128 pts). The 29 invariant warns are the ACCEPTED historical
gaps already documented in `governance/known-drift.md` — dragging the score with accepted
drift is wrong. block-149 (reconciliation) must recalibrate so the unified score is
meaningful: exclude accepted/documented drift and/or cap per-category warning cost, while
keeping the `score == 100 - sum(costs)` invariant and making audit + health_report report
the SAME number.

## 5. Files actually touched

`sdk/health_model.py`, `sdk/tests/test_health_model.py` created.
