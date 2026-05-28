---
id: block-011
tier: S
kind: doc-only
phase: phase-3
status: planned
dependencies: []
files:
  read:
    - manifests/block-001-fix-axiom-count.md
    - manifests/block-004-audit-parity.md
    - manifests/block-006-syntax-completeness.md
  modify: []
  create:
    - templates/schemas/manifest-s.schema.json
gates:
  - name: schema-exists
    type: file-exists
    paths: [templates/schemas/manifest-s.schema.json]
  - name: schema-validates-existing
    type: manual
    description: manifest-s.schema.json validates all existing Tier S manifests (001,003,004,005,006) without errors
  - name: required-fields-covered
    type: manual
    description: schema requires id, tier, kind, phase, status, files (read/modify/create), gates, created_at
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 011 — JSON Schema — Tier S manifest

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Create `templates/schemas/manifest-s.schema.json` — a JSON Schema that formally validates Tier S manifest frontmatter. Enables AI-driven validation via `/validate-manifest` (block-014) and documents what a valid manifest looks like machine-readably.

## 2. Files

- **Read:** manifests/block-001-fix-axiom-count.md, manifests/block-004-audit-parity.md, manifests/block-006-syntax-completeness.md (reference Tier S examples)
- **Modify:** none
- **Create:** templates/schemas/manifest-s.schema.json

## 3. Spec

Schema must cover:
- `id` — string, pattern: `^block-\d{3}$`
- `tier` — enum: ["S"]
- `kind` — enum: ["doc-only", "refactor", "enhancement", "bugfix", "feature"]
- `phase` — string, pattern: `^phase-\d+$`
- `status` — enum: ["planned", "wip", "done", "blocked", "cancelled"]
- `dependencies` — array of strings (block IDs), optional
- `files` — object with `read` (array), `modify` (array), `create` (array)
  - Tier S constraint: len(modify) + len(create) ≤ 2
- `gates` — array of gate objects (each has `name`, `type`, at least one of `paths`/`description`)
- `created_at` — string, date format (YYYY-MM-DD)
- `scope` — string, optional, enum: ["phase-bound", "cross-phase"]

Tier S constraint: `files.modify` + `files.create` combined must have ≤ 2 items.

## 4. Validation

- All existing Tier S manifests (001, 003, 004, 005, 006) pass the schema
- A manifest with 3+ modified files fails the schema (tier S constraint)

## 5. Out of scope

- Machine-executable validation tooling (Phase 5+)
- Schema for Tier M or L (blocks 012, 013)
