---
protection: guarded
protection_reason: Defines the schema contract for the tools registry; changes require conscious review.
---

# Protocol: Tools registry specification

BRIEF: Schema and contract for `governance/tools-registry.yaml`. Read before adding or modifying registry entries. Consumed by Master Agent, trigger engine (block-100), and dashboard (Phase 16).

## File location

`governance/tools-registry.yaml`

## Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Schema version; current: `"1.0"` |
| `generated_at` | string (date) | Date the registry was last regenerated (YYYY-MM-DD) |
| `timezone` | string | Timezone for interval interpretation; canonical: `America/Sao_Paulo` |
| `tools` | list | List of ToolEntry objects (see below) |

## ToolEntry fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique tool identifier (kebab-case). Used as primary key. |
| `name` | string | ✓ | Human-readable tool name. |
| `command` | string | ✓ | Canonical command to run the tool from arch root. |
| `description` | string | ✓ | One-line description of what the tool does. |
| `recommended_interval_days` | float | ✓ | How often this tool should run. `0` = event-triggered. |
| `trigger_type` | enum | ✓ | `time` (calendar-driven) or `event` (block-close, dependency change). |
| `priority` | enum | ✓ | `high`, `medium`, or `low`. Affects Master surfacing order. |
| `last_run` | string | ✓ | ISO-8601 timestamp of last run, or `"never"`. |
| `mutable_by` | string | ✓ | Who may update `last_run`. Always `master` in v1. |

## Freshness rules

| State | Condition | Master behavior |
|-------|-----------|-----------------|
| **Fresh** | `days_since_last_run ≤ recommended_interval_days` | No mention |
| **Stale** | `days_since_last_run > recommended_interval_days` | Mentioned on request or in briefing |
| **Overdue** | `days_since_last_run > 2 × recommended_interval_days` | Surfaced proactively before any block work |

Event-triggered tools (`trigger_type: event`) are never evaluated by interval.

## Mutability contract

- `last_run` field: Master Agent updates this after each tool run.
- All other fields: **frozen** after registry creation. Changes require a new block (or mini-block if in scope).
- Master NEVER modifies `id`, `command`, `recommended_interval_days`, `trigger_type`, or `priority`.

## Adding a new tool

To add a new tool to the registry:
1. Verify the tool's `command` exists (file or script path reachable from arch root).
2. Assign appropriate `trigger_type`, `priority`, and `recommended_interval_days` (consult design/arch-v3.md §5 for defaults).
3. Set `last_run: "never"`.
4. Add entry to `governance/tools-registry.yaml` in the `tools:` list.
5. Update `INDEX.md` if the tool is a new SDK module.

## Current tools (v1, block-099)

| id | interval | trigger | priority |
|----|----------|---------|----------|
| audit | 1d | time | high |
| health-report | 3d | time | high |
| pattern-mining | 7d | time | medium |
| weekly-report | 7d | time | medium |
| phase-forecast | 3d | time | medium |
| dependency-check | event | event | high |
| conflicts-check | 1d | time | medium |
| security-revalidation | 30d | time | medium |
| integrity-check | 1d | time | high |

End of tools-registry-spec.
