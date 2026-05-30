---
id: block-149
phase: phase-26
tier: M
status: done
actual_duration_hours: 1.0
duration_source: estimated
gates_passed: 4/4
created_at: 2026-05-30
---

# Block 149 Retrospective — Reconcile audit ↔ health_report onto one score

## 1. What was built

- Both divergent formulas DELETED (`audit: 100−e·15−w·2` → 30; `health_report:
  100−e·20−w·5` → 100). `audit.py` and `health_report.py` now derive their headline
  score from `health_model.compute(arch_root).score`.
- Recalibration in `health_model.compute` (keeps `score == max(0,100−sum(costs))`):
  1. **Accepted drift is free.** New `accepted_drift_blocks()` parses
     `governance/known-drift.md` (scoped to `## INV…` sections; handles ids, id-ranges,
     bare numeric ranges). Accepted blocks' warns move to 0-cost `*.accepted`
     transparency factors.
  2. **Per-category light-warn cap (30 pts)** so a pile of minor warns can't alone zero
     an otherwise-healthy root. Errors/criticals stay uncapped.
- `sdk/tests/test_health_consistency.py` (13 tests) + a 2-line mock-arity fix in
  test_health_model.py.

## 2. The key insight — double-counting

The accepted blocks 061-085 were counted TWICE — once as audit check-8 "drift" warns and
once as INV2 warns — and together sank the score to 0. Excluding accepted drift in BOTH
collectors fixed it. Honest, not gamed: real warns still count.

## 3. Gates

- tests-pass: 906 passed, 0 failed (13 new) ✓
- unified-score: `audit` == `health_report` == `health_model` == **80/100** on the real
  root (the 32-vs-100 contradiction is gone) ✓
- audit-pass: `audit.py` PASS, 0 errors, score 80 ✓
- no-recursion: `AuditResult.score()` lazily imports health_model; `_audit_factors` calls
  `run_audit(as_json=True)` to skip the summary → no circular import / infinite recursion ✓

## 4. Result

One honest, explainable health number: **80/100**, dragged only by 10 genuine audit warns
(NEXT over budget, broken pointers, a file-conflict claim) = 20 pts. Accepted historical
drift no longer lies about the project's health, and the two instruments can never diverge
again (same model input → same score).

## 5. Deviation (correct by design)

The generic scaffold scores 0/100 — it has 9 *critical* invariant violations (uncapped,
never excused). The cap protects only light warns; a real failure still tanks the score.

## 6. Files actually touched

`sdk/health_model.py`, `sdk/audit.py`, `sdk/health_report.py` modified;
`sdk/tests/test_health_consistency.py` created; `sdk/tests/test_health_model.py` mock fix.
