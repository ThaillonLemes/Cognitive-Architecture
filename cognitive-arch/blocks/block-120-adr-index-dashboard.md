---
id: block-120
phase: phase-19
tier: M
status: done
actual_duration_hours: 0.75
duration_source: estimated
tok_actual: 3800
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 120 Retrospective — ADR Index + Dashboard Widget

## 1. What was built

- `_render_adr_widget(index_path)` added to sdk/dashboard_generator.py
- Widget shows: total ADRs, last ADR date, status badges (draft/accepted/rejected counts)
- Gracefully handles: None path → "not found"; empty index → "No ADRs"; populated → full widget
- Integrated into `render_html()` before token widget (backwards-compatible via getattr)
- `governance/adrs/index.md` generated via `_rebuild_index()` (0 ADRs in current project — no design/adrs/*.md yet)
- `sdk/tests/test_adr_index.py`: 11 tests covering index management + widget render paths

## 2. Gates

- tests-pass: 576 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Widget reads `getattr(data, "adr_index_path", None)` — backwards-compatible, no DashboardData schema change
- `_render_adr_widget` is pure function (injectable path, testable in isolation)

## 4. DX updated

`sdk/dashboard_generator.py` — `_render_adr_widget()` added and integrated.
`governance/adrs/index.md` created (initial empty index).
