---
id: block-023
tier: S
kind: doc-only
phase: phase-4
status: planned
dependencies: [block-017]
files:
  read:
    - design/governor-v2.md
    - _syntax.md
  modify: []
  create:
    - protocols/governor-failure-handling.md
gates:
  - name: protocol-exists
    type: file-exists
    paths: [protocols/governor-failure-handling.md]
  - name: failure-modes-covered
    type: manual
    description: protocol addresses all 4 failure modes (blocked, scope-exceeded, crash/timeout, gate-fail)
  - name: recovery-steps
    type: manual
    description: each failure mode has a concrete recovery procedure (retry, skip, halt, escalate)
  - name: crash-recovery
    type: manual
    description: protocol covers Governor crash recovery using governor-state.md resume point
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 023 — Protocol: governor-failure-handling

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Dependencies:** block-017

## 1. Purpose

Create `protocols/governor-failure-handling.md` — the specification for how the Governor responds to failures during phase orchestration. Covers all failure modes: blocked blocks, scope exceeded, sub-agent crashes, gate failures, and Governor crashes with resume.

## 2. Files

- **Read:** design/governor-v2.md (Decision 9, Section 7), _syntax.md
- **Modify:** none
- **Create:** protocols/governor-failure-handling.md

## 3. Spec

`protocols/governor-failure-handling.md` must cover:

### Failure mode 1 — Block blocked (status:blocked)
Sub-agent returns `status:blocked issues:DESCRIPTION`

Recovery options (Governor decides in order):
1. **Retry once:** Re-dispatch with notes: field explaining the issue
2. **Skip:** Mark block as `blocked` in governor-state.md; continue to next group
3. **Halt phase:** If blocking block is required for subsequent groups (dependency)

Decision rule: If blocked block appears in a subsequent group's `depends_on:` → halt. Otherwise → skip.

### Failure mode 2 — Scope exceeded (status:scope-exceeded)
Sub-agent returns `status:scope-exceeded scope_exp:DESCRIPTION`

Recovery:
- Log scope discovery in governor-state.md
- Mark block done (scope discovery doesn't mean failure)
- Create a new block stub for the discovered work (Governor adds to backlog)
- Never expand block scope mid-phase

### Failure mode 3 — Sub-agent crash or timeout
Sub-agent returns nothing or times out

Recovery:
1. Wait for SDK timeout (implementation-defined)
2. If no return received: mark block as `timed-out` in governor-state.md
3. Retry once with same task packet
4. If second attempt fails: treat as `blocked`

### Failure mode 4 — Gate failure (gates contain FAIL)
Sub-agent returns `status:done` but `gates:some-gate:FAIL`

Recovery:
1. Log gate failure in governor-state.md
2. Mark block as `gates-failed` (not done)
3. Retry the block if gate failure is likely transient
4. If gate failure is structural → halt and escalate to implementer

### Governor crash recovery
If Governor process crashes mid-phase:

1. Read governor-state.md to find resume point
2. Check `groups_done:` and `blocks_done:` fields
3. Skip completed groups
4. Re-dispatch remaining pending blocks (idempotent — completed blocks' files won't be re-changed)
5. Resume from last incomplete group

governor-state.md format for crash recovery:
```
phase:phase-N gov:g-NNN ts:START status:in-progress
last_checkpoint:2026-05-21T10:30Z
groups_done:4A
blocks_done:block-017,block-018,block-019
blocks_in_flight:block-020,block-021
```

### Escalation to implementer
Governor halts and notifies implementer when:
- 2+ consecutive blocks in a group are blocked
- A dependency-required block fails twice
- Governor-state.md is corrupted or unreadable

## 4. Out of scope

- SDK-specific crash recovery (Phase 5 implementation detail)
- Cross-phase failure recovery
- Human-in-the-loop approval flows (future)
