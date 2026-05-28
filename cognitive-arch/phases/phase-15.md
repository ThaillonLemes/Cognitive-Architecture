---
id: phase-15
status: planned
prev_phase: phase-14
exit_criteria_count: 5
blocks_count: 5
estimated_duration_days: 7
created_at: 2026-05-23
last_updated: 2026-05-23
owner: implementer
---

# Phase 15 — Master Agent v1

BRIEF: The Conductor. A single agent that knows everything, surfaces tool freshness, suggests proactively when urgent, and orchestrates communication between sub-agents. Resolves the discoverability gap identified in v3 brainstorm.

## 1. Purpose

The biggest gap of v2.5 was discoverability: 9 sophisticated features existed but went unused because nothing actively reminded the user they were available. Phase 15 introduces a Master Agent that maintains awareness of the entire architecture, tracks tool freshness via a registry, surfaces stale items proactively when urgency warrants, and orchestrates communication between any other agents the user spawns. The Master is the only agent the user needs to talk to; the Master talks to everything else.

## 2. Goals

- Master Agent role defined with hybrid posture (Q5): proactive on urgency, reactive otherwise
- Tool registry tracks freshness per tool with configurable intervals (Q8)
- Time-based trigger engine detects stale tools and surfaces them
- Active suggestion protocol: when user requests work, Master mentions stale-but-relevant tools
- Inter-agent communication contracts formalized (YAML structured per D4)

## 3. Invariants

- Master only writes to permitted files (Q6: master-log, governance/, STATE/NEXT/board — never code)
- Master never commits (commit is user authority)
- Master respects all protection tiers from Phase 13
- Master's proactive triggers configurable; user can mute any specific trigger

## 4. Dependencies

- Phase 12 complete (tools must work to be tracked)
- Phase 13 complete (Master must respect protection)
- Phase 14 complete (Master surfaces patterns from mining)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Master too chatty — interrupts user flow | High | Strict urgency criteria (2× interval missed, gate failure 24h+, dependency unblocked); user can mute per trigger |
| Master writes to STATE.md while user is editing | Med | Lock check before write; warn-and-skip if lock held |
| Master's recommendations diverge from architecture intent | Med | All Master logic referenceable via `agents/agent-master.md`; user reviews and adjusts |
| Confused inter-agent messages in YAML | Low | Schema documented and validated; mismatch produces warning + fallback to plain text |

## 6. Validation

- Master behavior tested against 5 scenarios: fresh session, post-pause, mid-block, audit-overdue, gate-failure-stale
- Tool registry maintained correctly across 7-day simulation
- Inter-agent message format validated against schema

## 7. Exit Criteria

1. `agents/agent-master.md` exists with: role description, permissions matrix (read-all, write-restricted per Q6), posture rules (proactive triggers list + reactive defaults), tool registry consumption protocol.
2. `governance/tools-registry.yaml` exists with at least 8 tools listed (per design §5 table), each with `last_run`, `recommended_interval`, `priority`, `trigger_type`.
3. `sdk/master_scheduler.py` implements time-based trigger engine: reads registry, compares to current time (America/Sao_Paulo per Q7), returns list of stale tools with urgency level.
4. `protocols/master-active-suggestion.md` documents when and how Master surfaces tools: at session start (briefing), inline with block start (relevant tools), on explicit `governor status` request.
5. `protocols/inter-agent-messages.md` defines YAML message schema for Master ↔ sub-agent communication: `from`, `to`, `kind`, `payload`, `expects_response`. Used in MMORPG multi-agent context.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-098 | Master agent role definition | M | planned | `manifests/block-098-master-role.md` |
| block-099 | Tool registry + freshness | M | planned | `manifests/block-099-tool-registry.md` |
| block-100 | Time-based trigger engine | L | planned | `manifests/block-100-trigger-engine.md` |
| block-101 | Active suggestion protocol | M | planned | `manifests/block-101-active-suggestion.md` |
| block-102 | Inter-agent communication | M | planned | `manifests/block-102-inter-agent-messages.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 5
  recommended_agents: 2
  groups:
    - id: 15A
      blocks: [block-098]
      type: sequential
      depends_on: []
    - id: 15B
      blocks: [block-099]
      type: sequential
      depends_on: [15A]
    - id: 15C
      blocks: [block-100, block-102]
      type: parallel
      depends_on: [15B]
    - id: 15D
      blocks: [block-101]
      type: sequential
      depends_on: [15C]
```

Role first (defines vocabulary), then registry (data structure), then engine + inter-agent (independent technical pieces), then suggestion protocol (consumes engine).

## 10. Out of Scope

- Master autonomous code generation (Master only surfaces, suggests, orchestrates — never writes block code itself)
- Master making commit decisions (Q6 — explicit human authority)
- Cross-project Master (single-project today; multi-project future)
- Master persistence as background daemon (depends on `_future/governor-loop.md`; Phase 15 implements interactive Master only)

---

End of phase-15.
