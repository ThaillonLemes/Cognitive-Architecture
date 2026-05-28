---
id: block-100
tier: M
kind: implementation
phase: phase-15
scope: phase-bound
status: pending
security: false
dependencies: [block-099]
files:
  read:
    - governance/tools-registry.yaml
    - sdk/tools_registry.py
    - agents/agent-master.md
    - design/arch-v3.md
  modify: []
  create:
    - sdk/master_scheduler.py
    - sdk/tests/test_master_scheduler.py
    - protocols/master-scheduler-spec.md
gates:
  - name: scheduler-module
    type: file-changed
    paths: [sdk/master_scheduler.py]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_master_scheduler.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-099]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-100-trigger-engine.md]
created_at: 2026-05-23
estimated_duration_days: 2
---

# Block 100 — Time-based trigger engine

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Implement the scheduler that reads tools-registry, compares `last_run + recommended_interval` against current time in America/Sao_Paulo (Q7), and returns list of stale tools with urgency classification (overdue / very-overdue / critical). Backbone of Master's proactive behavior.

## 2. Dependencies

- block-099 (tool registry must exist for scheduler to read)

## 3. Files

- **Read:** tools-registry.yaml + module, Master role, arch-v3 design
- **Modify:** —
- **Create:** `sdk/master_scheduler.py` (engine), `sdk/tests/test_master_scheduler.py`, `protocols/master-scheduler-spec.md` (behavior doc)

## 4. Validation

- Scheduler returns deterministic output for given (registry_state, current_time) input
- Urgency classification rules: `overdue` = past recommended_interval; `very_overdue` = 2× interval; `critical` = 3× interval AND `priority: high`
- Timezone handled correctly (America/Sao_Paulo)
- Test suite covers: no stale tools, some stale, all stale, never-run tool, edge cases (DST transition)
- Pure function — no side effects (registry updates happen elsewhere)

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| DST handling wrong | Med | Use zoneinfo from stdlib; test with DST transition fixtures |
| Urgency thresholds annoying or invisible | Med | Tunable per tool via registry; user can override |
| Time comparisons cross-OS inconsistency | Low | All comparisons via UTC internally, display in local zone |

## 7. Out of Scope

- Active surfacing of stale tools (block-101)
- Adaptive learning of intervals (future)
- Event-triggered tool execution (handled separately in block-107 for dependency events)

## 8. New Abstraction

`StaleTool` record + urgency enum. Justification: consumed by suggestion protocol (block-101), by dashboard (Phase 16), by master log entries. Three clear callers.
