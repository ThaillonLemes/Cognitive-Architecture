---
id: block-043
tier: S
kind: doc-only
phase: phase-6
status: done
dependencies:
  - block-042
files:
  read:
    - phase-0/03-roadmap-draft.md
    - STATE.md
    - blocks/BLOCK_LOG.md
  modify:
    - phase-0/03-roadmap-draft.md
  create: []
gates:
  - name: file-updated
    type: file-changed
    paths: [phase-0/03-roadmap-draft.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 043 — Update roadmap to reflect phases 1–7

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Update `phase-0/03-roadmap-draft.md` to reflect what actually happened: Phases 1–5 complete, Phase 6 in progress (Retrofit Readiness, not the originally planned "Multi-agent maturation"), Phase 7 planned (SDK depth). The original roadmap was written before Phase 5 and has never been updated.

## 2. Files

- **Read:** `phase-0/03-roadmap-draft.md`, `STATE.md`, `blocks/BLOCK_LOG.md`
- **Modify:** `phase-0/03-roadmap-draft.md`
- **Create:** none

## 3. Validation

- Roadmap table rows for Phases 1–5 show `complete` or equivalent marker
- Phase 6 row updated: theme changed from "Multi-agent maturation" to "Retrofit Readiness (v2.0)" with correct block count
- Phase 7 row added: theme "SDK Depth (v2.1)" — async dispatch, file I/O, pytest, audit checks 5–8
- Original Phase 6/7 themes (multi-agent, brainstorm-on-arch) moved to `…` / v3.0+ row

## 4. Out of scope

- Creating `phases/MASTER.md` as a separate file (edit the existing roadmap doc instead)
- Detailed block lists for Phase 7 (Phase 7 phase doc generated separately later)
- Changing the roadmap format or adding new columns
