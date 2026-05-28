---
id: block-102
tier: M
kind: implementation
phase: phase-15
scope: phase-bound
status: pending
security: false
dependencies: [block-099]
files:
  read:
    - agents/agent-master.md
    - protocols/agents.md
    - protocols/parallelism.md
    - design/arch-v3.md
  modify: []
  create:
    - protocols/inter-agent-messages.md
    - sdk/agent_message_schema.py
    - sdk/tests/test_agent_messages.py
    - templates/agent-message.yaml
gates:
  - name: schema-and-protocol
    type: file-changed
    paths: [protocols/inter-agent-messages.md, sdk/agent_message_schema.py, templates/agent-message.yaml]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_agent_messages.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-099]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-102-inter-agent-messages.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 102 — Inter-agent communication

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Define structured YAML message format (per D4) for Master ↔ sub-agent communication. Includes: required fields (from, to, kind, payload), optional (expects_response, correlation_id, deadline). Provides schema validator and example template. Used initially in cognitive-arch (single-agent) but designed for MMORPG multi-agent later.

## 2. Dependencies

- block-099 (tool registry establishes vocabulary that messages may reference)

## 3. Files

- **Read:** Master role, agents protocol, parallelism protocol, arch-v3
- **Modify:** —
- **Create:** `protocols/inter-agent-messages.md` (spec), `sdk/agent_message_schema.py` (validator), test file, `templates/agent-message.yaml` (example)

## 4. Validation

- Spec defines all required + optional fields with types
- Validator accepts well-formed messages, rejects malformed with specific error
- Example template covers 3 message kinds: `request`, `notification`, `response`
- Test suite covers happy paths + 5 malformation cases

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| YAML format chosen instead of JSON might cause parser issues | Low | YAML chosen for human-readability (D4); pyyaml is standard |
| Schema too restrictive for future evolution | Med | Schema includes `extensions: dict` for forward-compat fields |
| Single-user context makes this premature | Low | Foundation for MMORPG multi-agent; thin investment now |

## 7. Out of Scope

- Transport mechanism (file-based delivery for now; future could be queue)
- Encryption / signing (not needed for filesystem-local)
- Multi-hop routing (only direct master ↔ sub-agent)

## 8. New Abstraction

`AgentMessage` schema. Justification: foundation for any future multi-agent communication; consumed by Master, by future sub-agents, by audit checks. Clear Rule of Three.
