---
id: block-002
status: done
tier: S
kind: refactor
opened_at: 2026-05-20
closed_at: 2026-05-20
duration_actual: <1h
---

# Block 002 — Retrospective

## What was built

Brought `CLAUDE.md` within Q2 size budget (Q2 = ≤60 lines):

- **Before:** 108 lines (80% over budget)
- **After:** 58 lines (3% under budget)

Strategy: extracted the trigger-phrase tables and detection-marker list into a new protocol file `protocols/trigger-phrases.md`. `CLAUDE.md` now holds a condensed routing summary (4-row table) + pointer to the protocol for the full phrase list.

## Gates result

| Gate | Result | Notes |
|------|--------|-------|
| lines-budget (CLAUDE.md ≤ 60) | PASS | 58 lines |
| files-updated (CLAUDE.md) | PASS | Full rewrite — slim version |
| files-updated (protocols/trigger-phrases.md) | PASS | Created with full extracted content |
| files-updated (STATE.md) | PASS | Updated at block-close |
| files-updated (NEXT.md) | PASS | Updated at block-close |
| files-updated (BLOCK_LOG.md) | PASS | Entry appended |

## Process notes

Second block under ADR-001 (Option A, dogfood-total). Overhead same as block-001: 4 artifacts for a single-file refactor. Acceptable.

The refactor preserves all routing behavior: trigger phrases are still reachable via CLAUDE.md → protocols/trigger-phrases.md. No information was deleted; it was relocated.

`INDEX.md` Briefs section does not yet reference `protocols/trigger-phrases.md`. Added to scope of block-005 (step-count/sweep pass) rather than expanding this block beyond Tier S.

## Next recommended

`block-003` — Disambiguate "Charter" vs "Comment Charter" naming. Currently 3 of 4 files use different names. ADR + rename. Tier S.
