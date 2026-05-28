---
id: block-101
manifest: manifests/block-101-active-suggestion.md
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

# Block 101 Retrospective — Active suggestion protocol

## 1. What was built

- Created `protocols/master-active-suggestion.md`: full behavior spec for 3 trigger types — session-start (all overdue), inline at block-start (critical only, max 2), on-demand (all overdue). Muting convention, master-log entry format, per-trigger example output.
- Created `sdk/master_suggest.py`: `Suggestion` dataclass; `suggest_at_session_start()`, `suggest_inline(block_id)`, `suggest_on_demand()`; `render_suggestions()`, `session_start_block()`, `inline_block()` convenience renderers; CLI (`--session`, `--inline`, `--demand`).
- Modified `agents/agent-master.md`: added "Active suggestion protocol" section with trigger table and session-start sequence.
- Updated `INDEX.md` with both new files.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| test_session_start_no_stale_empty | unit | pass |
| test_session_start_returns_all_stale | unit | pass |
| test_session_start_critical_first | unit | pass |
| test_session_start_suggestion_has_all_fields | unit | pass |
| test_session_start_excludes_event_tools | unit | pass |
| test_inline_empty_when_no_critical | unit | pass |
| test_inline_returns_critical_only | unit | pass |
| test_inline_max_two_suggestions | unit | pass |
| test_inline_source_is_inline | unit | pass |
| test_inline_accepts_none_block_id | unit | pass |
| test_on_demand_empty_when_all_fresh | unit | pass |
| test_on_demand_returns_all_stale | unit | pass |
| test_on_demand_source_is_on_demand | unit | pass |
| test_render_no_suggestions | unit | pass |
| test_render_includes_tool_name | unit | pass |
| test_render_with_header | unit | pass |
| test_session_start_block_empty_string_when_no_stale | unit | pass |
| test_session_start_block_returns_text_when_stale | unit | pass |
| test_inline_block_empty_string_when_no_critical | unit | pass |
| test_inline_block_returns_text_with_block_id | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| protocol-and-module | ✓ | `protocols/master-active-suggestion.md` + `sdk/master_suggest.py` created |
| tests-pass | ✓ | 20/20 tests pass |
| dependencies-met | ✓ | block-100 + block-102 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, this retrospective updated |

## 4. Decisions made

- `suggest_inline()` restricts to `critical` only. Justification: inline suggestions at block-start must not disrupt flow; only genuinely urgent items surface. "very_overdue" and "overdue" are shown in session briefing, not inline.
- Max 2 inline suggestions (`_INLINE_MAX = 2`). This is a named constant, not a magic number.
- `session_start_block()` returns empty string (not None) when no stale tools. Caller can do `if text: print(text)` cleanly.
- `agents/agent-master.md` modified as per manifest (guarded file — no ceremony needed per protocols/architecture-integrity.md for guarded tier).

## 5. Deferred to future blocks

- HTML dashboard integration (Phase 16 — block-106).
- Dependency resolver (block-107).

## 6. Token estimate

```
tok_estimated: ~1400  tok_src:estimated
```

## 7. Issues / surprises

None.

## 8. Files actually touched

- Created: `protocols/master-active-suggestion.md`, `sdk/master_suggest.py`, `sdk/tests/test_master_suggest.py`
- Modified: `agents/agent-master.md`, `INDEX.md`, `STATE.md`, `NEXT.md`, `blocks/BLOCK_LOG.md`, `board.md`
- As manifest otherwise.

---

End of retrospective.
