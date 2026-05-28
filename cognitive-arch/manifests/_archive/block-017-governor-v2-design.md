---
id: block-017
tier: M
kind: doc-only
phase: phase-4
status: planned
dependencies: []
files:
  read:
    - _brainstorm/governor-v2-redesign.md
    - _syntax.md
    - PROTOCOLS.md
    - protocols/agents.md
    - protocols/parallelism.md
    - templates/agent-roles/governor.md
  modify: []
  create:
    - design/governor-v2.md
gates:
  - name: design-doc-exists
    type: file-exists
    paths: [design/governor-v2.md]
  - name: all-13-decisions-covered
    type: manual
    description: design/governor-v2.md addresses all 13 decisions from _brainstorm/governor-v2-redesign.md
  - name: architecture-sections
    type: manual
    description: doc has sections for task packet format, return package format, sub-agent lifecycle, governor-state, convention snippets, failure handling, and manual fallback
  - name: files-updated
    type: file-changed
    paths: [design/governor-v2.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 017 — Master design doc: governor-v2.md

- **Tier:** M
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Create `design/governor-v2.md` — the authoritative specification for the SDK-based Governor v2 architecture. This is the single source of truth that all other Phase 4 blocks reference. Must be written first (group 4A); blocks 018–028 reference it.

## 2. Files

- **Read:** _brainstorm/governor-v2-redesign.md (13 decisions), _syntax.md, PROTOCOLS.md, protocols/agents.md, protocols/parallelism.md, templates/agent-roles/governor.md
- **Modify:** none
- **Create:** design/governor-v2.md

## 3. Spec

`design/governor-v2.md` must cover:

### Section 1 — Overview
- What Governor v2 is (SDK-based orchestrator, optional layer above manual mode)
- What it replaces vs. what it augments
- Two-tier architecture: manual mode (always supported) + automated mode (Governor v2)

### Section 2 — All 13 design decisions (from brainstorm)
Each decision: problem → chosen option → rationale → implications

Decision list:
1. Orchestration model: Claude Agent SDK (not custom HTTP)
2. Sub-agent isolation: temp dirs, not worktrees
3. Task packet format: compressed _syntax.md vocab
4. Return package format: compressed _syntax.md vocab
5. Convention snippet generation: Governor generates from PROTOCOLS.md
6. Governor state: governor-state.md (ephemeral, separate from STATE.md)
7. Scope discovery: explicit scope field in task packet; escalation protocol
8. Git commit ownership: sub-agent commits; Governor reviews; conflict = Governor resolves
9. Crash recovery: governor-state.md survives crashes; resume protocol
10. Intra-phase parallelism only (no cross-phase parallelism)
11. Sub-agent role: implement one block; write retrospective; emit return package
12. Governor role: orchestrate phase; validate returns; update STATE.md
13. All agent communication uses compressed _syntax.md vocabulary

### Section 3 — Task packet format (full spec)
### Section 4 — Return package format (full spec)
### Section 5 — Governor orchestration lifecycle
### Section 6 — Sub-agent execution lifecycle
### Section 7 — Failure handling overview
### Section 8 — Manual fallback: how to use all new protocols without SDK

## 4. Validation

- design/governor-v2.md exists and covers all 13 decisions
- All protocol names referenced in the doc match actual protocol files (blocks 018-023)
- Manual fallback section present

## 5. Out of scope

- Any implementation code (Phase 5 / v2.0)
- Actual Governor process execution
- Multi-repo support (v3.0+)
