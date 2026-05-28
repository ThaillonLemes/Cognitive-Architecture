---
id: block-001
status: done
tier: S
kind: doc-only
opened_at: 2026-05-20
closed_at: 2026-05-20
duration_actual: <1h
---

# Block 001 — Retrospective

## What was built

Corrected two inconsistencies in `INDEX.md`:

1. `PROTOCOLS.md` brief: **"14 axioms" → "19 axioms"** (actual breakdown: P1–P6=6, Q1–Q7=7, C1–C6=6, total=19).
2. `block-close-checklist.md` brief: **"7-step" → "8-step"** (actual per `protocols/block-close-checklist.md`).

Also created:
- `decisions/ADR-001-structure-option-a.md` — records the Option A structure decision (dogfood total, Tier S default).
- `manifests/block-001-fix-axiom-count.md` — this block's Tier S manifest.

## Gates result

| Gate | Result | Notes |
|------|--------|-------|
| files-updated (INDEX.md) | PASS | Two lines corrected |
| files-updated (STATE.md) | PASS | Updated at block-close |
| files-updated (NEXT.md) | PASS | Updated at block-close |
| files-updated (BLOCK_LOG.md) | PASS | Entry appended |

## Process notes

First block under ADR-001 (Option A, dogfood-total). Overhead: 4 artifacts (manifest, STATE, NEXT, retrospective) for a 2-line correction. This is the deliberate data point to evaluate Tier S sizing. Overhead is acceptable for now; re-evaluate after block-003 or block-004.

No git repo in workspace — step 7 (commit) skipped. Git is a dependency documented in `phase-0/01-stack-and-tools.md`. Not a block-001 concern.

## Scope changes

The "7-step → 8-step" fix was added because it lives in the same file and is the same category of error. This is not scope creep — it's deduplication within a single-file block.

## Next recommended

`block-002` — Bring `CLAUDE.md` within Q2 size budget (currently 108 lines vs 60-line budget). Likely requires moving trigger-phrase tables to a sub-protocol. Upgrade to Tier M if >2 files are modified.
