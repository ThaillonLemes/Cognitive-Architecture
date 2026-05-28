---
id: block-087
tier: S
kind: doc-only
phase: phase-12
status: pending
security: false
files:
  read:
    - templates/ADR.md
    - decisions/ADR-001-structure-option-a.md
    - decisions/ADR-002-charter-naming.md
    - design/arch-v3.md
    - phases/phase-4.md
    - PROTOCOLS.md
  modify: []
  create:
    - decisions/ADR-003-tier-system-S-M-L.md
    - decisions/ADR-004-governor-v2-python-sdk.md
    - decisions/ADR-005-group-m-axioms-split.md
gates:
  - name: three-adrs-created
    type: file-changed
    paths: [decisions/ADR-003-tier-system-S-M-L.md, decisions/ADR-004-governor-v2-python-sdk.md, decisions/ADR-005-group-m-axioms-split.md]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-087-adr-reintroduction.md]
created_at: 2026-05-23
---

# Block 087 — ADR reintroduction

- **Tier:** S
- **Kind:** doc-only
- **Status:** pending

## 1. Purpose

Backfill 3 architectural decision records (ADRs) for major decisions made historically without formal documentation: the Tier S/M/L manifest system, Governor v2 Python SDK adoption, and the Group M cognitive-arch-as-axiomas split. Marks them `backfilled: true` for transparency.

## 2. Files

- **Read:** ADR template, existing ADR-001/002 for style reference, phase-4 (Governor v2 design context), PROTOCOLS.md (Group M context), design/arch-v3.md
- **Modify:** —
- **Create:** ADR-003 (Tier S/M/L), ADR-004 (Governor v2 SDK), ADR-005 (Group M)

## 3. Validation

- All 3 ADRs follow `templates/ADR.md` structure
- Each ADR frontmatter includes `backfilled: true` and `original_decision_date: <approx>`
- Cross-references to source phases/blocks accurate

## 4. Out of scope

- Backfilling all historical decisions (only top-3 by consequence)
- Modifying existing ADR template (Phase 13 may revisit)
- Creating ADRs prospectively (that's natural workflow, no block needed)
