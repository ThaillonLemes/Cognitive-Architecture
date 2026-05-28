# Protocol: Governor dispatch

BRIEF: Step-by-step procedure for the Governor to orchestrate a phase — reading the execution plan, dispatching task packets to sub-agents, collecting returns, and advancing to the next group.

Design authority: `design/governor-v2.md §6` (Governor orchestration lifecycle)

---

## Overview

Governor dispatch is event-driven (Decision 6). Governor runs when triggered; it is not a continuous process. Each invocation handles one or more parallel groups and updates project state before exiting.

Trigger sources: (a) user starts a phase, (b) a sub-agent's return arrives, (c) fallback timer fires.

---

## Dispatch lifecycle

### Step 1 — Phase intake

On first invocation for a phase:

```
1a. Read phases/phase-N.md → extract parallel_execution_plan
1b. Read STATE.md → confirm phase is active and no blocks are in wip state from a prior run
1c. Initialize governance/governor-state.md:
      phase:phase-N gov:g-<ID> ts:<now> status:in-progress
      groups_done:-
      groups_pending:<all group IDs in order>
      blocks_done:-
      blocks_pending:<all block IDs>
      protocols_hash:<sha256-first-8 of PROTOCOLS.md>
```

On subsequent invocations (resuming after a return or timer):
```
1a. Read governance/governor-state.md → identify current group and pending blocks
1b. Verify no state inconsistency with STATE.md
```

---

### Step 2 — Build and dispatch a parallel group

For each block in the current group (all at once for parallel groups):

```
2a. Read manifests/block-NNN-slug.md
2b. Generate convention snippet (protocols/convention-snippet-generation.md)
2c. Assemble task packet (protocols/task-packet.md):
      - header (all required fields)
      - convention snippet body
      - manifest (verbatim)
2d. Dispatch sub-agent via SDK (send task packet as first message)
2e. Record dispatch in governor-state.md:
      blocks_dispatched: block-NNN,block-NNN,...
2f. Update board.md per dispatched block:
      agent:<sub-agent-id> b:NNN group:<group> status:wip lock:in-progress ts:<now>
```

For parallel groups: steps 2a-2f run for ALL blocks in the group before waiting for any returns.

---

### Step 3 — Collect return packages

```
3a. Wait for all sub-agents in current group to emit return packages
3b. If fallback timer fires before all returns:
      - Mark timed-out blocks as status:failed in governor-state.md
      - Escalate per protocols/governor-failure-handling.md
      - Continue with blocks that did return
3c. Parse each return package:
      - Validate schema (required fields present)
      - Extract: b, status, gates, fmod, fread, scope_exp, issues, retro_path, tok_in, tok_out
```

---

### Step 4 — Validate returns

For each return package:

```
4a. Check status:
    - done     → proceed to integration
    - partial  → check gates: field; some failures may be acceptable
    - blocked  → escalate (protocols/governor-failure-handling.md)
    - scope-exceeded → log scope_exp; create follow-up block or expand manifest
    - needs-decision → surface to user; pause phase until decision

4b. Validate gates:
    - All gates:pass → block is integrable
    - Any gates:fail → treat as partial; apply failure protocol

4c. Update governor-state.md:
    - Move block from blocks_pending to blocks_done (or blocks_failed)
    - Record tok_in/tok_out for session totals
```

---

### Step 5 — Integrate and update state

After all blocks in a group are validated:

```
5a. Integrate (protocols/governor-integration.md):
    - Merge modified files to main
    - Verify no conflicts with parallel blocks (fmod: disjoint check)
5b. Write STATE.md: update last_block, blocks_done, next
5c. Append BLOCK_LOG.md: one line per completed block
5d. Update board.md: status:done for each completed block
5e. Commit (git add + git commit with block-NNN slug)
5f. Move to next group in governor-state.md:
    - groups_done: append current group
    - groups_pending: pop current group
```

---

### Step 6 — Advance or close phase

```
If groups_pending is not empty:
    → return to Step 2 with next group
If groups_pending is empty:
    → all blocks done
    → trigger phase close (commands/phase-close.md)
    → update governor-state.md: status:complete
    → update STATE.md: phase status done
```

---

## governor-state.md structure

Ephemeral; overwritten each Governor session. Lives at `governance/governor-state.md`.

```
phase:phase-N gov:g-ID ts:ISO8601 status:in-progress|complete|failed
groups_done:4A
groups_pending:4B,4C
blocks_done:block-017,block-018
blocks_dispatched:block-018,block-019,block-020
blocks_pending:block-021,block-022,block-023,block-024,block-025
blocks_failed:-
protocols_hash:abc12345
tok_session_in:0 tok_session_out:0
```

---

## Fallback timer

Governor sets a per-group deadline when dispatching. Default: `phase_estimated_duration_days × 0.2 × 24h` per group (rough estimate). Configurable via `deadline_ts:` in task packet header.

If timer fires before all returns: Governor escalates per `protocols/governor-failure-handling.md`.

---

## Manual fallback (governor_mode: manual)

When no SDK Governor:
1. User reads phase doc → identifies next group manually
2. User assembles task packet by hand (templates/task-packet.md)
3. User pastes packet into new Claude session
4. User reads return package from sub-agent session
5. User runs integration steps manually (commands/integrate.md)
6. User updates STATE.md, BLOCK_LOG.md, board.md manually

End of governor-dispatch protocol.
