---
id: block-016
tier: S
kind: refactor
phase: phase-3
status: planned
dependencies: []
files:
  read:
    - commands/audit.md
    - phases/phase-3.md
  modify:
    - commands/audit.md
  create: []
gates:
  - name: dep-graph-check-documented
    type: manual
    description: commands/audit.md check 6 (dep-graph) describes how to resolve block dependency IDs manually
  - name: resolution-steps-clear
    type: manual
    description: the check explains what a valid dependency ID looks like and how to detect unresolvable ones
  - name: files-updated
    type: file-changed
    paths: [commands/audit.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 016 — audit.md — dep-graph check improvement

- **Tier:** S
- **Kind:** refactor
- **Status:** planned

## 1. Purpose

Improve `commands/audit.md` check 6 (dependency graph validation) from aspirational placeholder to actionable guidance. Currently check 6 just says "validate dep graph" with no method. This block rewrites it to describe:
- What a valid dependency ID looks like (format: `block-NNN`)
- How to manually verify that a dependency ID resolves to an actual manifest
- How to detect circular dependencies by inspection

## 2. Files

- **Read:** commands/audit.md, phases/phase-3.md
- **Modify:** commands/audit.md (rewrite check 6 section)
- **Create:** none

## 3. Spec

**Rewrite check 6 in commands/audit.md:**

```markdown
### Check 6 — Dependency graph (Governor-only, partially manual)

**What to check:**
1. For each manifest with `dependencies:` field, verify each listed ID matches `^block-\d{3}$`
2. For each dependency ID, verify `manifests/block-NNN-*.md` exists
3. Inspect for cycles: if block-A depends on block-B and block-B depends on block-A → WARN

**Manual validation:**
- List all manifests with non-empty dependencies
- For each dep ID, run: `ls manifests/block-{NNN}-*.md` — if no match → BROKEN DEP
- Cycle detection: trace the dependency chain 3 levels deep; if a block reappears → CYCLE

**Automated (Governor-only):**
Full cycle detection and topological sort are Governor responsibilities.
Script check: only validates ID format and file existence (not cycles).
```

## 4. Validation

- commands/audit.md check 6 has concrete steps (not just "validate dep graph")
- Resolution method is described in plain language
- Cycle detection is noted as manual/Governor-only (not pretended to be automated)

## 5. Out of scope

- Implementing automated dep-graph cycle detection in bash (Governor-only)
- Cross-phase dependency validation (Phase 5)
