---
id: phase-2
status: planned
version: v1.2
prev_phase: phase-1
exit_criteria_count: 4
blocks_count: 4
estimated_duration_days: 3
created_at: 2026-05-20
last_updated: 2026-05-20
owner: implementer
---

# Phase 2 — Token metering (v1.2)

BRIEF: Add token cost visibility to the architecture. Every HOT file gets a token estimate. A new `/token-audit` command reports boot cost. Retrospectives track token usage per block.

## 1. Purpose

The architecture has no visibility into its own token cost. CLAUDE.md has a line budget (Q2) but lines ≠ tokens. A 60-line file with dense tables costs more than a 60-line file with short sentences. This phase adds:
- Token estimation (proxy: chars/4) for all HOT files
- A `/token-audit` command to surface costs on demand
- Token fields in retrospective template
- Token budget guidance in PROTOCOLS.md Q2

## 2. Goals

- HOT file token costs are estimable without SDK
- `/token-audit` reports boot cost and per-file breakdown
- Retrospectives record estimated token cost per block
- PROTOCOLS.md Q2 mentions token estimates alongside line budgets
- audit.sh reports total HOT boot token estimate

## 3. Invariants

- No new external dependencies (proxy estimation = chars/4, pure bash)
- Existing audit.sh checks (1-4/8) remain unchanged in behavior
- All changes are backward compatible

## 4. Dependencies

- Phase 1 complete ✅
- _syntax.md has tok_in, tok_out, tok_src, tok_estimated keys ✅ (added in brainstorm session)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Token estimation inaccurate (±30%) | Low | Clearly labeled "estimated"; SDK measurement added in Phase 5 |
| audit.sh grows too large | Low | Token reporting is INFO only, not a gate check |

## 7. Exit Criteria

1. `commands/token-audit.md` exists and describes a complete token audit workflow
2. `templates/block-retrospective.md` includes `tok_estimated:` field
3. `audit.sh` reports HOT file token estimates in INFO section
4. `PROTOCOLS.md` Q2 includes token estimates alongside line budgets

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-007 | Token audit command | S | planned | `manifests/block-007-token-audit-command.md` |
| block-008 | Retrospective template — token fields | S | planned | `manifests/block-008-retrospective-token-fields.md` |
| block-009 | audit.sh — token estimation INFO section | S | planned | `manifests/block-009-audit-token-estimation.md` |
| block-010 | PROTOCOLS.md Q2 — token budget estimates | S | planned | `manifests/block-010-protocols-token-budgets.md` |

## 9. Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 4
  groups:
    - id: 2A
      blocks: [block-007, block-008, block-009, block-010]
      type: parallel
      depends_on: []
```

All 4 blocks touch different files — fully parallel.

## 10. Out of Scope

- Real token measurement via Claude API (Phase 5 / v2.0 with SDK)
- Token budget enforcement as a gate (future; currently informational only)
- Per-session token tracking dashboard (future)
