---
id: block-005
status: done
tier: M
kind: refactor
opened_at: 2026-05-20
closed_at: 2026-05-20
duration_actual: <1h
---

# Block 005 — Retrospective

## What was built

Fixed 4 step-count errors discovered by reading all numbered protocol references:

| File | Error | Fix applied |
|------|-------|-------------|
| `protocols/block-retrospective-generation.md` line 10 | "step 4" — retrospective is block-close step 5 | → "step 5" |
| `protocols/parallelism.md` line 107 | "step 0 of block-close-checklist" — no step 0 exists; lock set in block-start | → "during block-start; see commands/block-start.md" |
| `CLAUDE.md` line 13 | "9-step flow" — RETROFIT.md has Steps 0–9 = 10 steps | → "10-step flow (Steps 0–9)" |
| `protocols/trigger-phrases.md` line 20 | same "9-step flow from Step 0" | → "10-step flow (Steps 0–9)" |

## Gates result

| Gate | Result | Notes |
|------|--------|-------|
| step-refs-verified | PASS | All 4 errors fixed; block-close-checklist confirmed at 8 steps; RETROFIT confirmed at 10 |
| files-updated (4 files) | PASS | All declared files changed |
| files-updated (STATE, NEXT, BLOCK_LOG) | PASS | Updated at block-close |

## Process notes

Discovered that RETROFIT.md has Steps 0–9 = 10 steps, contradicting the "9-step" label in CLAUDE.md and trigger-phrases.md. The step count of 10 is correct (Step 0 is the detect/greet step; Step 9 is the final checklist report).

The "step 0 of block-close-checklist" error in parallelism.md was misleading: lock:in-progress is set when a block starts (block-start command), not when a block closes. The block-close-checklist step 6 is where lock:ready is set at block end — that reference was correct.

## Next recommended

Phase 1 block-close complete. Phase close via `commands/phase-close.md`.
