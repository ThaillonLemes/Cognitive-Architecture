---
id: phase-20
status: done
blocks_completed: 5/5
actual_duration_minutes: 180
tok_actual: 22000
exit_criteria_met: 5/5
closed_at: 2026-05-28
---

# Phase 20 Retrospective — Learning Loop

## Exit Criteria Verification

1. `governance/proposals/` with proposal.md schema (pending|accepted|rejected) ✓ — block-121
2. `sdk/protocol_updater.py` generates proposals for patterns D1 ≥ 3; dedup by glob ✓ — block-122
3. `session_start.py` shows `[PROPOSALS] N pending` at every session start ✓ — block-123
4. `sdk/proposal_resolver.py --accept/--reject` updates file + index; `--apply` patches with .bak ✓ — block-125
5. Dashboard proposals widget: badge + last 5 table ✓ — block-124

## What went well

- Python 3.13 `global` declaration issue caught and fixed before tests ran (protocol_updater.py)
- getattr()-based backwards compat pattern kept DashboardData schema stable across 3 new widgets
- 634 tests — all passing; no regressions across phases 18-20

## Decisions

- proposal_resolver `--apply` is annotation-only (appends HTML comment); actual content edit is always human — prevents auto-corruption
- Index update uses regex on markdown table; no YAML parse overhead at runtime
- Proposals use deterministic IDs (date + slug) for human-readable dedup

## Metrics

| Metric | Value |
|--------|-------|
| Blocks | 5 |
| Tests added | 43 (proposals_widget: 15, resolver: 28) |
| Total test count | 634 |
| tok_actual (est.) | 22,000 |

## Next

Phase 21 — Governor Persistent (blocks 126-129)
