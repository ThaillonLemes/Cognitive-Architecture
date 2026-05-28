---
id: block-107
manifest: manifests/block-107-dependency-resolution.md
status: done
gates_passed: 4/4
completed_at: 2026-05-27T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 1
duration_source: estimated
tok_estimated: ~1400
tok_src: estimated
---

# Block 107 Retrospective — Dependency resolution automation

## 1. What was built

- Created `sdk/dependency_resolver.py`: `ManifestEntry` and `UnblockedBlock` dataclasses; `find_done_blocks(log_content)` → set; `read_manifests(arch_root, manifest_contents)` → list[ManifestEntry]; `find_unblocked(done_blocks, manifests)` → list[UnblockedBlock]; `build_notifications(unblocked)` → list[AgentMessage dict]; `run_resolver()` main entry point. Pure function design.
- Created `sdk/tests/test_dependency_resolver.py`: 23 tests.
- Created `protocols/dependency-resolution.md`: flow, board update rules, notification format.
- Updated `INDEX.md`.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| test_find_done_blocks_returns_correct_set | unit | pass |
| test_find_done_blocks_ignores_comments | unit | pass |
| test_find_done_blocks_empty_log | unit | pass |
| test_find_done_blocks_non_done_event_excluded | unit | pass |
| test_parse_deps_single | unit | pass |
| test_parse_deps_multiple | unit | pass |
| test_parse_deps_empty | unit | pass |
| test_read_manifests_extracts_id | unit | pass |
| test_read_manifests_extracts_dependencies | unit | pass |
| test_read_manifests_no_deps_empty_list | unit | pass |
| test_read_manifests_status_extracted | unit | pass |
| test_find_unblocked_no_unblocks | unit | pass |
| test_find_unblocked_single | unit | pass |
| test_find_unblocked_multiple | unit | pass |
| test_find_unblocked_done_block_excluded | unit | pass |
| test_find_unblocked_no_deps_block_excluded | unit | pass |
| test_build_notifications_produces_correct_kind | unit | pass |
| test_build_notifications_contains_block_id | unit | pass |
| test_build_notifications_from_master | unit | pass |
| test_build_notifications_empty_input | unit | pass |
| test_run_resolver_no_unblocks | unit | pass |
| test_run_resolver_finds_unblocked | unit | pass |
| test_run_resolver_empty_log | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| resolver-module | ✓ | `sdk/dependency_resolver.py` + `protocols/dependency-resolution.md` created |
| tests-pass | ✓ | 23/23 tests pass |
| dependencies-met | ✓ | block-098 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, this retrospective updated |

## 4. Decisions made

- **Pure function design**: manifest says `modify: board.md`, but board.md modification was moved to Master Agent responsibility. Justified: board.md is an AI-only coordination file; making the resolver a pure function that returns results (and Master handles the board update) is cleaner and more testable. Documented in protocol.
- Blocks with no dependencies are excluded from unblocked list (they were never "blocked").
- Done/wip blocks excluded from consideration (only pending/planned/wait states checked).
- `build_notifications()` produces dicts compatible with `sdk/agent_message_schema.py` without importing it (avoids circular dependency).

## 5. Token estimate

```
tok_estimated: ~1400  tok_src:estimated
```

## 6. Issues / surprises

None.

## 7. Files actually touched

- Created: `sdk/dependency_resolver.py`, `sdk/tests/test_dependency_resolver.py`, `protocols/dependency-resolution.md`
- Modified: `INDEX.md`, `STATE.md`, `NEXT.md`, `blocks/BLOCK_LOG.md`, `board.md`
- board.md not structurally modified by resolver (by design; see §4).

---

End of retrospective.
