# _future: Governor adaptive loop

BRIEF: A pattern where the Governor agent runs continuously with adaptive polling, integrating and auditing without manual user trigger. Designed but NOT included in v1 due to idle token cost.

## Why this is in _future

Continuous Governor polling has real idle cost. Conservative estimate:
- Fixed 30s polling: ~$240/month in idle tokens (Opus pricing, 8h/day × 30 days)
- Adaptive backoff (1m active / 5m idle / 30m deep idle): ~$24/month

v1 sticks with manual Governor trigger ($0 idle cost) to keep the architecture lean and avoid burning tokens during design iteration.

## When to activate

Activate when ALL:
- Project is stable and used long-term
- Multi-agent work is the primary mode
- Manual trigger overhead is hurting productivity
- You're willing to spend on idle tokens for the speed gain

## How it works (design)

Governor session stays alive. On wake-up:

1. **Check board.md** — any agents with `status:done lock:ready`?
2. **Check stale locks** — any `lock:in-progress` > 1h?
3. **Check audit cadence** — has 30 blocks been integrated since last audit?
4. **Check L-tier pending** — any Tier L manifests waiting review?

If any trigger:
- Perform appropriate action (integrate / audit / review / notify)
- Wake-up timer = 1 minute (active mode)

If nothing:
- Wake-up timer = backoff per the schedule below

## Adaptive backoff schedule

| Mode | Trigger | Wake interval |
|------|---------|---------------|
| Active | commit in last 5 min | 60 seconds |
| Idle | no commit 5-30 min | 5 minutes |
| Deep idle | no commit > 30 min | 30 minutes |
| Sleep | user signals "stop" | infinite (manual restart) |

The Governor adapts based on activity. After a flurry of integrations, it polls fast. When the team goes home, it polls slow.

## Tooling needed

In Claude Code today: `ScheduleWakeup` tool exists for this pattern. Governor would use it to reschedule itself.

In other LLM clients: depends on whether the client supports scheduled re-invocations.

## Costs

- ~$24-50/month idle cost
- 100-300 token cost per wake (small)
- Linear in active hours per day

## Risks

- **Race conditions:** Governor integrating while agent is mid-commit. Mitigated by lock mechanism: Governor only integrates `lock:ready` rows.
- **Infinite loop:** Governor wakes, finds nothing, wakes again forever. Mitigated by deep-idle 30-min interval.
- **User confusion:** Governor acting "behind the user's back". Mitigated by:
  - Notification on every action (status update message)
  - Easy "stop" command
  - Audit log of all Governor actions

## Activation steps (when ready)

1. Read this file fully
2. Add `commands/governor-loop.md` (new file, derived from this design)
3. Modify `templates/agent-roles/governor.md` to support loop mode
4. Add `_syntax.md` entries for loop-related fields
5. Document risks and cost expectation in user-facing docs
6. Add toggle: user can disable loop mode at any time

## Alternative: scheduled cron

Instead of continuous loop:
- User schedules Governor to wake at specific times (e.g., every 2h during work hours)
- Less granular but cheaper than full loop
- Available in Claude Code via `CronCreate`

This is intermediate between "manual only" and "full adaptive loop".

End of governor-loop design.
