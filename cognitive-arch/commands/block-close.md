# Command: block-close

Mode required: checklist

BRIEF: Strict 8-step closing protocol. Per `protocols/block-close-checklist.md`. No deviation, no shortcuts.

## Usage

- User says: "close block" or "follow block-close"
- Auto-triggered when implementation feels done in block-start step 9

## Reference

This command is THIN. The real protocol is at `protocols/block-close-checklist.md`. Read that.

## Quick reference

```
1. validate_gates       (run all gates; HALT on any fail unless forced)
2. write_state          (update STATE.md per _syntax.md)
3. write_next           (point NEXT.md to next block or phase-close)
4. append_block_log     (one line in BLOCK_LOG.md)
5. write_retrospective  (blocks/block-NNN-<slug>.md per template)
6. update_board         (your row in board.md → status:done lock:ready)
7. commit               (git commit with standardized message; do NOT push)
8. emit_next_instruction (self-contained block for user to paste after /clear)
```

After step 8, run `./audit.sh` (optional but recommended) to verify.

## Retrospective quality check (Phase 8+)

Before writing the retrospective (step 5), run the semantic rubric from `protocols/retrospective-rubric.md`:
- Call `validate_rubric(retro_text, tok_in, tok_out)` in `sdk/return_validator.py`, or manually verify the 5 criteria.
- Record any `[RUBRIC WARNING]` lines at the bottom of the retrospective under `## Rubric Warnings`.
- Warnings are advisory — they do not block close. 3+ warnings = consider expanding the retro.

## Mode discipline

Stay in CHECKLIST mode throughout. Do not speculate. Do not narrate. Output structured.

## Gate failure handling

If step 1 reveals a failed gate:
- HALT immediately
- Output to user:
  ```
  Gate <name> failed.
  Evidence: <command output snippet>
  Options:
  [a] retry with better technique
  [b] revise manifest (e.g., relax threshold) and try again
  [c] force-pass with rationale (creates audit record)
  ```
- Await user decision
- Do NOT proceed to steps 2-8 until resolved

## Commit message format

Subject (≤ 70 chars):
```
block-<NNN>: <slug> — <one-line-summary>
```

Body (optional):
```
- <built thing 1>
- <built thing 2>
- <gate result>
```

## Emit next-instruction format

```
═══ BLOCK CLOSE ═══
agent: <your-id>
block: <NNN> done
gates: N/M pass
files: <count> modified, <count> created
status: ready | blocked | needs_decision

═══ PASTE AFTER /clear ═══
You are agent <id>. Read AGENT.md. Start block <next-id>.
Follow commands/block-start.md.
```

If blocked on dep:
```
═══ PASTE WHEN UNBLOCKED ═══
(wait for governor to integrate <dep-id>. board.md will show <dep-id>=done.
Then paste: "You are agent <id>. Read AGENT.md. Start block <next-id>.")
```

## Cost

~3K-5K tokens (gate validation + writes + commit).

End of block-close command.
