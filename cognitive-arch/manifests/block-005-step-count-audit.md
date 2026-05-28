---
id: block-005
tier: M
kind: refactor
phase: phase-1
scope: phase-bound
status: done
dependencies: []
files:
  read:
    - protocols/block-close-checklist.md
    - protocols/block-retrospective-generation.md
    - protocols/parallelism.md
    - RETROFIT.md
    - CLAUDE.md
    - protocols/trigger-phrases.md
  modify:
    - protocols/block-retrospective-generation.md
    - protocols/parallelism.md
    - CLAUDE.md
    - protocols/trigger-phrases.md
  create: []
gates:
  - name: step-refs-verified
    type: manual
    description: all numbered step cross-references verified against actual protocol step counts
  - name: files-updated
    type: file-changed
    paths: [protocols/block-retrospective-generation.md, protocols/parallelism.md, CLAUDE.md, protocols/trigger-phrases.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-20
---

# Block 005 — Step-count audit pass

- **Tier:** M
- **Kind:** refactor
- **Status:** wip

## 1. Purpose

Fix cross-file step count errors found during audit:

| File | Error | Fix |
|------|-------|-----|
| `protocols/block-retrospective-generation.md` line 10 | "step 4" — but retrospective is block-close step 5 | → "step 5" |
| `protocols/parallelism.md` line 107 | "step 0 of block-close-checklist" — no step 0 exists; lock set during block-start | → "during block-start" |
| `CLAUDE.md` line 13 | "9-step flow" — RETROFIT.md has Steps 0–9 = 10 steps | → "10-step" |
| `protocols/trigger-phrases.md` | same "9-step" error | → "10-step" |

## 2. Files

- **Read:** protocols/block-close-checklist.md, RETROFIT.md, protocols/block-retrospective-generation.md, protocols/parallelism.md, CLAUDE.md, protocols/trigger-phrases.md
- **Modify:** protocols/block-retrospective-generation.md, protocols/parallelism.md, CLAUDE.md, protocols/trigger-phrases.md
- **Create:** none

## 3. Validation

- block-retrospective-generation.md references "step 5" (not step 4)
- parallelism.md references "during block-start" (not "step 0 of block-close-checklist")
- CLAUDE.md and trigger-phrases.md reference "10-step" for RETROFIT

## 4. Out of Scope

- Changing actual protocol step counts (these are verified counts)
- Updating audit.sh with step-count checks
