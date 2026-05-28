---
protection: immutable
protection_reason: "8-step block close protocol. Changes here alter core audit-checkable workflow and agent coordination."
restore_command: "git checkout HEAD -- protocols/block-close-checklist.md"
---

# Protocol: Block close checklist

BRIEF: The EXACT 8-step protocol every agent follows at the end of every block. No deviation. Triggered by `commands/block-close.md`.

## Governor v2 ownership note

> In **Governor v2 mode** (`governor_mode:sdk`), steps are split between sub-agent and Governor as annotated below. In **manual mode** (`governor_mode:manual`), the implementing AI performs all steps. Annotations are additive — no step content changes.

## Mode

**checklist** — strict yes/no. Do not skip steps. Do not reorder.

## The 8 steps

```
on:block_close
seq:
  1. validate_gates       run all gates in manifest, verify pass
  2. write_state          update STATE.md with new phase/block/tip
  3. write_next           update NEXT.md with pointer to next block
  4. append_block_log     append one line to BLOCK_LOG.md
  5. write_retrospective  write blocks/block-NNN-slug.md
  6. update_board         update agent's row in board.md
  7. commit               git add files; git commit with standardized message
  8. emit_next_instruction print self-contained next-block prompt
verify:audit.sh --block-close
```

## Step details

### Step 1 — validate_gates
**Owner (Governor v2): sub-agent**

For each gate in manifest `gates:` array:
- Run the gate's command (if `type:cmd`) and check expected output
- Or verify file state (if `type:file-changed`, `type:deps-complete`, etc.)
- Output: pass/fail per gate

If any gate fails:
- HALT step 1
- Do NOT proceed to step 2
- Tell user: "Gate <name> failed. Output: <evidence>. Want to (a) retry with better technique, (b) revise manifest, (c) force-pass?"
- Await user decision

If all gates pass: proceed to step 2.

### Security Gate (conditional — between steps 1 and 2)
**Owner (Governor v2): sub-agent (manual mode) / Governor (SDK mode)**

If the block's manifest has `security: true`:

1. Run `commands/security-review.md` against this block before proceeding.
2. Record the result (PASS / WARN / FAIL) in the block's retrospective notes using the format specified in the command.
3. **A FAIL result prevents block close.** Resolve all FAIL findings, re-run the full security review, and achieve a PASS or acknowledged WARN before continuing.
4. A WARN result allows block close **only if** all warnings are explicitly acknowledged in writing with a named owner and acceptance rationale in the retrospective.
5. A PASS result requires no additional action — proceed to step 2.

If the block's manifest has `security: false`: skip this step entirely and proceed to step 2.

**Reference:** `commands/security-review.md` — `protocols/stack-addenda/security.md` — axiom S5 in `PROTOCOLS.md`

---

### Step 2 — write_state
**Owner (Governor v2): Governor**

Update STATE.md with new state. Use compact AI-only format from `_syntax.md`. Example:

```
p:<phase> b:<block> status:done next:<next-block> wt:<worktree> tip:<commit-hash> gates:N/M last_updated:<ts>
```

### Step 3 — write_next
**Owner (Governor v2): Governor**

Update NEXT.md to point to next block:
- If next block in same phase: `manifest:manifests/block-<next>-<slug>.md`
- If phase complete: `manifest:phase-close` (triggers commands/phase-close.md)
- If no next planned: `manifest:none next_action:plan_next_phase`

### Step 4 — append_block_log
**Owner (Governor v2): Governor**

Append ONE line to `blocks/BLOCK_LOG.md`:

```
<block-id> done <commit-hash> <ts>
```

Do NOT reformat or re-order existing lines.

### Step 5 — write_retrospective
**Owner (Governor v2): sub-agent**

Before writing, record `actual_duration_hours`:
- Check git log for approximate start/end timestamps of files in this block's scope → set `duration_source: auto-inferred`
- Or enter the time manually if you tracked it → set `duration_source: manual`
- If unknown, estimate based on block tier (S≈1h, M≈2-4h, L≈6-8h) → set `duration_source: estimated`

Generate the block retrospective per `protocols/block-retrospective-generation.md`. Save to `blocks/block-<NNN>-<slug>.md`.

### Step 6 — update_board
**Owner (Governor v2): Governor**

Update YOUR row in `board.md`:

```
agent:<id> b:<block> group:<group> status:done lock:ready ts:<ts>
```

If multi-agent: governor will read this to know you're ready for integration.

### Step 7 — commit
**Owner (Governor v2): Governor** (sub-agent in manual mode; Governor in SDK mode per `protocols/governor-integration.md`)

Stage and commit changes:

```bash
git add manifests/block-<NNN>-<slug>.md
git add blocks/block-<NNN>-<slug>.md
git add blocks/BLOCK_LOG.md
git add STATE.md
git add NEXT.md
git add board.md
# Plus all files declared in manifest's files.modify and files.create
git commit -m "block-<NNN>: <slug> — <one-line-summary>"
```

Commit message format:
- Subject: `block-<NNN>: <slug> — <summary>` (≤ 70 chars)
- Body (optional): bullet list of what was built (from retrospective §1)

DO NOT push automatically. Pushing is user authority.

### Step 8 — emit_next_instruction
**Owner (Governor v2): Governor**

Output a self-contained block the user copies after `/clear`. Format:

```
═══ BLOCK CLOSE ═══
agent: <your-id>
block: <NNN> done
gates: <N>/<M> pass
files: <count> modified, <count> created
status: <ready | blocked | needs_decision>

═══ PASTE AFTER /clear ═══
You are agent <id>. Read AGENT.md. Start block <next-id>.
Follow commands/block-start.md.
```

If next block is blocked on dependency:
```
═══ PASTE WHEN UNBLOCKED ═══
(wait for governor to integrate <dep-id>. board.md will show <dep-id>=done.
Then paste: "You are agent <id>. Read AGENT.md. Start block <next-id>.")
```

If user decision needed (gate failure unresolved):
```
═══ USER DECISION REQUIRED ═══
[a] retry with better technique
[b] revise manifest and try again
[c] force-pass with rationale
```

## Layer Check

Which memory layer(s) did this block update? Check before committing.

- [ ] **AX only** (normal block close — no architecture or product changes): proceed to commit.
- [ ] **DX updated** (protocols/, design/, sdk/, or templates/ changed): verify the modified DX file accurately reflects the new architecture. Add a note in the retro: "DX updated: `<filename>`."
- [ ] **UX updated** (PROJECT.md, phase-0/, or decisions/ changed): confirm a decision record exists in `decisions/` explaining the change. This is unusual — if unexpected, pause and verify the change was intentional.

Reference: `protocols/project-memory-layers.md`

---

## Final verification

After step 8, run (or invite user to run): `./audit.sh`

Audit should report: PASS or PASS WITH WARNINGS. If FAIL, something in the 8 steps was missed.

## What can go wrong (and what to do)

- Gate command fails to find binary → check PROJECT.md commands; ask user
- File not modified that should be → review manifest scope; possibly add to manifest as discovered
- Tests fail → halt; do not commit; ask user (per step 1 fail flow)
- Worktree dirty unexpectedly → halt; ask user to review uncommitted changes

## Why the rigor

Without this checklist, agents drift:
- STATE.md goes stale
- BLOCK_LOG.md becomes incomplete
- Board.md misleads Governor
- Audit catches issues late instead of early

The 8 steps are the SHORTEST PATH to a clean block close. Do not skip.

End of block-close-checklist.
