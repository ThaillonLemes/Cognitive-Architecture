---
id: block-027
tier: M
kind: refactor
phase: phase-4
status: planned
dependencies: [block-018, block-019, block-020, block-021, block-022, block-023, block-024, block-025]
files:
  read:
    - protocols/agents.md
    - design/governor-v2.md
    - protocols/task-packet.md
    - protocols/sub-agent-contract.md
    - protocols/convention-snippet-generation.md
    - templates/task-packet.md
    - templates/sub-agent-return.md
  modify:
    - protocols/agents.md
  create: []
gates:
  - name: task-packet-model
    type: manual
    description: protocols/agents.md describes sub-agents operating on task packets (not full project context)
  - name: lifecycle-updated
    type: manual
    description: sub-agent lifecycle section updated to match sub-agent-contract.md (receive packet → read fread files → execute → emit return)
  - name: backward-compatible
    type: manual
    description: manual mode (human-run sub-agent without SDK) still fully described
  - name: references-new-protocols
    type: manual
    description: agents.md links to task-packet.md, sub-agent-contract.md, and templates
  - name: files-updated
    type: file-changed
    paths: [protocols/agents.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 027 — Update: protocols/agents.md (task-packet model)

- **Tier:** M
- **Kind:** refactor
- **Status:** planned
- **Dependencies:** block-018, block-019, block-020, block-021, block-022, block-023, block-024, block-025

## 1. Purpose

Rewrite `protocols/agents.md` to describe sub-agents operating on the task-packet model (Governor v2 design). The current agents.md was written before Governor v2 was designed; it describes a full-context model where sub-agents get the entire project. This block updates it to the lean task-packet model.

## 2. Files

- **Read:** protocols/agents.md (current), design/governor-v2.md (Sections 4, 6), protocols/task-packet.md, protocols/sub-agent-contract.md, protocols/convention-snippet-generation.md, templates/task-packet.md, templates/sub-agent-return.md
- **Modify:** protocols/agents.md (major rewrite)
- **Create:** none

## 3. Spec

**Keep from current agents.md:**
- Agent role definitions (Governor, sub-agent, reviewer)
- Multi-agent coordination principles
- Board.md integration
- Manual mode instructions

**Add / rewrite:**

### Section: Sub-agent operating model (new)
- Sub-agents receive task packets, not full project context
- Sub-agent scope is bounded by the task packet's `fread:` and `fmod:` fields
- Sub-agents communicate back via return packages (not multi-turn conversation)
- Reference: `protocols/task-packet.md`, `protocols/sub-agent-contract.md`

### Section: Sub-agent lifecycle (rewrite)
1. Receive task packet (first message)
2. Parse required fields: b, kind, phase, axioms, scope, fread, fmod
3. Read ONLY files listed in fread (scope discipline)
4. Execute block per manifest
5. Follow block-close-checklist.md (sub-agent steps only)
6. Emit return package as final message (template: templates/sub-agent-return.md)

### Section: Convention snippets (new)
- Sub-agents apply only the axioms listed in `axioms:` field
- No need to read full PROTOCOLS.md (convention snippet is pre-selected)
- Reference: `protocols/convention-snippet-generation.md`

### Section: Manual mode (keep + clarify)
- Without SDK: human creates task packet using templates/task-packet.md
- Human runs sub-agent conversation manually (one conversation per block)
- Human collects return package and validates gates
- All protocols are human-followable; Governor automates the mechanical steps only

## 4. Validation

- agents.md has "task-packet" in it (key concept mentioned)
- Sub-agent lifecycle matches sub-agent-contract.md
- Manual mode section still present and accurate
- References to new protocols (task-packet.md, sub-agent-contract.md, templates) present

## 5. Out of scope

- Changing role definitions (Governor, reviewer) — those are stable
- SDK implementation code
- Multi-repo agent coordination (v3.0+)
