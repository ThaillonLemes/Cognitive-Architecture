---
id: block-116
phase: phase-18
tier: M
status: done
actual_duration_hours: 1.0
duration_source: estimated
tok_actual: 4800
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 116 Retrospective — token_analyzer.py Signals

## 1. What was built

- `TokenSignal` dataclass added to `sdk/retro_signals.py` (block_id, tok_estimated, tok_actual, delta_pct, date)
- `extract_token_signals(arch_root)` — scans blocks, extracts tok_actual signals; skips blocks without tok_actual
- `detect_budget_overrun(token_signals, threshold_pct=20, d1_min=3)` added to `sdk/pattern_analyzer.py` as Rule R8
- Registered in `_RULES` list for automatic detection in analyze()
- `sdk/tests/test_token_signals.py`: 13 tests covering signal extraction + pattern detection

## 2. Gates

- tests-pass: 548 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Token signals use separate `TokenSignal` type; `extract_token_signals()` is separate from `extract_all()`
- `detect_budget_overrun` takes `list` (duck-typed) — works with real TokenSignal or SimpleNamespace in tests
- delta_pct is None when tok_estimated is missing (not zero, to avoid false overruns)

## 4. DX updated

`sdk/retro_signals.py` — `TokenSignal` dataclass + `extract_token_signals()`.
`sdk/pattern_analyzer.py` — `detect_budget_overrun()` + Rule R8 registered.
