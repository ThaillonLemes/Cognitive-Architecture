# Protocol: Parallelism

BRIEF: Rules for identifying parallel work, spawning multiple agents, and synchronizing via Governor. Read when generating a phase doc OR when starting multi-agent execution.

## Identifying parallel opportunities

Two blocks A and B can run in parallel IFF ALL:

1. **No dependency:** A is not in B's `dependencies:` (and transitively) and vice versa.
2. **Disjoint files:** `A.files.modify ∩ B.files.modify = ∅`. Same applies to `files.create`.
3. **No shared external resource:** no shared database table being migrated, no shared config file being rewritten, no shared external service contract change.

If those hold: A and B can be in the same parallel group.

## Phase design rules

**Decision 10 from `design/governor-v2.md`:** Maximize intra-phase parallelism. Cross-phase parallelism is out of scope (deferred to v3.0+).

### Intra-phase only

All parallelism machinery (board.md, governor-state.md, dep-graph checks) is designed for blocks within a single phase. Do NOT attempt to run blocks from different phases simultaneously — state management is not designed for cross-phase parallelism.

Cross-phase parallelism deferred to v3.0+. Reason: distributed state management across phases adds complexity that exceeds the benefit for the current architecture.

### Instead — merge themes

If two independent work themes have no file conflicts, merge them into one larger phase with separate parallel groups. Both themes execute in parallel within the merged phase; no cross-phase machinery required.

```
Before (cross-phase attempt): Phase A ║ Phase B → complex Governor logic
After (merged phase):         Phase A+B with parallel groups 1A, 1B → existing mechanism
```

### Phase design decision tree

```
New work theme to add?
├── Conflicts with blocks in an upcoming phase? → separate phase (sequential)
├── Depends on an upcoming phase? → separate phase after that phase
└── Fully independent (no file conflicts)?
    └── Already planned phases are close? → merge into next phase as new parallel group
    └── Phases are far off? → new independent phase
```

### Maximizing intra-phase parallelism

When designing a phase:
1. List all blocks; build dep DAG
2. Check `files.modify` overlap between non-dep blocks
3. Group non-overlapping, non-dep blocks into a single parallel group
4. Sequential chains (A→B→C) become sequential groups (3A, 3B, 3C)
5. Independent chains run in parallel within the same phase

Goal: maximize the number of blocks that can dispatch simultaneously.

---

## parallel_execution_plan YAML format

Every phase doc §9 uses this format:

```yaml
parallel_execution_plan:
  total_blocks: N
  recommended_agents: N          # = max width of any single parallel group
  groups:
    - id: PHASE-LETTER           # e.g., 4A, 4B, 4C (phase number + letter)
      blocks: [block-NNN, ...]   # list of block IDs in this group
      type: sequential|parallel  # sequential = single block; parallel = can dispatch together
      depends_on: []             # group IDs this group depends on (must complete first)
      note: human description
```

**Group execution rules:**
- `parallel` groups: all blocks dispatch simultaneously; Governor waits for ALL returns
- `sequential` groups: single block; listed as a group for structural uniformity
- A group does not start until all groups in its `depends_on:` list are `done`
- `recommended_agents` = max `len(blocks)` across all parallel groups

**File conflict check (before dispatch):**
Two blocks in the same parallel group must NOT share any path in their `fmod:` lists.
Governor validates this before dispatch. Conflict → re-sequence blocks or split into separate groups.

---

## Parallel group identification (during phase generation)

When generating `phases/phase-<N>.md`:

1. List all blocks for the phase.
2. Build the dependency DAG from each block's `dependencies:`.
3. Compute topological order.
4. Group blocks that are at the same depth AND have disjoint `files.modify`.
5. Output as `parallel_execution_plan` in phase doc §9.

Example:
- Phase has 10 blocks: 21, 22, 23, 24, 25, 26, 27, 28, 29, 30
- Deps: 22→21, 23→21, 24→22, 25→22, 26→23, 27→24+25, 28→26, 29→27+28, 30→29
- Disjoint check: 22 and 23 modify different files? Yes. 24 and 25? Yes. 26 and ??? etc.
- Groups:
  - 1a: [21] depends on []
  - 1b: [22, 23] depends on [1a] (parallel within group)
  - 1c: [24, 25] depends on [1b]
  - 1d: [26] depends on [1b]
  - 1e: [27] depends on [1c]
  - 1f: [28] depends on [1d]
  - 1g: [29] depends on [1e, 1f]
  - 1h: [30] depends on [1g]

