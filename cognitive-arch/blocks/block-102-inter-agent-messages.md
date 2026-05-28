---
id: block-102
manifest: manifests/block-102-inter-agent-messages.md
status: done
gates_passed: 4/4
completed_at: 2026-05-27T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 1
duration_source: estimated
tok_estimated: ~1500
tok_src: estimated
---

# Block 102 Retrospective — Inter-agent communication

## 1. What was built

- Created `protocols/inter-agent-messages.md`: full YAML message schema spec (v1.0); required/optional fields table; kind conventions (request/notification/response payload shapes); validation rules; delivery mechanism note; audit trail format.
- Created `sdk/agent_message_schema.py`: `AgentMessage` dataclass with `to_dict()`, `from_dict()`, `audit_line()`; `validate(dict) -> list[str]`; `is_valid(dict) -> bool`; `create_message()` factory; `create_response()` factory; CLI demo.
- Created `sdk/tests/test_agent_messages.py`: 23 tests (3 happy paths, 6 malformation cases, factory tests, dataclass round-trip, audit line).
- Created `templates/agent-message.yaml`: three worked examples (request, notification, response).
- Updated `INDEX.md` with all new files.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| test_valid_request_message | unit | pass |
| test_valid_notification_message | unit | pass |
| test_valid_response_message | unit | pass |
| test_is_valid_returns_true_for_valid | unit | pass |
| test_missing_from_field | unit | pass |
| test_missing_to_field | unit | pass |
| test_invalid_kind | unit | pass |
| test_empty_from_string | unit | pass |
| test_payload_not_dict | unit | pass |
| test_not_a_dict_input | unit | pass |
| test_is_valid_returns_false_for_invalid | unit | pass |
| test_create_message_produces_valid_output | unit | pass |
| test_create_message_sets_schema_version | unit | pass |
| test_create_message_invalid_kind_raises | unit | pass |
| test_create_message_empty_from_raises | unit | pass |
| test_create_message_includes_correlation_id | unit | pass |
| test_create_message_extensions_included | unit | pass |
| test_create_response_correlated_to_request | unit | pass |
| test_create_response_is_valid | unit | pass |
| test_agent_message_from_dict_valid | unit | pass |
| test_agent_message_from_dict_invalid_raises | unit | pass |
| test_agent_message_to_dict_round_trip | unit | pass |
| test_agent_message_audit_line | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| schema-and-protocol | ✓ | `protocols/inter-agent-messages.md` + `sdk/agent_message_schema.py` + `templates/agent-message.yaml` created |
| tests-pass | ✓ | 23/23 tests pass |
| dependencies-met | ✓ | block-099 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, this retrospective updated |

## 4. Decisions made

- `from` is a reserved Python keyword; `AgentMessage` uses `from_id` internally but the dict/YAML representation uses `"from"`. `to_dict()` and `from_dict()` handle the mapping transparently.
- `extensions: dict` field added for forward-compatibility (per manifest risk table mitigation).
- Validation uses strict-required-field check first, returns early on missing fields to avoid spurious downstream errors.
- Delivery mechanism kept filesystem-agnostic (in-memory in v1); appends to master-log.md via `audit_line()`.

## 5. Deferred to future blocks

- Active suggestion protocol (block-101 — next).
- Filesystem delivery to `governance/agent-inbox/` (future Phase 16+).

## 6. Token estimate

```
tok_estimated: ~1500  tok_src:estimated
```

## 7. Issues / surprises

None. Python's `from` keyword conflict was anticipated and handled cleanly.

## 8. Files actually touched

- Created: `protocols/inter-agent-messages.md`, `sdk/agent_message_schema.py`, `sdk/tests/test_agent_messages.py`, `templates/agent-message.yaml`
- Modified: `INDEX.md`, `STATE.md`, `NEXT.md`, `blocks/BLOCK_LOG.md`, `board.md`
- As manifest otherwise.

---

End of retrospective.
