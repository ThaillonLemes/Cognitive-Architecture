# Block Execution Protocol — SPARC

BRIEF: 5-phase execution sequence for use within each block. Mandatory for M and L tier blocks. Recommended for S tier. Prevents "jump-straight-to-code" errors by enforcing Specification before implementation and measurement before close.

**Tier applicability:**

| Tier | SPARC requirement |
|------|------------------|
| S | Recommended — skip P if trivial, always do S and C |
| M | Mandatory — all 5 phases |
| L | Mandatory — all 5 phases; document A phase in a comment in the modified file |

---

## Phase S — Specification

**Entry condition:** Block manifest has been read in full.

**Actions:**
1. Re-read the manifest's Purpose section. Confirm you understand the single deliverable.
2. List every file to be read, modified, or created (from manifest `files:` section).
3. Re-read all `files.read` entries. Do not skip this — unknown file state is the #1 source of block failure.
4. Write a 3-line plan in a scratch comment or internal note:
   - Line 1: What I will create/change.
   - Line 2: What the output will look like (file, function, section).
   - Line 3: How I will verify it worked (which gate, which grep, which test).
5. If the plan contradicts the manifest or is unclear: HALT. Re-read the manifest and clarify before proceeding.

**Exit condition:** 3-line plan written. All read files inspected. No unresolved ambiguity.

---

## Phase P — Pseudocode / Plan

**Entry condition:** Specification phase complete.

**Actions (for implementation blocks):**
1. Write the logic in comments or pseudocode before touching any file.
2. For protocol files: outline the sections and their key content before writing prose.
3. For SDK/code files: write function signatures and docstrings before body.
4. Identify: what could go wrong? What edge cases does the manifest not cover? Add a note.

**Skip condition:** For purely additive S-tier documentation blocks (creating a new markdown file from a fully specified manifest), Phase P may be skipped. Mark it: `[P: skipped — pure content block]`.

**Exit condition:** Outline or pseudocode exists. Edge cases noted.

---

## Phase A — Architecture

**Entry condition:** Pseudocode / plan phase complete.

**Actions:**
1. Verify the approach is consistent with existing modules. Read headers of related files if needed.
2. Confirm no naming conflicts with existing functions, files, or protocols.
3. For SDK changes: confirm the change does not break existing public APIs.
4. For protocol files: confirm the protocol does not duplicate or contradict an existing protocol.
5. If inconsistency found: HALT. Resolve before proceeding (either adjust the approach or note the intentional deviation with rationale).

**Exit condition:** Approach confirmed consistent. No naming conflicts. No API breaks.

---

## Phase R — Refinement

**Entry condition:** Architecture phase complete.

**Actions:**
1. Implement. Write the actual files, code, or content.
2. After each significant write, run a quick self-check: does this match the Specification plan?
3. Run gates as you go — do not wait until Phase C to discover gate failures.
4. If a gate fails: diagnose, fix, re-run. Do not proceed to Phase C with a failing gate.
5. If implementation reveals the Specification was wrong: go back to Phase S and revise. Do not silently drift.

**Exit condition:** All files created/modified. All gates passing locally.

---

## Phase C — Completion

**Entry condition:** All gates pass.

**Actions:**
1. Run all gates listed in the manifest. Record results.
2. Write the block retrospective to `blocks/block-NNN-retro.md` using `templates/block-retrospective.md`.
3. Update the manifest status to `done`.
4. Update `STATE.md`: `last_block:block-NNN last_block_status:done next:block-NNN+1`.
5. Update `NEXT.md`: pointer to next block.
6. Append to `blocks/BLOCK_LOG.md`: `block-NNN done YYYY-MM-DD`.
7. Update `board.md` if multi-agent: mark block done, update agent status.

**Exit condition:** All state files updated. Retrospective written. Block closed.

---

## SPARC Checklist (paste into retro or scratch)

```
S — Specification
  [ ] Manifest re-read in full
  [ ] All read files inspected
  [ ] 3-line plan written

P — Pseudocode
  [ ] Outline/pseudocode written  OR  [skipped — pure content block]

A — Architecture
  [ ] Consistency verified
  [ ] No naming conflicts
  [ ] No API breaks

R — Refinement
  [ ] Implementation complete
  [ ] Gates checked during implementation
  [ ] No silent drift from Specification

C — Completion
  [ ] All gates pass
  [ ] Retrospective written
  [ ] STATE.md, NEXT.md, BLOCK_LOG updated
```

---

## Out of scope

- Applying SPARC to Track Blocks (Track Blocks use `protocols/track-block-execution.md`).
- Enforcing SPARC via automated tooling (that is a future phase).
- Using SPARC for Phase-level work (Phases use `commands/phase-start.md`).

End of block-execution-sparc.md.
