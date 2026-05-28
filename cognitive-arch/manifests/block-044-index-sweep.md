---
id: block-044
tier: S
kind: doc-only
phase: phase-6
status: done
dependencies:
  - block-043
files:
  read:
    - INDEX.md
    - sdk/governor.py
    - sdk/convention_snippet.py
    - sdk/task_packet.py
    - sdk/return_validator.py
    - sdk/dispatch.py
    - sdk/integration.py
    - sdk/config.py
  modify:
    - INDEX.md
  create: []
gates:
  - name: file-updated
    type: file-changed
    paths: [INDEX.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 044 — Sweep INDEX.md for SDK + Phase 6 entries

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Add missing entries to `INDEX.md` for all 7 `sdk/` modules, the new Phase 6 files created in blocks 038–043, and `phases/phase-6.md`. Remove or mark stale any entries that no longer exist. Ensure every new file has a one-line BRIEF in the catalog.

## 2. Files

- **Read:** `INDEX.md`, all 7 `sdk/*.py` files (for their code-header BRIEFs), and any new files from blocks 038–043
- **Modify:** `INDEX.md`
- **Create:** none

## 3. Validation

- `INDEX.md` has entries for: `sdk/governor.py`, `sdk/convention_snippet.py`, `sdk/task_packet.py`, `sdk/return_validator.py`, `sdk/dispatch.py`, `sdk/integration.py`, `sdk/config.py`
- `INDEX.md` has entries for `phases/phase-6.md`, `phases/phase-5-retro.md`, `phases/phase-1.md`
- `INDEX.md` has entries for all 3 stack addenda (even if paths use TBD until block-047+)
- No entries point to files that don't exist (pointer integrity)
- Each new entry is ≤ 15 words (BRIEF format per `_syntax.md`)

## 4. Out of scope

- Rewriting all existing INDEX.md entries (only add missing + remove broken)
- Adding entries for Phase 7 files (those don't exist yet)
- Reordering the entire INDEX.md structure
