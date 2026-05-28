---
id: phase-3
status: done
version: v1.3
opened_at: 2026-05-21
closed_at: 2026-05-21
blocks_total: 6
blocks_done: 6
---

# Phase 3 — Retrospective (v1.3 Formal schema validation)

## What was delivered

All 6 planned blocks completed. Manifest frontmatter is now formally specified and AI-validatable. Audit script gained structural path checking.

## Block summary

| Block | What | Files changed |
|-------|------|--------------|
| block-011 | JSON Schema Tier S — required fields, enums, patterns, tier constraint doc | templates/schemas/manifest-s.schema.json |
| block-012 | JSON Schema Tier M — same base + 3-8 file constraint, owner/parallel_safe fields | templates/schemas/manifest-m.schema.json |
| block-013 | JSON Schema Tier L — adds adr_required (true only), adr_ref conditional require, owner required | templates/schemas/manifest-l.schema.json |
| block-015 | audit.sh check 3b — awk-based YAML files.modify path existence check (WARN) | audit.sh, commands/audit.md |
| block-016 | audit.md check 6 — dep-graph validation: format spec, file resolution, Q5 check, 3-hop cycle detection | commands/audit.md |
| block-014 | /validate-manifest command — 9-step AI workflow, tier routing, all constraint checks, fix suggestions | commands/validate-manifest.md |

## Exit criteria check

| Criterion | Status |
|-----------|--------|
| `templates/schemas/manifest-s.schema.json` validates Tier S manifest | ✅ |
| `templates/schemas/manifest-m.schema.json` validates Tier M manifest | ✅ |
| `templates/schemas/manifest-l.schema.json` validates Tier L manifest | ✅ |
| `commands/validate-manifest.md` has step-by-step workflow | ✅ 9 steps, tier routing, fix suggestions |
| `audit.sh` check 3 catches broken YAML paths (files.modify) | ✅ awk-based check 3b, WARN severity |

## Notes

Group 3A (5 blocks) executed fully in parallel — no conflicts (all touched different files or created new files). Group 3B (block-014) ran after 3A; depended on the 3 schema files being complete.

Key design constraint surfaced: JSON Schema draft-07 cannot natively sum two sibling array lengths to enforce tier constraints. Resolution: constraint documented in `$comment` fields; enforcement delegated to `/validate-manifest` command reasoning. This is correct — schema documents the structure, command enforces the semantics.

audit.sh check 3b uses `awk` state machine — cleaner than grep/sed pipeline for multi-line YAML section extraction.

## Next phase

Phase 4 (v1.4) — Governor v2 design.
Entry point: `phases/phase-4.md`
First group (4A): block-017 only (master design doc — must run first).
Then group 4B: blocks 018-025 in parallel (6 protocols + 2 templates).
Then group 4C: blocks 026-028 in parallel (3 protocol updates).
