---
id: block-002
tier: S
kind: refactor
phase: phase-1
status: done
files:
  read:
    - CLAUDE.md
  modify:
    - CLAUDE.md
  create:
    - protocols/trigger-phrases.md
gates:
  - name: lines-budget
    type: manual
    description: CLAUDE.md line count ≤ 60
  - name: files-updated
    type: file-changed
    paths: [CLAUDE.md, protocols/trigger-phrases.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-20
---

# Block 002 — Bring CLAUDE.md within Q2 size budget

- **Tier:** S
- **Kind:** refactor
- **Status:** wip

## 1. Purpose

Reduce CLAUDE.md from 108 lines to ≤60 (Q2 budget). Extract the trigger-phrase tables and detection-marker list into `protocols/trigger-phrases.md`. CLAUDE.md retains a condensed routing summary + pointer to the new protocol.

## 2. Files

- **Read:** CLAUDE.md
- **Modify:** CLAUDE.md (full rewrite — condensed)
- **Create:** protocols/trigger-phrases.md (extracted content)

## 3. Validation

- CLAUDE.md line count ≤ 60
- All trigger routes still reachable (summary in CLAUDE.md + full tables in trigger-phrases.md)
- STATE.md, NEXT.md, BLOCK_LOG.md updated at block-close

## 4. Out of scope

- Updating INDEX.md Briefs section to list trigger-phrases.md (→ block-005 step-count/sweep pass)
- Renaming "Comment Charter" → "Charter" (→ block-003)
- audit.sh portability (→ block-004 / phase-2)
