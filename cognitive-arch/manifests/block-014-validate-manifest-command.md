---
id: block-014
tier: S
kind: doc-only
phase: phase-3
status: planned
dependencies: [block-011, block-012, block-013]
files:
  read:
    - templates/schemas/manifest-s.schema.json
    - templates/schemas/manifest-m.schema.json
    - templates/schemas/manifest-l.schema.json
    - commands/audit.md
  modify: []
  create:
    - commands/validate-manifest.md
gates:
  - name: command-exists
    type: file-exists
    paths: [commands/validate-manifest.md]
  - name: schema-reference
    type: manual
    description: validate-manifest.md references all three schema files (S, M, L) and instructs AI to load the correct one based on manifest tier
  - name: workflow-complete
    type: manual
    description: command has step-by-step validation workflow that an AI can execute without external tooling
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 014 — Command: validate-manifest

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Dependencies:** block-011, block-012, block-013 (schemas must exist first)

## 1. Purpose

Create `commands/validate-manifest.md` — a step-by-step AI command for validating any manifest against its JSON Schema. Uses AI reasoning (no machine tooling required). Completes the schema validation loop started by blocks 011-013.

## 2. Files

- **Read:** templates/schemas/manifest-s.schema.json, manifest-m.schema.json, manifest-l.schema.json, commands/audit.md
- **Modify:** none
- **Create:** commands/validate-manifest.md

## 3. Spec

`commands/validate-manifest.md` must include:

**Trigger:** `/validate-manifest <path>` or "validate the manifest for block-NNN"

**Step 1 — Read manifest:**
- Read the target manifest file
- Extract `tier:` from frontmatter

**Step 2 — Load schema:**
- If tier: S → load `templates/schemas/manifest-s.schema.json`
- If tier: M → load `templates/schemas/manifest-m.schema.json`
- If tier: L → load `templates/schemas/manifest-l.schema.json`

**Step 3 — Validate required fields:**
- For each required field in schema, check that manifest frontmatter has it
- Check field values against enum constraints (status, tier, kind)
- Check date format for created_at

**Step 4 — Validate tier constraint:**
- Count files.modify + files.create items
- Compare against tier constraint (S: ≤2, M: 3-8, L: ≥9)

**Step 5 — Report:**
- List: PASS / WARN / FAIL for each check
- If any FAIL: list specific failures with fix suggestions
- If all PASS: confirm manifest is valid

**Output format:**
```
validate-manifest: block-NNN
schema: manifest-{tier}.schema.json
required-fields: PASS
tier-constraint: PASS (2 files, tier S ≤ 2)
date-format: PASS
overall: VALID
```

## 4. Validation

- Command clearly explains which schema to load for each tier
- Step-by-step workflow can be executed by AI without external tooling
- Output format is consistent and human-readable

## 5. Out of scope

- Machine-executable validation (Phase 5)
- Network-based schema validation
- Validating non-manifest files
