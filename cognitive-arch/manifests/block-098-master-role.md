---
id: block-098
tier: M
kind: implementation
phase: phase-15
scope: phase-bound
status: pending
security: false
dependencies: []
files:
  read:
    - templates/AGENT.md
    - templates/agent-roles/governor.md
    - templates/agent-roles/implementer.md
    - protocols/agents.md
    - protocols/modes.md
    - design/arch-v3.md
  modify:
    - board.md
    - INDEX.md
  create:
    - agents/agent-master.md
    - templates/agent-roles/master.md
gates:
  - name: master-role-created
    type: file-changed
    paths: [agents/agent-master.md, templates/agent-roles/master.md]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-098-master-role.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 098 — Master agent role definition

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Define the Master Agent role: identity, posture (hybrid proactive+reactive per Q5), permissions matrix (Q6 — read-all, write to master-log + governance + STATE/NEXT/board, no commits), tool registry consumption protocol. Adds the Master to board.md as the orchestrator agent.

## 2. Dependencies

None. First block of Phase 15.

## 3. Files

- **Read:** AGENT template, existing agent role templates (governor, implementer), agents protocol, modes protocol, arch-v3 design
- **Modify:** board.md (add master row), INDEX.md (catalog new files)
- **Create:** `agents/agent-master.md` (concrete agent identity), `templates/agent-roles/master.md` (reusable role template)

## 4. Validation

- `agents/agent-master.md` covers: identity, posture rules (when proactive vs reactive), permissions matrix (read/write/commit table), inter-agent comm role
- `templates/agent-roles/master.md` is reusable for other projects (no MMORPG/cognitive-arch specifics)
- board.md shows master row with appropriate initial state (`status:idle`, `lock:ready`)

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Master scope overlaps with Governor confusingly | Med | Document distinction explicitly: Governor = integration/auditing; Master = orchestration/surfacing |
| Master role too broad without clear behavior rules | High | Posture rules concrete; bound to tool registry consumption (block-099) |

## 7. Out of Scope

- Tool registry implementation (block-099)
- Trigger engine (block-100)
- Active suggestion protocol (block-101)
- Inter-agent message format (block-102)

## 8. New Abstraction

`agent-master` role. Justification: not just one role file — establishes the orchestrator pattern reusable across projects. New abstraction warranted.
