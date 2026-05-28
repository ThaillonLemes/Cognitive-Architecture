---
protection: guarded
protection_reason: Defines Master Agent scheduling behavior; changes require conscious review.
---

# Protocol: Master scheduler specification

BRIEF: Behavioral contract for `sdk/master_scheduler.py`. Defines urgency classification rules, timezone handling, event exclusions, and output format. Read before modifying scheduler logic or adding urgency levels.

## Purpose

The Master Scheduler reads `governance/tools-registry.yaml` and produces a sorted list of stale tools with urgency labels. It is a **pure function** — it does not modify the registry or any state file. Registry updates (last_run) are performed by the caller after a tool runs.

## Urgency classification rules

Three urgency levels (applied in order — first match wins):

| Level | Condition | Display emoji |
|-------|-----------|---------------|
| `critical` | `days_since > 3 × interval` **AND** `priority == "high"` | 🔴 |
| `very_overdue` | `days_since > 2 × interval` | 🟠 |
| `overdue` | `days_since > 1 × interval` | 🟡 |

Note: conditions use **strict greater-than** (`>`). A tool at exactly 2× interval is `overdue`, not `very_overdue`.

### Never-run tools

A tool with `last_run: "never"` is assigned `days_since = 999_999` (sentinel). This guarantees:
- High-priority tools → `critical`
- Medium/low-priority tools → `very_overdue`

### Event-triggered tools

Tools with `trigger_type: event` are **always excluded** from scheduler results. Their freshness is managed by event hooks (e.g., block-close).

## Timezone handling

- All comparisons are performed in **UTC** internally.
- `last_run` timestamps are stored as ISO-8601 with UTC offset.
- Naive timestamps are treated as UTC.
- Display helpers use `America/Sao_Paulo` (Q7) via `zoneinfo.ZoneInfo`.

## Sort order

Results sorted by:
1. Urgency (`critical` → `very_overdue` → `overdue`)
2. `days_since_last_run` descending (longest-neglected first within the same urgency)

## StaleTool record fields

| Field | Type | Description |
|-------|------|-------------|
| `tool_id` | str | Registry `id` |
| `tool_name` | str | Registry `name` |
| `urgency` | str | `"critical"` / `"very_overdue"` / `"overdue"` |
| `days_overdue` | float | `days_since - interval` (positive = overdue) |
| `days_since_last_run` | float | Raw days elapsed; `999999.0` = never run |
| `recommended_interval_days` | float | From registry entry |
| `priority` | str | From registry entry |
| `command` | str | From registry entry |
| `message` | str | Human-readable one-line summary |

## Integration with Master Agent

Master Agent calls `check_schedule()` at session start:
1. If any `critical` tools exist → surface immediately, before responding to user.
2. If any `very_overdue` or `overdue` → include in session briefing.
3. After each tool is run → call `update_last_run(tool_id)` from `sdk/tools_registry.py`.

## CLI usage

```bash
# List all stale tools
python sdk/master_scheduler.py --arch-root .

# Print markdown report
python sdk/master_scheduler.py --arch-root . --report

# Exit code: 0 if all current, 1 if any stale
```

End of master-scheduler-spec.
