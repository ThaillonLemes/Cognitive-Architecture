---
id: block-155
phase: phase-27
tier: M
status: done
actual_duration_hours: 0.8
duration_source: estimated
gates_passed: 4/4
created_at: 2026-05-30
---

# Block 155 Retrospective — End-to-end demo (apply + forced rollback) + verify

## 1. What was built

- `sdk/tests/test_apply_e2e.py` (24 tests, no production change needed): drives the FULL
  pipeline (generate_diff → check_guards → apply_proposal) end-to-end on synthetic
  tmp_path arches with a REAL stub `sdk/tests` + `audit.py`, so the verification subprocess
  genuinely runs (not a re-test of 154).

## 2. The two paths, proven

- **APPLY** (synthetic, accepted non-immutable target): `applied=True` — backup created,
  reviewable section appended (frontmatter intact), proposal flipped to `applied`,
  governor-log `APPLY APPLIED` block, `ADR-006-apply-*` stub written.
- **ROLLBACK** (verification forced RED): `rolled_back=True`, `applied=False`, target
  restored **byte-identical**, proposal still `accepted`, no ADR.
- **Real-repo refusal:** both accepted proposals (immutable targets) → `allowed=False`;
  `apply(confirm=True)` leaves `templates/manifest-medium.md` byte-identical. Non-immutable
  target's immutability guard does NOT block (refused only for being rejected). 0 stray
  `_backups/`/`*.tmp` in the real repo.

## 3. Final Phase-27 verification

- `pytest sdk/tests/ -q` → **1042 passed, 0 failed**
- `audit.py` → PASS, 0 errors, **score 82/100**
- `integrity_check --verify` → all **17/17** immutable OK
- `invariant_check` → **0 critical**, 29 warn (accepted historical)

## 4. Effect — the loop is fully closed

The architecture now observes itself, mines patterns, recommends, proposes, AND can apply
an accepted proposal to its own non-immutable protocols — safely, atomically, with a full
test+audit gate and guaranteed rollback, never touching an immutable file without a human
bump. detect → propose → **apply (guarded, reversible)**. End-to-end, demonstrated.

## 5. Files actually touched

`sdk/tests/test_apply_e2e.py` created.
