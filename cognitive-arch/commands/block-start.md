# Command: block-start

Mode required: guardrails (start), then guidance (during implementation)

BRIEF: Protocol for starting a new block. Pre-flight checks, manifest validation, dependency confirmation, then proceed to implementation.

## Usage

User says: "start block <NNN>" or "follow block-start"

Or: it's invoked automatically after a previous block's `block-close.md` emits next-instruction.

## Pre-flight (guardrails)

### Step 1 — Identify the block
Read NEXT.md for the next block ID. Verify the manifest exists at `manifests/block-<NNN>-<slug>.md`.

If no manifest yet:
- Block is in `planned` state (declared in phase doc but no manifest)
- Generate manifest first per `protocols/manifest-{small,medium,large}-generation.md`
- Then return to this command

### Step 2 — Verify dependencies
Read manifest's `dependencies:` field. For each dep:
- Find it in BLOCK_LOG.md
- Verify it has line `<dep-id> integrated <hash> <ts>` (or `done` for non-multi-agent setups)

If any dep is not integrated:
- HALT
- Output: "Waiting for <dep-id> to be integrated. Cannot start block-<NNN> yet."
- Tell user to wait until governor integrates the dep

### Step 3 — Verify board.md
Read your agent's row in board.md. Confirm:
- `status:idle` (you're not already in a block)
- No conflict with other in-progress agents (files.modify disjoint)

If you're already in a block per board.md:
- HALT
- Output: "Already working on block-<X>. Close it first via block-close."

### Step 4 — Rebase worktree (multi-agent only)
If you have a worktree:
```bash
cd <worktree>
git checkout <branch>
git rebase main
```

This pulls in dependency changes integrated since you last worked.

If rebase has conflicts: HALT, ask user.

### Step 5 — Update board.md
Write your row in board.md:
```
agent:<id> b:<NNN> group:<group> status:wip lock:in-progress deps:<list> ts:<now>
```

This signals to Governor and other agents that you're now busy.

## During implementation (guidance mode)

Switch to guidance mode after pre-flight passes.

### Step 6 — Read context + assign tier
Read in order:
1. Block manifest (you have it from step 1)
2. Files in manifest's `files.read` list
3. Relevant design/ docs if mentioned
4. Phase doc (for context on what this block contributes to)

Before implementing, confirm the block's tier using `protocols/block-complexity-estimator.md`. If the block is M or L, the full SPARC execution protocol is mandatory (see Step 6b).

### Step 6b — SPARC execution protocol (M/L mandatory, S recommended)

Follow `protocols/block-execution-sparc.md` for the 5-phase execution sequence:
- **S — Specification:** re-read manifest, inspect read files, write 3-line plan.
- **P — Pseudocode:** outline logic before writing code or prose.
- **A — Architecture:** verify consistency with existing modules and protocols.
- **R — Refinement:** implement; run gates as you go.
- **C — Completion:** all gates pass → write retro → update state files.

For S-tier blocks: at minimum complete Phase S (Specification) and Phase C (Completion).

### Step 7 — Implement
Write code per manifest's `files.modify` and `files.create`.

Apply Axiom Q6 (Files exhaustively declared): if you discover you need to modify a file NOT in `files.modify`, halt and update the manifest first.

Apply Axiom Q1 (Rule of Three for new abstractions): document any new abstraction in manifest §8.

Apply `protocols/code-header-protocol.md`: every code file you create or modify gets the standard header.

### Step 8 — Intermediate validation
As you go:
- Run unit tests for new functions (don't wait until the end)
- Run lint frequently
- Commit at logical stopping points within the block (but don't commit the FINAL state yet — that's block-close)

### Step 9 — Ready for close
When implementation feels done:
- Switch to checklist mode
- Follow `commands/block-close.md`

## Failure modes

- Dependency not yet integrated → HALT, wait
- File conflict with other agent → HALT, ask user to resolve
- Tests fail mid-implementation → debug; if stuck, ask user for guidance
- Scope creep (file you need not in manifest) → HALT, update manifest

## Cost

Pre-flight: ~1K-2K tokens.
Implementation: variable (the actual block work).

End of block-start command.