`recommended_agents` = max parallel width = 2 (groups 1b, 1c each have 2 blocks).

## Spawning agents

Once parallel groups are identified:

1. User asks Governor: "Spawn agents for phase-<N>."
2. Governor reads phase doc parallel_execution_plan.
3. Governor generates AGENT.md per group:
   - `agents/agent-1a.md` — assigned to group 1a (block 21)
   - `agents/agent-1b.md` — assigned to group 1b (blocks 22-23)
   - ... etc.
4. Governor outputs boot prompts for the user to paste into new Claude Code sessions.
5. User opens N tabs (one per parallel group's width), pastes boot prompt, agent identifies via AGENT.md.

## Worktree assignment

Each agent gets its own git worktree:
- Group 1a → worktree at `.claude/worktrees/1a/`
- Group 1b → worktree at `.claude/worktrees/1b/`
- ...

This isolates work; agents commit to their own branch (`claude/1a`, `claude/1b`, ...).

If your project doesn't use worktrees: agents can work in a shared directory but with strict locking via board.md (slower, harder to merge).

## Synchronization (sync points)

A sync point occurs when a group's blocks are all `done` and Governor integrates them to main.

Sync point flow:
1. Agent finishes its block per `protocols/block-close-checklist.md`.
2. Agent updates `board.md`: `status:done lock:ready`.
3. User (or Governor) reviews board.md; if all blocks in a group are `done`, triggers integrate.
4. Governor runs `commands/integrate.md` for each `done` worktree:
   a. Verify gates passed
   b. Verify no file conflict with other in-progress agents
   c. Merge worktree branch → main
   d. Update board.md: `status:integrated`
   e. Archive manifest
5. Once group is integrated, dependent groups can start.

## Dependency check at block start

Before any agent starts a block:
1. Agent reads `board.md` to check that all blocks in its `dependencies:` are `status:integrated` (not just `done`).
2. If any dep is not integrated, agent halts: "Waiting on <block-id> to be integrated."
3. Once dep integrated, agent rebases its worktree from main (to pull in dep's changes):
   ```bash
   git checkout <my-branch>
   git rebase main
   ```
4. Then agent starts the block.

This prevents agents from working off stale base.

## File conflict prevention

Audit detects file conflicts BEFORE work starts:
- Audit reads all `manifests/*.md` with status `pending` or `wip`.
- For each pair, checks `files.modify ∩ files.modify`.
- If non-empty: audit ERROR. Halt; resolve before any block in the conflict starts.

This prevents merge hell after parallel work.

## Lock mechanism

Each agent writes a lock to `board.md`:
- `lock:in-progress` when block starts (set during block-start; see `commands/block-start.md`)
- `lock:ready` at step 6 of block-close-checklist

Governor only integrates `lock:ready` rows.

If `lock:in-progress` has not progressed in > 1 hour (no board.md update from that agent), audit flags as stale lock. Governor asks user: "Agent <id> seems stuck. Reset, retry, or ignore?"

## Multi-agent UX

Optimal user UX for multi-agent work:

1. Open one Governor session (always-on tab; manual trigger for actions in v1).
2. Open N implementer sessions (one per parallel group).
3. Each implementer session has AGENT.md → auto-identifies.
4. User starts blocks: paste block-start prompt into each session.
5. As blocks close, agents emit next-instruction blocks.
6. User: `/clear` + paste next-instruction → next block.
7. Periodically: switch to Governor session, paste `integrate.md` command → integrate ready agents.
8. Resume implementer sessions for next round.

Worst case overhead per block: paste-clear-paste. ~30 seconds.

## When NOT to parallelize

Sometimes serial is better:
- Project is small (< 5 blocks per phase) — overhead exceeds gain
- Blocks share too much code (lots of `files.modify` overlap)
- User is solo and managing N sessions is more burden than gain
- Stack doesn't support clean worktree isolation (rare)

Default to serial for projects starting out. Parallelize when the phase has clear independent paths.

## Governor v2 automation (Phase 5)

Governor v2 (SDK-based) automates parallel dispatch and integration. Design: `design/governor-v2.md`.

- Automated agent spawn via Claude Agent SDK (`protocols/governor-dispatch.md`)
- Parallel block dispatch within groups (no user tab-management)
- Automated return collection and gate validation
- Auto-integrate at sync points (`protocols/governor-integration.md`)

**Cross-phase parallelism:** deferred to v3.0+. Not in Governor v2 scope. See `_future/multi-repo.md` for context.

End of parallelism protocol.
