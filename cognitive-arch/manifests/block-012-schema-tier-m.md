---
id: block-012
tier: S
kind: doc-only
phase: phase-3
status: planned
dependencies: []
files:
  read:
    - manifests/block-002-claude-md-budget.md
    - manifests/block-005-step-count-audit.md
  modify: []
  create:
    - templates/schemas/manifest-m.schema.json
gates:
  - name: schema-exists
    type: file-exists
    paths: [templates/schemas/manifest-m.schema.json]
  - name: schema-validates-existing
    type: manual
    description: manifest-m.schema.json validates all existing Tier M manifests (002, 005) without errors
  - name: tier-m-constraint
    type: manual
    description: schema enforces files.modify + files.create between 3 and 8 items
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 012 — JSON Schema — Tier M manifest

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Create `templates/schemas/manifest-m.schema.json` — JSON Schema for Tier M manifest frontmatter. Tier M = 3–8 files modified/created. Enables AI validation and documents what a valid medium-complexity block looks like.

## 2. Files

- **Read:** manifests/block-002-claude-md-budget.md, manifests/block-005-step-count-audit.md (reference Tier M examples)
- **Modify:** none
- **Create:** templates/schemas/manifest-m.schema.json

## 3. Spec

Same fields as Tier S schema (block-011) with these differences:

- `tier` — enum: ["M"]
- `files` constraint: len(modify) + len(create) must be 3–8 (minItems: 3, maxItems: 8 across combined array)
- `dependencies` — more likely to be populated; still optional
- `scope` — recommended (may span sub-modules)
- `estimated_hours` — optional integer field (Tier M blocks often take longer)

Additional recommended (not required) fields for Tier M:
- `owner` — string (who executes this block)
- `parallel_safe` — boolean (safe to run with other blocks?)

## 4. Validation

- All existing Tier M manifests (002, 005) pass the schema
- A manifest with 2 modified files fails the schema (tier M constraint)
- A manifest with 9 modified files fails the schema (too large for M)

## 5. Out of scope

- Machine-executable validation tooling (Phase 5+)
- Tier S or L schemas (blocks 011, 013)
