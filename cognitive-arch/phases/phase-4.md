---
id: phase-4
status: complete
version: v1.4
prev_phase: phase-3
exit_criteria_count: 6
blocks_count: 12
estimated_duration_days: 10
created_at: 2026-05-20
last_updated: 2026-05-21
owner: implementer
---

# Phase 4 — Governor v2 design (v1.4)

BRIEF: Write every design document and protocol stub for the SDK-based Governor. No implementation yet — this phase produces the complete specification that Phase 5 builds from.

## 1. Purpose

The brainstorm in `_brainstorm/governor-v2-redesign.md` produced 13 design decisions for the SDK-based Governor. This phase converts those decisions into:
- One master design document (`design/governor-v2.md`)
- Six new protocols (task-packet, sub-agent-contract, convention-snippet-generation, governor-dispatch, governor-integration, governor-failure-handling)
- Two new templates (task-packet, sub-agent-return)
- Updates to three existing protocols (block-close-checklist, agents, parallelism)

Phase 5 (v2.0) will implement these specs in code. Phase 4 is pure specification.

## 2. Goals

- `design/governor-v2.md` contains the complete, finalized Governor v2 architecture
- All new protocols exist as full documents (not stubs)
- block-close-checklist annotated: each step labeled sub-agent or Governor
- protocols/agents.md rewritten for task-packet model
- protocols/parallelism.md updated with phase design rules

## 3. Invariants

- No existing protocols are deleted — only updated
- Manual mode (no SDK) still fully documented and supported
- All new protocols reference `_syntax.md` compressed format for agent communication

## 4. Dependencies

- Phase 1 complete ✅
- `_brainstorm/governor-v2-redesign.md` complete ✅ (13 decisions confirmed)
- `_syntax.md` has all new communication keys ✅
- Phase 2 and Phase 3 not required (Phase 4 is independent)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Design decisions change during spec writing | Med | Block-017 (master design doc) written first; others reference it |
| Protocol explosion — too many new files | Low | 6 new protocols is bounded; each has clear scope |
| Phase 5 reveals design gaps | Med | Phase 4 retro explicitly flags open questions for Phase 5 |

## 7. Exit Criteria

1. `design/governor-v2.md` exists, covers all 13 decisions from brainstorm
2. All 6 new protocol files exist with full content (not stubs)
3. Both new template files exist
4. `protocols/block-close-checklist.md` annotated with sub-agent/Governor ownership
5. `protocols/agents.md` describes task-packet model
6. `protocols/parallelism.md` includes phase design rules

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-017 | Master design doc: governor-v2.md | M | planned | `manifests/block-017-governor-v2-design.md` |
| block-018 | Protocol: task-packet | S | planned | `manifests/block-018-protocol-task-packet.md` |
| block-019 | Protocol: sub-agent-contract | S | planned | `manifests/block-019-protocol-sub-agent-contract.md` |
| block-020 | Protocol: convention-snippet-generation | S | planned | `manifests/block-020-protocol-convention-snippet.md` |
| block-021 | Protocol: governor-dispatch | S | planned | `manifests/block-021-protocol-governor-dispatch.md` |
| block-022 | Protocol: governor-integration | S | planned | `manifests/block-022-protocol-governor-integration.md` |
| block-023 | Protocol: governor-failure-handling | S | planned | `manifests/block-023-protocol-governor-failure.md` |
| block-024 | Template: task-packet | S | planned | `manifests/block-024-template-task-packet.md` |
| block-025 | Template: sub-agent-return | S | planned | `manifests/block-025-template-sub-agent-return.md` |
| block-026 | Update: block-close-checklist (annotate ownership) | S | planned | `manifests/block-026-update-block-close-checklist.md` |
| block-027 | Update: protocols/agents.md (task-packet model) | M | planned | `manifests/block-027-update-agents-protocol.md` |
| block-028 | Update: protocols/parallelism.md (phase design rules) | S | planned | `manifests/block-028-update-parallelism-protocol.md` |

## 9. Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 12
  recommended_agents: 4
  groups:
    - id: 4A
      blocks: [block-017]
      type: sequential
      depends_on: []
      note: master design doc — run first so others can reference it
    - id: 4B
      blocks: [block-018, block-019, block-020, block-021, block-022, block-023, block-024, block-025]
      type: parallel
      depends_on: [4A]
      note: all create new files — no conflicts; reference governor-v2.md
    - id: 4C
      blocks: [block-026, block-027, block-028]
      type: parallel
      depends_on: [4B]
      note: update existing files — no conflicts; reference new protocols
```

## 10. Out of Scope

- Any SDK code or implementation (Phase 5 / v2.0)
- Actual Governor process execution
- Multi-repo support (v3.0+)
- Cross-phase parallelism machinery (deferred to v3.0+)
