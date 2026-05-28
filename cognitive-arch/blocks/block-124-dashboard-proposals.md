---
id: block-124
phase: phase-20
tier: S
status: done
actual_duration_hours: 0.4
duration_source: estimated
tok_actual: 2800
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 124 Retrospective — Dashboard Proposals Widget

## 1. What was built

- `sdk/dashboard_generator.py`: `_render_proposals_widget(index_path)` — renders pending count badge + last 5 proposals table
- Integration into `render_html()` HTML template: `<!-- Proposals Widget -->` section between Token Widget and Footer
- Uses `getattr(data, "proposals_index_path", None)` for backwards-compatible data access
- Graceful fallback for `None` path, missing file, or empty table
- `sdk/tests/test_dashboard_proposals_widget.py`: 15 tests

## 2. Gates

- tests-pass: 606 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Last 5 rows from index.md shown (most recent activity, not oldest)
- Badge color orange when pending > 0, green when 0 — visible status at a glance
- `badge-warning` CSS class for pending rows; `badge-done` for accepted/rejected

## 4. DX updated

`sdk/dashboard_generator.py` has `_render_proposals_widget`. Template call at `render_html()` line 695.
