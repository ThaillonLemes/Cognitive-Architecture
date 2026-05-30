---
id: block-143
phase: phase-24
tier: S
kind: gate
status: pending
files:
  read:
    - sdk/audit.py
    - sdk/tests/test_cli_smoke.py
  create:
    - sdk/tests/test_boot_budget.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: budget-test-asserts-under-4000
    type: command
    command: python -m pytest sdk/tests/test_boot_budget.py -q
    expect: 'passes; asserts HOT boot total < 4000 tok using the same chars/4 sum as audit.print_token_estimates'
  - name: full-audit-pass
    type: command
    command: python sdk/audit.py --arch-root .
    expect: 'Result: PASS; Errors: 0; HOT boot total line shows < 4000 tok and NOT "OVER BUDGET"'
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-143-budget-gate.md]
created_at: 2026-05-30
---

# Block 143 — Boot-budget regression gate + verification

- **Tier:** S
- **Kind:** gate
- **Status:** pending
- **Parallel-with:** none (depends on 140–142 landed)

## 1. Purpose

Blocks 140–142 cut the HOT boot under 4000 tok, but nothing stops a future edit from
silently growing it back. This block adds a regression test that computes the HOT
boot total the SAME way as `sdk/audit.py::print_token_estimates` (sum of `chars/4`
over the HOT file list, then `//4` of the byte total) and asserts it stays < 4000,
then runs the final full audit to confirm PASS with 0 errors and no `OVER BUDGET`.

## 2. Dependencies

block-140 (INDEX split), block-141 (STATE dedup), block-142 (`_syntax` reclassified
out of the audit HOT list). All must be `done` — the budget only fits once they land.

## 3. Files

- **Read:** `sdk/audit.py` (mirror `print_token_estimates`: the exact HOT file list
  and the `len(read_bytes()) // 4` / sum-then-`//4` arithmetic — the test must match
  it, not invent its own), `sdk/tests/test_cli_smoke.py` (reuse its `_ARCH` root
  resolution and `audit.py` real-run pattern for the audit-PASS assertion).
- **Create:** `sdk/tests/test_boot_budget.py` (one test asserts HOT boot total < 4000
  tok computed like `print_token_estimates`; a second asserts `python sdk/audit.py
  --arch-root .` exits 0 and its output contains neither `OVER BUDGET` nor any
  `ERROR:` line).

## 4. Validation

- `python -m pytest sdk/tests/test_boot_budget.py -q` → passes; the asserted total is
  < 4000 with the ≥200-tok headroom the phase targets.
- The test imports the HOT list from `audit` (or asserts it equals
  `audit.print_token_estimates`'s list) so it can't silently diverge from the audit's
  own measurement.
- `python sdk/audit.py --arch-root .` → `Result: PASS`, `Errors: 0`, HOT boot total
  line shows `< 4000 tok` and the `OK` tag (not `[!] OVER BUDGET`).
- Full suite `python -m pytest sdk/tests/ -q` → 0 failed (≥789 tests).

## 5. Gates

Declared in frontmatter: tests-pass, budget-test-asserts-under-4000, full-audit-pass,
files-updated. `budget-test-asserts-under-4000` is the permanent regression guard;
`full-audit-pass` is the phase's integration exit check (0 errors, not OVER BUDGET).

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Test hard-codes a HOT list that drifts from audit's | Med | Import the list/threshold from `sdk.audit` (don't duplicate it), or assert equality against `print_token_estimates`'s list so the two stay coupled. |
| 4000 is met with near-zero headroom → flaky red | Low | Phase targets ≥200-tok headroom; if margin is thin, the failure correctly signals a needed trim, not a flake. |
| Test measures chars differently (encoding) than audit | Low | Use `read_bytes()` exactly as `print_token_estimates` does; assert on the same integer arithmetic. |

## 7. Out of Scope

- Changing the 4000-tok budget value (the goal is to fit it, not move it).
- Further content trimming beyond what 140–142 already achieved.
- Asserting per-file budgets (covered by audit check 2); this gate is the boot TOTAL.
- Wiring the test into CI config (it lives in `sdk/tests/`, run by the existing suite).

## 8. New Abstraction

None. `test_boot_budget.py` reuses `audit.print_token_estimates`'s list/arithmetic and
the `test_cli_smoke.py` run pattern. No new code abstraction.
