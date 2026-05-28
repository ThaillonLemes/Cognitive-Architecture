---
id: block-104
manifest: manifests/block-104-weekly-report.md
status: done
gates_passed: 4/4
completed_at: 2026-05-27T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 1
duration_source: estimated
tok_estimated: ~1600
tok_src: estimated
---

# Block 104 Retrospective — Weekly report HTML

## 1. What was built

- Created `sdk/weekly_report.py`: `WeeklyReport` dataclass; `generate_weekly_report()` reads BLOCK_LOG/STATE/NEXT/patterns/scheduler (all injectable); `render_html()` standalone dark HTML; `write_report()` writes to `governance/reports/weekly-YYYY-MM-DD.html`; CLI (`--stdout`, `--days`).
- Created `sdk/tests/test_weekly_report.py`: 21 tests covering helpers, generator, HTML renderer, file writer.
- Created `templates/weekly-report.html`: annotated HTML template showing the design structure.
- Updated `INDEX.md`.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| test_blocks_in_period_correct | unit | pass |
| test_blocks_in_period_inclusive_range | unit | pass |
| test_extract_pattern_names | unit | pass |
| test_velocity_calculation | unit | pass |
| test_velocity_zero_days | unit | pass |
| test_forecast_calculation | unit | pass |
| test_forecast_none_velocity | unit | pass |
| test_generate_returns_weekly_report | unit | pass |
| test_generate_period_dates | unit | pass |
| test_generate_blocks_closed_count | unit | pass |
| test_generate_velocity_positive | unit | pass |
| test_generate_current_phase | unit | pass |
| test_generate_next_action_from_next_md | unit | pass |
| test_generate_stale_tools_counted | unit | pass |
| test_generate_forecast_positive | unit | pass |
| test_render_html_is_standalone | unit | pass |
| test_render_html_no_cdn | unit | pass |
| test_render_html_contains_dates | unit | pass |
| test_render_html_contains_next_action | unit | pass |
| test_write_report_creates_file | unit | pass |
| test_write_report_in_correct_dir | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| weekly-report-module | ✓ | `sdk/weekly_report.py` + `templates/weekly-report.html` created |
| tests-pass | ✓ | 21/21 tests pass |
| dependencies-met | ✓ | block-095 + block-100 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, this retrospective updated |

## 4. Decisions made

- `gates_pass_rate` set to `None` in v1 (requires parsing retro files — deferred to dashboard block-105 which has more time budget).
- `_blocks_in_period` uses inclusive string comparison (YYYY-MM-DD lexicographic) — correct without date parsing.
- All content injectable for testing; no filesystem reads in tests.
- `write_report` creates `governance/reports/` with `mkdir(parents=True, exist_ok=True)` — handles missing directory.

## 5. Token estimate

```
tok_estimated: ~1600  tok_src:estimated
```

## 6. Issues / surprises

None.

## 7. Files actually touched

- Created: `sdk/weekly_report.py`, `sdk/tests/test_weekly_report.py`, `templates/weekly-report.html`
- Modified: `INDEX.md`, `STATE.md`, `NEXT.md`, `blocks/BLOCK_LOG.md`, `board.md`
- As manifest otherwise.

---

End of retrospective.
