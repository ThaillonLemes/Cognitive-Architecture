---
id: block-004
status: done
tier: S
kind: refactor
opened_at: 2026-05-20
closed_at: 2026-05-20
duration_actual: <1h
---

# Block 004 — Retrospective

## What was built

Resolved the mismatch between `audit.sh` (5 labeled checks) and `commands/audit.md` (8 declared checks) by documenting the script/Governor split explicitly in both files.

**audit.sh (rewrite):**
- Check labels updated from [1/5]–[5/5] to [1/8]–[4/8]
- Bootstrap state check folded into check 4 as sub-check 4b
- [5-8/8] Governor-only note added listing all 4 Governor checks with explanations
- Summary line updated to read "script checks 1–4 of 8"
- Header comment updated to explain the architecture of the split

**commands/audit.md (targeted edits):**
- Added coverage table after "Run 8 audit checks in order:" (checks 1–4 = script, 5–8 = Governor)
- Each check heading annotated: "(script)", "(script, partial)", or "(Governor-only)"

## Gates result

| Gate | Result | Notes |
|------|--------|-------|
| labels-consistent | PASS | audit.sh reads [1/8]–[4/8]; Governor-only note present |
| files-updated (audit.sh, commands/audit.md) | PASS | Both files modified |
| files-updated (STATE, NEXT, BLOCK_LOG) | PASS | Updated at block-close |

## Process notes

Strategy chosen: document the split, do not implement checks 5–8 in bash. Rationale: manifest schema validation, dep-graph, file-conflict, and drift detection all require reading and reasoning over multiple files simultaneously — this is LLM work, not bash work. The split is now explicit and honest in both files.

Discovered: the bootstrap state check in the old [5/5] slot was a sub-check of check 4 (AI-only file format), not a separate 5th check vs the 8-check list. Folded accordingly.

## Next recommended

Phase 1 block-close complete. Phase close via `commands/phase-close.md`.
