---
id: block-001
tier: S
kind: doc-only
phase: phase-1
status: done
files:
  read:
    - INDEX.md
    - PROTOCOLS.md
  modify:
    - INDEX.md
  create: []
gates:
  - name: files-updated
    type: file-changed
    paths: [INDEX.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-20
---

# Block 001 — Fix axiom-count inconsistency in INDEX.md

- **Tier:** S
- **Kind:** doc-only
- **Status:** wip

## 1. Purpose

Correct INDEX.md's PROTOCOLS.md brief from "14 axioms" to "19 axioms" (actual: P1–P6=6, Q1–Q7=7, C1–C6=6, total=19). Also correct block-close-checklist.md brief from "7-step" to "8-step" (actual per `protocols/block-close-checklist.md`).

## 2. Files

- **Read:** INDEX.md, PROTOCOLS.md
- **Modify:** INDEX.md (two one-line corrections)
- **Create:** none

## 3. Validation

- INDEX.md PROTOCOLS.md brief reads "19 axioms"
- INDEX.md block-close-checklist.md brief reads "8-step"
- STATE.md, NEXT.md, BLOCK_LOG.md updated (block-close protocol)

## 4. Out of scope

- Full step-count sweep across ALL files (→ block-005)
- Fixing CLAUDE.md size budget (→ block-002)
- Formal audit of axiom breakdown (facts are already in PROTOCOLS.md — no ADR needed)
