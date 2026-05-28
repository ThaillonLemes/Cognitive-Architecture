---
id: block-115
phase: phase-18
tier: M
status: done
actual_duration_hours: 1.0
duration_source: estimated
tok_actual: 5200
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 115 Retrospective — Dashboard Token Widget

## 1. What was built

- `_render_token_widget(records, budget)` added to sdk/dashboard_generator.py (pure function → testable in isolation)
- Widget renders: last 7 blocks bar chart (CSS-only, no JS), total tok_actual, avg/block, budget vs actual
- Graceful handling: `None` records → "not found" message; <3 blocks → "Insufficient data" message
- Budget color: green if within, red if overrun
- Integrated into `render_html()` before footer via `getattr(data, "token_records", None)` (backwards-compatible)
- `sdk/tests/test_dashboard_token_widget.py`: 11 tests covering all render paths

## 2. Gates

- tests-pass: 548 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Used `getattr(data, "token_records", None)` to read from DashboardData without modifying the dataclass schema (backwards-compatible)
- Pure HTML/CSS bar chart — no JS frameworks required per manifests's out-of-scope

## 4. DX updated

`sdk/dashboard_generator.py` — `_render_token_widget()` added, integrated into `render_html()`.
