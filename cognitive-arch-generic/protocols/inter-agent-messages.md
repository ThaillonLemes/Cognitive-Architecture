---
protection: guarded
protection_reason: Defines inter-agent communication contract; changes must be backward-compatible.
---

# Protocol: Inter-agent messages

BRIEF: Structured YAML message schema for Master ↔ sub-agent communication (D4). Defines required fields, optional fields, validation rules, and example usage. Consumed by Master Agent and any sub-agent that sends or receives structured messages.

## Motivation

v3 Master Agent needs a formal communication contract to:
1. Surface tool freshness reports to sub-agents mid-block.
2. Receive completion notifications from sub-agents.
3. Coordinate dependency resolution across agents.

Unstructured text messages lose auditability and break the `.governor/log.md` trail. YAML messages are machine-readable, diffable, and human-readable.

## Message schema (v1.0)

```yaml
schema_version: "1.0"    # required; string
from: "<agent-id>"        # required; non-empty string (e.g., "master", "implementer")
to: "<agent-id>"          # required; non-empty string
kind: "<kind>"            # required; enum: request | notification | response
sent_at: "<ISO-8601>"     # required; auto-set by create_message()
payload:                  # required; dict (arbitrary contents; kind-specific)
  key: value
expects_response: false   # optional; bool; default false
correlation_id: null      # optional; string; links request to its response
deadline: null            # optional; ISO-8601 string; response expected before this time
extensions: {}            # optional; dict; forward-compatibility bag
```

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Schema version; current: `"1.0"` |
| `from` | string | Sending agent id (e.g., `master`, `implementer`, `governor`) |
| `to` | string | Receiving agent id |
| `kind` | enum | `request`, `notification`, or `response` |
| `sent_at` | string | ISO-8601 timestamp; set automatically by `create_message()` |
| `payload` | dict | Arbitrary message body; contents defined by kind conventions below |

## Optional fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `expects_response` | bool | `false` | Whether sender expects a reply |
| `correlation_id` | string | `null` | UUID or slug linking a response to its request |
| `deadline` | string | `null` | ISO-8601; response required before this time |
| `extensions` | dict | `{}` | Forward-compatibility bag for future fields |

## Kind conventions

### `request`
Sender asks receiver to take an action or provide information.
Payload should include:
- `action`: string (e.g., `"run_tool"`, `"check_state"`, `"block_status"`)
- `args`: dict (action-specific parameters)

### `notification`
Sender informs receiver of an event. No response expected (set `expects_response: false`).
Payload should include:
- `event`: string (e.g., `"block_closed"`, `"tool_overdue"`, `"dep_unblocked"`)
- `data`: dict (event-specific data)

### `response`
Sender replies to a previous `request`. Must include `correlation_id` matching the request.
Payload should include:
- `status`: string (`"ok"`, `"error"`, `"partial"`)
- `result`: any (request-specific result data)
- `error_message`: string | null (if `status == "error"`)

## Validation rules

A message is **valid** if:
1. All required fields are present.
2. `schema_version` is a non-empty string.
3. `from` and `to` are non-empty strings.
4. `kind` is one of: `request`, `notification`, `response`.
5. `sent_at` is a non-empty string (ISO-8601 not enforced at validation time).
6. `payload` is a dict (not null, not a list, not a scalar).

Use `sdk/agent_message_schema.py` — `validate(msg_dict) -> list[str]` — to check messages programmatically.

## Delivery mechanism (v1)

In v1 (single-user, interactive), messages are not persisted to disk. Master Agent constructs messages in-memory for logging to `agents/master-log.md`. Future versions may write to a `governance/agent-inbox/<agent-id>/` queue.

## Audit trail

All messages sent or received by Master Agent must be appended to `agents/master-log.md`:
```
[2026-05-27T12:00:00Z] MSG from:master to:implementer kind:notification event:tool_overdue tool_id:audit
```

## Examples

See `templates/agent-message.yaml` for three worked examples (request, notification, response).

End of inter-agent-messages protocol.
