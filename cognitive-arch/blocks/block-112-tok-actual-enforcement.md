---
id: block-112
phase: phase-18
tier: S
status: done
actual_duration_hours: 0.5
duration_source: estimated
tok_actual: 3200
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 112 Retrospective — tok_actual Enforcement

## 1. What was built

- Added `_check_tok_actual(arch_root, block_id, force)` to `sdk/block_close.py`
- Accepts `tok_actual`, `tok-actual`, `tokens_actual` field variants (regex normalization)
- Returns `(False, msg)` when field absent or null/empty; `(True, '')` when present
- Integrated into `close_block()` after retro/hours checks: halts with WARN unless `--force`
- Created `sdk/tests/test_block_close.py` with 11 tests covering all variants and edge cases

## 2. Gates

- tests-pass: 504 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Historical retros without tok_actual return `(True, "no_retro")` — no false halt
- Force flag bypasses halt but still logs `tok_actual_check: missing` in results dict

## 4. DX updated

`sdk/block_close.py` — new `_check_tok_actual()` function and integration in `close_block()`.
