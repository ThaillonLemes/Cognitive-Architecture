---
id: block-143
phase: phase-24
tier: S
status: done
actual_duration_hours: 0.3
duration_source: estimated
gates_passed: 4/4
created_at: 2026-05-30
---

# Block 143 Retrospective — Boot-budget regression gate + verification

## 1. What was built

- New `sdk/tests/test_boot_budget.py` (4 tests):
  - `test_hot_boot_under_budget` — HOT boot < 4000 tok, computed exactly like
    `audit.print_token_estimates` (`sum(len(read_bytes())) // 4` over the 6 HOT files).
  - `test_hot_boot_keeps_headroom` — ≥200 tok headroom under the budget.
  - `test_list_matches_audit_measurement` — coupling guard: the test's HOT list equals
    audit's, and `_syntax.md` stays out (can't silently diverge).
  - `test_audit_run_not_over_budget` — runs `audit.py` and asserts no `OVER BUDGET`.

## 2. Gates

- tests-pass: 797 passed, 0 failed (was 793 + 4 new) ✓
- budget-test-asserts-under-4000: `test_boot_budget.py` 4/4 pass ✓
- full-audit-pass: Result PASS, Errors 0, HOT boot ~3763 tok (OK, not OVER BUDGET) ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md, this retro ✓

## 3. Effect — Phase 24 locked in

The diet is now permanent: any future edit that pushes the HOT boot back over 4000 (or
below 200-tok headroom) fails the suite. The boot tax stays ~3763 tok — a ~48% cut from
the ~7260 it was at the start of the phase.

## 4. Files actually touched

As manifest (sdk/tests/test_boot_budget.py created).
