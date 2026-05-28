# Command: phase-close

Mode required: checklist

BRIEF: Close a phase when all blocks are integrated and exit criteria are met. Write phase retrospective. Update tracking.

## Usage

- Auto-triggered after `commands/integrate.md` integrates last block of phase
- Manual: "close phase <N>" or "follow phase-close"

## Pre-flight (checklist mode)

### Step 1 — Verify all blocks integrated
Read phase doc §8 Block Index. For each block:
- Status must be `integrated` in BLOCK_LOG.md

If any block not integrated: HALT, report what's outstanding.

### Step 2 — Verify exit criteria against Phase Quality Rubric
Read phase doc §7 Exit Criteria. For each criterion:
- Manually check (per checklist mode): is it met?
- Cite evidence (file path, log, test result, ADR)

Cross-check against `protocols/phase-quality-rubric.md` criterion 2: each exit criterion must be verifiable. If a criterion was accepted as vague during phase-start, flag it in the phase retrospective.

If any criterion not met: HALT. Options:
- [a] Defer to future phase (update §10 Out of Scope + retro)
- [b] Add a block to address (block goes to manifests/, phase stays open until done)
- [c] Document as known limitation and proceed anyway (user authority)

### Step 3 — Verify all gates
Quick sanity: run `./audit.sh`. Should be pass or pass-with-warnings.

## Close steps

### Step 4 — Write phase retrospective
Per `protocols/phase-retrospective-generation.md`:
- Read all block retrospectives for this phase (`blocks/block-*.md` from this phase's IDs)
- Aggregate data
- Fill `templates/phase-retrospective.md`
- Save to `phases/phase-<N>-retro.md`

### Step 5 — Archive manifests
For each block in this phase:
- Move manifest: `manifests/block-<NNN>-<slug>.md` → `manifests/_archive/block-<NNN>-<slug>.md`
- (Already archived during integrate? Then no-op for those)

### Step 6 — Update phase doc
Update phase doc YAML frontmatter: `status: complete`, `last_updated: <today>`

### Step 7 — Update HOT files
- STATE.md: `p:<N+1> status:planned` (or `complete` if final phase)
- NEXT.md: pointer to phase-<N+1> first block, OR to project-complete state
- INDEX.md: update phase brief; add phase retro brief

### Step 8 — Commit
```bash
git add phases/phase-<N>.md phases/phase-<N>-retro.md
git add manifests/_archive/
git rm manifests/block-*.md     # remove those moved to archive
git add STATE.md NEXT.md INDEX.md
git commit -m "Close phase <N>: <name>"
```

### Step 9 — Trigger audit
Run `commands/audit.md` to verify post-close state is clean.

### Step 10 — Notify user
Output:
```
✓ Phase <N> closed.
  Blocks integrated: <count>
  Exit criteria met: N/M
  Phase retrospective: phases/phase-<N>-retro.md
  Next: phase-<N+1> (or project complete)
```

If no next phase planned:
```
✓ Phase <N> closed. No next phase planned.
  Consider: planning phase-<N+1>, marking project complete, or shipping current state.
```

## Failure modes

- Exit criteria not met → don't close; address the gap first
- Audit fails → don't close; fix issues first
- Manifests not properly archived → check integrate completeness

NEVER close a phase with unresolved blocks.

## Cost

~5K-8K tokens (retrospective synthesis + audit + commits).

End of phase-close command.
