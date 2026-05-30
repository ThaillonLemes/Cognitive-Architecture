---
id: block-146
phase: phase-25
tier: M
status: done
actual_duration_hours: 0.7
duration_source: estimated
gates_passed: 3/3
created_at: 2026-05-30
---

# Block 146 Retrospective — Wire invariant gate into session_start + registry

## 1. What was wired

- `sdk/invariant_check.py`: `gate_result(arch_root) -> (ok, critical_violations)` —
  `ok = no criticals`. The single HALT authority for block-close. Pure, never raises
  (reuses `run_all`, which degrades a buggy invariant to warn → can't fabricate a HALT).
- `sdk/session_start.py`: `run_invariant_check` runner registered in `TOOL_RUNNERS`
  (id `invariant-check`, in-process import so INV4 sees live `TOOL_RUNNERS`); an
  `[INVARIANTS] N critical, M warn` summary line after `[PROPOSALS]`, wrapped in
  try/except. It SURFACES but never aborts — HALT is only in `gate_result()`.
- `governance/tools-registry.yaml`: `invariant-check` entry (1-day, time, high) next to
  `integrity-check`.
- `sdk/tests/test_invariant_gate.py` — 11 tests (gate HALTs on critical / clean on
  healthy; runner shape + registration; registry parses the new id; INV4 sees it).

## 2. Gates

- tests-pass: 850 passed, 0 failed (11 new) ✓
- session-surfaces-not-aborts: `session_start --force` exits 0, prints
  `[INVARIANTS] 7 critical, 29 warn [CRITICAL]`, runs `invariant-check`, no abort ✓
- immutable-untouched: `integrity_check --verify` 17/17 OK; `block-close-checklist.md`
  (immutable) byte-identical ✓

## 3. Design note

Critical separation: the session SURFACES drift every run (visibility), but the HALT
power lives only in `gate_result()` for block-close to consult. This avoids the
chicken-and-egg of a session that won't start because of pre-existing drift — while
still giving block-close a hard gate once block-147 clears the criticals.

## 4. Files actually touched

As manifest (sdk/invariant_check.py, sdk/session_start.py, governance/tools-registry.yaml
modified; sdk/tests/test_invariant_gate.py created).
