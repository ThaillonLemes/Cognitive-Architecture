# Command: integrate

Mode required: checklist

BRIEF: Governor command. Merges completed worktree branches into main. Atomic per worktree. Refuses partial merges.

## Usage

- Manual: "follow commands/integrate.md" (Governor session only)
- Triggered when board.md shows agents with `status:done lock:ready`

## Pre-flight (guardrails before checklist)

Before any integration, verify:

1. Current branch is `main` (not a worktree branch)
2. Working tree is clean (no uncommitted local changes)
3. `audit.sh` passes (no critical errors)
4. board.md shows at least 1 agent with `status:done lock:ready`

If any pre-flight fails: HALT. Report to user.

## Integration loop

For each agent with `status:done lock:ready` in board.md:

### Step 1 — Identify the block
- Read agent's row in board.md: agent ID, block ID, worktree path, branch name
- Read the block's manifest from `manifests/block-<NNN>-<slug>.md`
- Read the agent's block retrospective from `blocks/block-<NNN>-<slug>.md`

### Step 2 — Validate gates
Re-verify gates from manifest:
- `tests-pass`, `lint-pass`, `build-pass`, `files-updated`, `dependencies-met`, plus any custom gates
- If any gate is `forced`: check rationale is present in retrospective
- ERROR if any gate is `failed` without explicit force

### Step 3 — Validate file conflicts
- For each agent currently `wip` in board.md: check `files.modify` intersection with this block's `files.modify`
- ERROR if conflict (the wip agent could be working on a file this integration will touch)
- Resolution: ask user to (a) wait for wip agent to finish, (b) integrate anyway with conflict flagged

### Step 4 — Validate dependencies
- All deps in manifest `dependencies:` must be `integrated` in BLOCK_LOG.md
- ERROR if any dep is not integrated

### Step 5 — Merge
```bash
cd <worktree-path>
git checkout <branch>
git rebase main                   # rebase against latest main (catches conflicts early)
git checkout main
git merge --no-ff <branch> -m "Integrate <block-id>: <slug>"
```

If rebase or merge conflicts arise:
- HALT
- Notify user
- DO NOT auto-resolve

### Step 6 — Archive manifest
```bash
mv manifests/block-<NNN>-<slug>.md manifests/_archive/block-<NNN>-<slug>.md
```

Commit:
```bash
git add manifests/_archive/block-<NNN>-<slug>.md
git rm manifests/block-<NNN>-<slug>.md
git commit -m "Archive manifest block-<NNN>"
```

### Step 7 — Update tracking files
- Append BLOCK_LOG.md: `<id> integrated <main-commit-hash> <ts>`
- Update board.md: `agent:<id> ... status:integrated`
- Update STATE.md: `last_integrated:<id> <ts>`

Commit:
```bash
git add BLOCK_LOG.md board.md STATE.md
git commit -m "Track integration of block-<NNN>"
```

### Step 8 — Notify
Output to user:
```
✓ block-<NNN> integrated. main is now at <commit-hash>.
  Files touched: <count>
  Tests: pass
```

Move to next agent in board.md until all `done+ready` are processed.

## After integration loop

### Step 9 — Post-integration audit
Run `commands/audit.md` after all integrations. Report drift.

### Step 10 — Check for phase close
- If all blocks in current phase are `integrated`:
  - Trigger `commands/phase-close.md`

### Step 11 — Notify agents
For each agent waiting on integration of one of the just-merged blocks:
- Their `deps` are now satisfied
- They can proceed (user will paste next-instruction in their session)

## Failure modes

- Conflict during rebase → halt, report
- Gate not actually passing on re-check → halt; reopen the block
- Disk full / git error → halt; investigate

NEVER force-merge. NEVER skip gate validation.

## Cost

Per integration: ~5K-10K tokens (manifest read + retrospective + audit + git ops feedback).

End of integrate command.
