---
id: block-099
tier: M
kind: implementation
phase: phase-15
scope: phase-bound
status: pending
security: false
dependencies: [block-098]
files:
  read:
    - agents/agent-master.md
    - commands/audit.md
    - commands/health-report.md
    - commands/pattern-mining.md
    - design/arch-v3.md
  modify:
    - INDEX.md
  create:
    - governance/tools-registry.yaml
    - sdk/tools_registry.py
    - sdk/tests/test_tools_registry.py
    - protocols/tools-registry-spec.md
gates:
  - name: registry-created
    type: file-changed
    paths: [governance/tools-registry.yaml, sdk/tools_registry.py]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_tools_registry.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-098]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-099-tool-registry.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 099 — Tool registry + freshness

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Create `governance/tools-registry.yaml` listing every tool/command Master tracks, each with `last_run` (timestamp), `recommended_interval`, `priority`, `trigger_type` (time|event). Provides Python API to read/update entries. Foundation for trigger engine (block-100).

## 2. Dependencies

- block-098 (Master role must exist before defining its toolset)

## 3. Files

- **Read:** Master role doc, key command files (audit, health-report, pattern-mining), arch-v3 design
- **Modify:** INDEX.md (catalog new files)
- **Create:** `governance/tools-registry.yaml` (initial 8+ tools per design §5), `sdk/tools_registry.py` (read/update API), test file, `protocols/tools-registry-spec.md` (schema doc)

## 4. Validation

- Registry has 8+ entries matching design §5 table (audit.sh, health-report, pattern-mining, weekly-report, phase-forecast, dependency-check, conflicts, security-revalidation)
- `last_run` initialized to "never" or appropriate seed timestamp
- Python API: `read_registry()`, `update_last_run(tool_id)`, `get_stale_tools(now_ts) -> list[ToolEntry]`
- Test coverage on read/update operations

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Registry becomes stale relative to actual tools available | Med | Audit check (future) verifies registry matches commands/ directory |
| Concurrent write conflicts on registry file | Low | Single-user; advisory file lock if needed |

## 7. Out of Scope

- Trigger engine (block-100)
- Adaptive interval learning (deferred — see Master Agent posture future work)
- Multi-project registries

## 8. New Abstraction

`ToolEntry` dataclass and `tools_registry` module. Justification: consumed by Master, by audit, by future Phase 16 dashboard, by recommendation engine. Past Rule of Three.
