---
id: block-099
manifest: manifests/block-099-tool-registry.md
status: done
gates_passed: 4/4
completed_at: 2026-05-27T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 1
duration_source: estimated
tok_estimated: ~1800
tok_src: estimated
---

# Block 099 Retrospective — Tool registry + freshness

## 1. What was built

- Created `governance/tools-registry.yaml`: 9-tool registry (8+ required) — audit, health-report, pattern-mining, weekly-report, phase-forecast, dependency-check, conflicts-check, security-revalidation, integrity-check. Each with id, name, command, description, recommended_interval_days, trigger_type, priority, last_run, mutable_by.
- Created `sdk/tools_registry.py`: `ToolEntry` dataclass with `days_since_last_run`, `is_stale`, `is_overdue` properties; `read_registry()`, `update_last_run()`, `get_stale_tools()` functions; CLI (`--list`, `--stale`, `--overdue`, `--update`).
- Created `sdk/tests/test_tools_registry.py`: 19 tests; all pass.
- Created `protocols/tools-registry-spec.md`: schema doc with freshness rules and mutability contract.
- Updated `INDEX.md` with all new files.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| test_read_registry_returns_all_tools | unit | pass |
| test_read_registry_first_tool_id | unit | pass |
| test_read_registry_interval_parsed_as_float | unit | pass |
| test_read_registry_last_run_never | unit | pass |
| test_read_registry_last_run_timestamp | unit | pass |
| test_read_registry_event_tool | unit | pass |
| test_days_since_last_run_never | unit | pass |
| test_days_since_last_run_event_tool | unit | pass |
| test_is_overdue_never_run | unit | pass |
| test_is_stale_never_run | unit | pass |
| test_is_stale_recent_tool | unit | pass |
| test_is_overdue_event_tool | unit | pass |
| test_update_last_run_changes_value | unit | pass |
| test_update_last_run_other_tools_unchanged | unit | pass |
| test_update_last_run_invalid_id_raises | unit | pass |
| test_get_stale_tools_includes_never_run | unit | pass |
| test_get_stale_tools_excludes_event_tools | unit | pass |
| test_get_stale_tools_threshold_multiplier_2 | unit | pass |
| test_get_stale_tools_fresh_tool_excluded | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| registry-created | ✓ | `governance/tools-registry.yaml` + `sdk/tools_registry.py` created |
| tests-pass | ✓ | 19/19 tests pass |
| dependencies-met | ✓ | block-098 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, this retrospective updated |

## 4. Decisions made

- 9 tools registered (manifest required ≥8). Added `integrity-check` as 9th (aligns with Phase 13 deliverable).
- Minimal YAML parser written in-house (stdlib-only). Uses `re.split(r"(?m)^  - id:", ...)` to split tool blocks — robust to comments and blank lines.
- `update_last_run()` uses line-by-line scan with `stripped.startswith("- id:")` detection. Avoids regex across tool blocks (which would need non-greedy DOTALL patterns).
- `is_overdue` threshold set at 2× recommended_interval (consistent with Master Agent posture rules from block-098).

## 5. Deferred to future blocks

- Trigger engine (block-100) — reads this registry and compares to `now`.
- Auto-adding new tools when commands/ directory changes (future audit check idea, logged as deferred).

## 6. Token estimate

```
tok_estimated: ~1800  tok_src:estimated
```

## 7. Issues / surprises

None. The minimal YAML parser worked cleanly on first run for all 19 test cases.

## 8. Files actually touched

- Created: `governance/tools-registry.yaml`, `sdk/tools_registry.py`, `sdk/tests/test_tools_registry.py`, `protocols/tools-registry-spec.md`
- Modified: `INDEX.md`, `STATE.md`, `NEXT.md`, `blocks/BLOCK_LOG.md`, `board.md`
- As manifest otherwise.

---

End of retrospective.
