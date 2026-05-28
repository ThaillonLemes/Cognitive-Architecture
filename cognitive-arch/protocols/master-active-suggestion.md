---
protection: guarded
protection_reason: Defines Master Agent's proactive behavior rules; changes affect user-facing surfacing.
---

# Protocol: Master active suggestion

BRIEF: When and how Master surfaces tool freshness suggestions to the user. Three trigger types: session-start briefing, inline at block-start, on-demand status request. Implements the hybrid proactive+reactive posture (Q5).

## Overview

The Master Agent calls `check_schedule()` (sdk/master_scheduler.py) to identify stale tools, then calls the appropriate `suggest_*` function (sdk/master_suggest.py) depending on context. Suggestions are text rendered in conversation — never auto-executed.

## The three trigger types

### 1. Session-start briefing

**When:** At every session start, before responding to the user's first request.

**Condition:** Any tool with urgency `overdue`, `very_overdue`, or `critical`.

**Action:**
1. Call `suggest_at_session_start()`.
2. If non-empty: render suggestions before any other output.
3. Format: inline list with urgency emoji and run command.
4. Muted per-tool: if tool has `muted: true` in tools-registry.yaml (future field), skip.

**Example output:**
```
🔴 **CRITICAL** — audit has not been run in 4 days (interval: 1d)
   Run: `bash audit.sh`

🟠 **VERY OVERDUE** — pattern-mining has not been run in 18 days (interval: 7d)
   Run: `python sdk/pattern_analyzer.py && python sdk/patterns_report.py`
```

**Max items:** All overdue tools shown (no cap at session start — user needs full picture).

### 2. Inline at block-start

**When:** When user begins a block (`/block-start` or reading a block manifest).

**Condition:** Any tool with urgency `critical` only (more restrictive than session-start).

**Rationale:** Inline suggestions must not disrupt block flow. Only truly critical items surface inline.

**Action:**
1. Call `suggest_inline(block_id)`.
2. If non-empty: prefix the block output with at most **2 suggestions**.
3. Label: "⚠️ Before starting — critical tool overdue:" header.

**Example output:**
```
⚠️ Before starting block-103 — critical tool overdue:
🔴 audit (4 days overdue) — Run: `bash audit.sh`
```

**Max items:** 2 (enforced in `suggest_inline()`).

### 3. On-demand status request

**When:** User asks "what's stale?", "status?", "what tools need running?", or similar.

**Condition:** Same as session-start — urgency >= overdue.

**Action:**
1. Call `suggest_on_demand()`.
2. Render full list with urgency levels and run commands.
3. Also include: tools that are stale but not yet overdue (for completeness).

## Relevance heuristic for inline suggestions

`suggest_inline(block_id)` filters to critical tools only. No additional keyword matching in v1 (future: match tool domain to block manifest files.read).

## Muting (v1 — passive only)

In v1, there is no runtime mute mechanism. User can add `# muted` comment to a tool entry in tools-registry.yaml as a convention — scheduler ignores commented-out entries naturally (YAML comment). Formal mute field (`muted: true`) deferred to future schema version.

## Master-log entry format

After generating suggestions, Master appends to `agents/master-log.md`:
```
[2026-05-27T12:00Z] SUGGEST source:session_start count:2 tools:[audit,pattern-mining]
```

## Suggestion format (text)

Each suggestion rendered as:
```
{emoji} **{URGENCY_LABEL}** — {tool_name}: {days_since} since last run (interval: {interval}d)
   Run: `{command}`
```

Where `emoji` is 🔴 (critical), 🟠 (very_overdue), 🟡 (overdue).

End of master-active-suggestion protocol.
