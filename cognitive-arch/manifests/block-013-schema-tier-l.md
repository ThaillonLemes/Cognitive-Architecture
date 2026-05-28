---
id: block-013
tier: S
kind: doc-only
phase: phase-3
status: planned
dependencies: []
files:
  read:
    - PROTOCOLS.md
    - INDEX.md
  modify: []
  create:
    - templates/schemas/manifest-l.schema.json
gates:
  - name: schema-exists
    type: file-exists
    paths: [templates/schemas/manifest-l.schema.json]
  - name: tier-l-constraint
    type: manual
    description: schema enforces files.modify + files.create >= 9 OR cross-repo flag present
  - name: required-fields-covered
    type: manual
    description: schema adds adr_required field (boolean, required for Tier L)
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 013 — JSON Schema — Tier L manifest

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Create `templates/schemas/manifest-l.schema.json` — JSON Schema for Tier L manifest frontmatter. Tier L = 9+ files modified/created, OR cross-repo impact. Tier L blocks must have an ADR. No existing Tier L manifests yet; this schema is forward-looking.

## 2. Files

- **Read:** PROTOCOLS.md (tier definitions), INDEX.md
- **Modify:** none
- **Create:** templates/schemas/manifest-l.schema.json

## 3. Spec

Same base fields as Tier S/M schemas with these differences:

- `tier` — enum: ["L"]
- `files` constraint: len(modify) + len(create) ≥ 9, OR `cross_repo: true`
- `adr_required` — boolean, **required**, must be `true` for Tier L (architectural decision required)
- `adr_ref` — string, required when adr_required is true (e.g., "decisions/ADR-003.md")
- `owner` — string, required for Tier L (large blocks must have a named owner)
- `review_required` — boolean, recommended (Tier L blocks benefit from review before close)
- `estimated_hours` — integer, recommended
- `cross_repo` — boolean, optional (marks cross-repository impact)
- `rollback_plan` — string, optional (how to revert if block fails)

## 4. Validation

- Schema is internally consistent (valid JSON Schema draft-07)
- A manifest with 9 modified files and adr_required: true passes
- A manifest with 9 modified files and no adr_required field fails

## 5. Out of scope

- Machine-executable validation tooling (Phase 5+)
- Tier S or M schemas (blocks 011, 012)
- Actual Tier L blocks (Phase 5+ work)
