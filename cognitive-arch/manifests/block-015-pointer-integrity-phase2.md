---
id: block-015
tier: M
kind: enhancement
phase: phase-3
status: planned
dependencies: []
files:
  read:
    - audit.sh
    - commands/audit.md
    - manifests/block-001-fix-axiom-count.md
    - manifests/block-004-audit-parity.md
  modify:
    - audit.sh
    - commands/audit.md
  create: []
gates:
  - name: path-check-implemented
    type: manual
    description: audit.sh check 3 (or new sub-check) validates that file paths listed in manifest files.modify actually exist on disk
  - name: warn-not-error
    type: manual
    description: broken path emits WARN not ERROR — exit code unchanged for now (schemas in stabilization)
  - name: audit-md-documented
    type: manual
    description: commands/audit.md documents the new path-existence check under check 3 or as check 3b
  - name: files-updated
    type: file-changed
    paths: [audit.sh, commands/audit.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 015 — audit.sh — pointer integrity phase 2 (YAML paths)

- **Tier:** M
- **Kind:** enhancement
- **Status:** planned

## 1. Purpose

Extend `audit.sh` check 3 (manifest pointer integrity) to validate that file paths listed in manifest `files.modify` and `files.create` arrays actually exist on disk. Currently check 3 only verifies that the manifest file itself exists; this block adds content-level path checking.

This is "pointer integrity phase 2" — phase 1 was checking that the manifest file exists; phase 2 is checking that the paths *inside* the manifest are real.

## 2. Files

- **Read:** audit.sh, commands/audit.md, two example manifests (for testing logic)
- **Modify:** audit.sh (extend check 3), commands/audit.md (document new sub-check)
- **Create:** none

## 3. Spec

**audit.sh changes:**

For each manifest in `manifests/`, extract `files.modify` paths via simple grep/awk:
```bash
# Extract files.modify paths from manifest frontmatter
# Look for lines between "modify:" and the next key (create:/read:/gates:)
```

For each extracted path:
- If path is `[]` (empty) — skip
- If path is a real file path — check `[ -f "$path" ]`
- If file does not exist → emit `WARN: $manifest: files.modify path not found: $path`

**Scope of check:**
- Only `files.modify` paths checked (files that should already exist)
- `files.create` paths NOT checked (they don't exist yet by design)

**Exit code:** WARN lines do not affect exit code (remain INFO severity until schema stabilizes).

**commands/audit.md changes:**
- Under check 3, add sub-check "3b: YAML path existence (files.modify)" with WARN status note

## 4. Validation

- If a manifest has `files.modify: [audit.sh]` and `audit.sh` exists → no warning
- If a manifest has `files.modify: [nonexistent.md]` → WARN emitted
- audit.sh exit code is unaffected by WARNs
- commands/audit.md documents check 3b

## 5. Out of scope

- `files.create` path checking (by design — these are new files)
- Full YAML parsing (use grep/awk heuristic — exact parser is Phase 5)
- Checking `files.read` paths (read files may be optional references)
- Hard ERROR mode for broken paths (deferred until schemas stable)
