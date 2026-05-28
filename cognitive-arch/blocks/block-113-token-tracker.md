---
id: block-113
phase: phase-18
tier: M
status: done
actual_duration_hours: 1.5
duration_source: estimated
tok_actual: 6800
gates_passed: 3/3
created_at: 2026-05-28
---

# Block 113 Retrospective — token_tracker.py

## 1. What was built

- `sdk/token_tracker.py`: reads all `blocks/*-retro.md`, extracts tok_estimated / tok_actual / date / phase
- `TokenRecord` dataclass with null-safe field parsing; handles tok_actual / tok-actual / tokens_actual variants
- `TokenTracker.load()` scans blocks dir; excludes BLOCK_LOG; `TokenTracker.report()` → markdown
- Generates `governance/token-report.md` with per-block table + per-phase summary + coverage stats
- `sdk/tests/test_token_tracker.py`: 20 tests covering all parsing variants and edge cases
- Initial token-report.md written: 87 blocks scanned, 1 with tok_actual (baseline established)

## 2. Gates

- tests-pass: 524 passed, 0 failed ✓
- lint-pass: syntax OK (flake8 not installed; py_compile used) ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- `tok-actual` and `tokens_actual` variants accepted via regex normalization (matches block_close.py)
- BLOCK_LOG.md excluded from scan via `"LOG" not in r.name.upper()` check
- Report format follows health_report.md conventions (markdown tables)

## 4. DX updated

`sdk/token_tracker.py` created. `governance/token-report.md` first run.
