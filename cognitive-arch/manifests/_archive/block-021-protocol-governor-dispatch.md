---
id: block-021
tier: S
kind: doc-only
phase: phase-4
status: planned
dependencies: [block-017]
files:
  read:
    - design/governor-v2.md
    - phases/phase-4.md
    - _syntax.md
  modify: []
  create:
    - protocols/governor-dispatch.md
gates:
  - name: protocol-exists
    type: file-exists
    paths: [protocols/governor-dispatch.md]
  - name: dispatch-lifecycle
    type: manual
    description: protocol covers full dispatch lifecycle (phase-start → read phase doc → build group → dispatch batch → collect returns → validate → next group)
  - name: parallel-group-handling
    type: manual
    description: protocol explains how Governor handles parallel groups (dispatch all simultaneously, wait for all returns before proceeding)
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 021 — Protocol: governor-dispatch

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Dependencies:** block-017

## 1. Purpose

Create `protocols/governor-dispatch.md` — the step-by-step procedure the Governor follows to orchestrate a phase. Covers reading the phase parallel execution plan, dispatching task packets to sub-agents, collecting return packages, and deciding what to do next.

## 2. Files

- **Read:** design/governor-v2.md (Section 5), phases/phase-4.md (as example phase doc), _syntax.md
- **Modify:** none
- **Create:** protocols/governor-dispatch.md

## 3. Spec

`protocols/governor-dispatch.md` must cover:

### Governor dispatch lifecycle

**Step 1 — Phase intake**
- Read phase doc (phases/phase-N.md)
- Extract parallel execution plan (groups, dependencies, block IDs)
- Initialize governor-state.md with phase ID, group list, timestamp

**Step 2 — Group dispatch (per group)**
- For each block in the group:
  - Read block manifest
  - Generate convention snippet (per protocols/convention-snippet-generation.md)
  - Build task packet (per protocols/task-packet.md)
  - Dispatch sub-agent with task packet as first message

**Step 3 — Parallel group handling**
- Dispatch all blocks in a parallel group simultaneously (SDK parallelism)
- Do NOT proceed to next group until ALL blocks in current group return
- Collect all return packages

**Step 4 — Return validation**
- For each return package:
  - Parse status field
  - Validate gates (check `gates:` field)
  - If status:done and all gates pass → mark block done in governor-state.md
  - If status:blocked → follow governor-failure-handling.md
  - If status:scope-exceeded → log and continue (flagged for retro)

**Step 5 — State update**
- After each group: update STATE.md (phase progress), governor-state.md (orchestration state)
- After all groups: trigger phase close

**Step 6 — Phase close**
- All blocks done → emit phase retrospective summary
- Update STATE.md: phase status done

### governor-state.md structure
```
phase:phase-N gov:g-NNN ts:START status:in-progress
groups_done:4A
groups_pending:4B,4C
blocks_done:block-017
blocks_pending:block-018,block-019,...
protocols_hash:MD5HASH  # for convention snippet staleness check
```

## 4. Out of scope

- Failure handling logic (→ block-023 governor-failure-handling)
- Integration with Claude SDK code (→ Phase 5)
- Cross-phase dependency management
