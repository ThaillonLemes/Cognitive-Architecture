---
id: block-105
manifest: manifests/block-105-dashboard.md
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

# Block 105 Retrospective — Live dashboard HTML

## 1. What was built

- Created `templates/_styles.css`: shared CSS design system (dark theme #0f0f1a). CSS variables (--bg-card, --purple, --gold, --teal, --green, --red, --orange, --grey, --text-dim, --code-bg). Classes: `.card` + color variants, `.badge` + state variants, `table/th/td`, `.phase-row/.phase-pill`, `.dash-grid` (4-col auto-fit grid), `.timeline`, `.alert`.
- Created `sdk/dashboard_generator.py`: `AgentRow` and `DashboardData` dataclasses; `_parse_board()`, `_blocks_in_window()`, `_timeline_entries()`, `_extract_recent_patterns()`, `_build_roadmap()`, `_velocity()`, `_forecast()` helpers; `generate_dashboard()` (all content injectable); `render_html()` (standalone dark HTML, no CDN); `write_dashboard()` (reads `_styles.css`, writes `governance/dashboard.html`); CLI with `--arch-root` / `--stdout`.
- Created `sdk/tests/test_dashboard.py`: 44 tests.
- Created `templates/dashboard.html`: annotated template with placeholder comments.
- Generated `governance/dashboard.html`: live initial output (Phase 16, last block-107, 4-col layout, timeline, roadmap Phases 1–16 done / 16 active / 17 planned, quick-commands footer).

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| test_parse_board_returns_agent_rows | unit | pass |
| test_parse_board_correct_agent_id | unit | pass |
| test_parse_board_correct_block | unit | pass |
| test_parse_board_correct_status | unit | pass |
| test_parse_board_last_done_field | unit | pass |
| test_parse_board_ignores_comments | unit | pass |
| test_parse_board_empty_content | unit | pass |
| test_parse_board_ignores_non_agent_lines | unit | pass |
| test_blocks_in_window_within_range | unit | pass |
| test_blocks_in_window_includes_cutoff_date | unit | pass |
| test_blocks_in_window_excludes_older_blocks | unit | pass |
| test_blocks_in_window_empty_log | unit | pass |
| test_timeline_entries_newest_first | unit | pass |
| test_timeline_entries_empty_log | unit | pass |
| test_timeline_entries_format | unit | pass |
| test_extract_patterns_returns_names | unit | pass |
| test_extract_patterns_excludes_summary_table | unit | pass |
| test_extract_patterns_max_count | unit | pass |
| test_extract_patterns_empty_content | unit | pass |
| test_build_roadmap_active_phase_correct | unit | pass |
| test_build_roadmap_done_phases | unit | pass |
| test_build_roadmap_planned_phases | unit | pass |
| test_build_roadmap_phase_1_no_done | unit | pass |
| test_build_roadmap_invalid_phase_defaults_to_1 | unit | pass |
| test_velocity_calculation | unit | pass |
| test_velocity_zero_days | unit | pass |
| test_forecast_calculation | unit | pass |
| test_forecast_none_velocity | unit | pass |
| test_generate_returns_dashboard_data | unit | pass |
| test_generate_current_phase | unit | pass |
| test_generate_next_action | unit | pass |
| test_generate_agents_count | unit | pass |
| test_generate_blocks_7d_positive | unit | pass |
| test_generate_stale_tool_count | unit | pass |
| test_generate_roadmap_populated | unit | pass |
| test_render_html_is_standalone | unit | pass |
| test_render_html_no_cdn | unit | pass |
| test_render_html_contains_phase | unit | pass |
| test_render_html_contains_next_action | unit | pass |
| test_render_html_contains_last_block | unit | pass |
| test_render_html_custom_css | unit | pass |
| test_write_dashboard_creates_file | unit | pass |
| test_write_dashboard_correct_path | unit | pass |
| test_write_dashboard_returns_path | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| dashboard-and-styles | ✓ | `sdk/dashboard_generator.py`, `templates/dashboard.html`, `templates/_styles.css`, `governance/dashboard.html` created |
| tests-pass | ✓ | 44/44 tests pass |
| dependencies-met | ✓ | block-103, block-104, block-107 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, this retrospective updated |

## 4. Decisions made

- **`render_html(data, css=None)` signature**: caller passes pre-read CSS string; avoids coupling render function to filesystem. `write_dashboard()` reads `templates/_styles.css` and passes it. Tests use `css=None` → inline `_FALLBACK_CSS`.
- **`_FALLBACK_CSS` module constant**: full copy of `_styles.css` design tokens embedded in Python module so `render_html()` is fully self-contained without file access — supports tests and programmatic use without arch_root.
- **Roadmap hardcoded max_phase=17**: Known from arch-v3.md brainstorm; `_build_roadmap()` accepts `max_phase` kwarg so future callers can override.
- **Manifest tier upgraded to L**: Initial manifest said Tier M, may upgrade to L. Final scope (4-column grid, timeline, roadmap, CSS system, 44 tests) warrants Tier L; noted in retrospective only (manifest frozen per protocol).

## 5. Token estimate

```
tok_estimated: ~1600  tok_src:estimated
```

## 6. Issues / surprises

None. CSS f-string escaping non-issue because CSS string is passed as a Python variable to `render_html`, not embedded in the f-string template body.

## 7. Files actually touched

- Created: `sdk/dashboard_generator.py`, `sdk/tests/test_dashboard.py`, `templates/dashboard.html`, `governance/dashboard.html`
- `templates/_styles.css` (already existed from earlier in block-105 session)
- Modified: `INDEX.md`, `STATE.md`, `NEXT.md`, `blocks/BLOCK_LOG.md`, `board.md`

---

End of retrospective.
