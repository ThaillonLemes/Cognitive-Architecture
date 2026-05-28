---
id: block-004
tier: S
kind: refactor
phase: phase-1
scope: phase-bound
status: done
dependencies: []
files:
  read:
    - audit.sh
    - commands/audit.md
  modify:
    - audit.sh
    - commands/audit.md
  create: []
gates:
  - name: labels-consistent
    type: manual
    description: audit.sh labels read [N/8] and Governor-only note present for checks 5-8
  - name: files-updated
    type: file-changed
    paths: [audit.sh, commands/audit.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-20
---

# Block 004 — audit.sh ↔ commands/audit.md parity

- **Tier:** S
- **Kind:** refactor
- **Status:** wip

## 1. Purpose

Resolve mismatch between `audit.sh` (5 labeled checks) and `commands/audit.md` (8 declared checks). Strategy: document the split rather than implement checks 5–8 in bash (manifest schema, dep-graph, file-conflict, and drift require LLM reasoning and are Governor-only).

Concretely:
- `audit.sh`: relabel [1/5]–[5/5] to [1/8]–[4/8]; fold bootstrap state check into check 4; add [5-8/8] Governor-only note
- `commands/audit.md`: mark each check header as (script) or (Governor-only); add coverage table

## 2. Files

- **Read:** audit.sh, commands/audit.md
- **Modify:** audit.sh, commands/audit.md
- **Create:** none

## 3. Validation

- audit.sh check labels read [1/8] through [4/8]
- audit.sh has explicit note pointing to commands/audit.md for checks 5–8
- commands/audit.md check headers have (script) / (Governor-only) annotations

## 4. Out of Scope

- Implementing checks 5–8 in bash (Phase 2 / v1.3 audit-depth scope)
- PowerShell port of audit.sh (Phase 2 / v1.2)
