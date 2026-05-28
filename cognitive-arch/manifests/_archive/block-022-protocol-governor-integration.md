---
id: block-022
tier: S
kind: doc-only
phase: phase-4
status: planned
dependencies: [block-017]
files:
  read:
    - design/governor-v2.md
    - PROTOCOLS.md
    - templates/agent-roles/governor.md
  modify: []
  create:
    - protocols/governor-integration.md
gates:
  - name: protocol-exists
    type: file-exists
    paths: [protocols/governor-integration.md]
  - name: manual-automated-boundary
    type: manual
    description: protocol clearly defines which steps are manual-mode (today) vs automated-mode (Governor v2 with SDK)
  - name: sdk-integration-points
    type: manual
    description: protocol lists the 3-5 SDK integration points where manual steps become automated in v2.0
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 022 — Protocol: governor-integration

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Dependencies:** block-017

## 1. Purpose

Create `protocols/governor-integration.md` — the specification for how the Governor integrates with the rest of the cognitive architecture. Defines the boundary between manual mode (AI-driven today) and automated mode (SDK-driven in v2.0). Ensures the architecture stays usable without SDK.

## 2. Files

- **Read:** design/governor-v2.md (Sections 5, 8), PROTOCOLS.md, templates/agent-roles/governor.md
- **Modify:** none
- **Create:** protocols/governor-integration.md

## 3. Spec

`protocols/governor-integration.md` must cover:

### Integration principles
1. Governor is an optional orchestration layer — architecture works without it
2. All protocols (task-packet, sub-agent-contract, etc.) are designed to be human-followable
3. Governor automates the mechanical steps; judgment stays with the implementer

### Architecture boundaries
```
┌────────────────────────────────────────────┐
│  Manual mode (today)                       │
│  Human reads phase → creates task packets  │
│  → runs blocks → checks returns → updates  │
└────────────────────────────────────────────┘
         ↓ SDK available (v2.0) ↓
┌────────────────────────────────────────────┐
│  Automated mode (Governor v2)              │
│  Governor reads phase → dispatches agents  │
│  → collects returns → updates state        │
└────────────────────────────────────────────┘
```

### SDK integration points (Phase 5 targets)
1. **Agent dispatch:** SDK launches sub-agent with task packet → replaces manual "start a new conversation with block manifest"
2. **Parallel execution:** SDK runs group 4B blocks simultaneously → replaces "open 4 tabs and run in parallel"
3. **Return collection:** SDK receives return package from sub-agent → replaces "copy return package back to main session"
4. **governor-state.md update:** SDK writes orchestration state → replaces manual state tracking
5. **Gate validation:** SDK parses return package and validates gates → replaces manual gate check

### Files owned by Governor
- `governor-state.md` — ephemeral, Governor-only
- `board.md` — Governor updates; human reads

### Files owned by implementer (never auto-modified)
- `PROTOCOLS.md`, `CLAUDE.md`, `INDEX.md` — architecture definition files

### Coexistence rules
- governor-state.md is created fresh each phase; deleted on phase close
- STATE.md is updated by Governor after each group completes (not per block)
- Retrospectives are always written by sub-agents, never by Governor

## 4. Out of scope

- Actual SDK code (Phase 5)
- Multi-Governor support (v3.0+)
- Governor-to-Governor communication
