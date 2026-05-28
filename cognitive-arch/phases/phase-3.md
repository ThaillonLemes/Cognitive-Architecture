---
id: phase-3
status: planned
version: v1.3
prev_phase: phase-2
exit_criteria_count: 5
blocks_count: 6
estimated_duration_days: 5
created_at: 2026-05-20
last_updated: 2026-05-20
owner: implementer
---

# Phase 3 — Formal schema validation (v1.3)

BRIEF: Make the audit trustworthy. Manifest frontmatter gets JSON Schemas. audit.sh gains YAML path checks. Dependency ID validation moves from "Governor-only aspirational" to implementable.

## 1. Purpose

Currently, a broken manifest (missing required field, wrong tier field, invalid status value) is only caught by an LLM reading it — not by a script. This phase introduces:
- JSON Schemas for Tier S, M, L manifest frontmatter
- A `/validate-manifest` command for AI-driven schema validation
- Pointer integrity phase 2: YAML file paths in manifests must exist
- Pointer integrity phase 3: block dependency IDs must resolve

This makes the audit checklist mechanically verifiable for the parts that don't require reasoning.

## 2. Goals

- JSON Schema files exist for all three manifest tiers
- AI can validate any manifest against its schema via `commands/validate-manifest.md`
- audit.sh check 3 extended: catches broken file paths in manifest YAML
- commands/audit.md check 6 (dep-graph) improved: dependency ID resolution documented
- All existing manifests pass the new schemas

## 3. Invariants

- Existing manifests (001-006) must not require modification (schemas are backward-compatible)
- audit.sh remains exit-code compatible (new checks are WARN, not ERROR, until schemas are stable)

## 4. Dependencies

- Phase 1 complete ✅
- Phase 2 not required (independent)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing manifests fail new schema | Med | Schema designed to match current manifests; tier-S is the reference |
| JSON Schema tooling unavailable | Low | Schemas used by AI for validation (commands/validate-manifest.md); machine validation is Phase 5+ |

## 7. Exit Criteria

1. `templates/schemas/manifest-s.schema.json` exists and validates a Tier S manifest
2. `templates/schemas/manifest-m.schema.json` exists and validates a Tier M manifest
3. `templates/schemas/manifest-l.schema.json` exists and validates a Tier L manifest
4. `commands/validate-manifest.md` exists with step-by-step validation workflow
5. `audit.sh` check 3 catches at least one class of broken YAML paths (manifests files.modify)

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-011 | JSON Schema — Tier S manifest | S | planned | `manifests/block-011-schema-tier-s.md` |
| block-012 | JSON Schema — Tier M manifest | S | planned | `manifests/block-012-schema-tier-m.md` |
| block-013 | JSON Schema — Tier L manifest | S | planned | `manifests/block-013-schema-tier-l.md` |
| block-014 | Command: validate-manifest | S | planned | `manifests/block-014-validate-manifest-command.md` |
| block-015 | audit.sh — pointer integrity phase 2 (YAML paths) | M | planned | `manifests/block-015-pointer-integrity-phase2.md` |
| block-016 | audit.md — dep-graph check improvement | S | planned | `manifests/block-016-dep-graph-check.md` |

## 9. Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 6
  recommended_agents: 3
  groups:
    - id: 3A
      blocks: [block-011, block-012, block-013, block-015, block-016]
      type: parallel
      depends_on: []
    - id: 3B
      blocks: [block-014]
      type: sequential
      depends_on: [3A]
```

block-014 (validate-manifest command) references the schemas from 011-013, so it runs after group 3A.

## 10. Out of Scope

- Machine-executable schema validation (requires Python/Node tooling — Phase 5+)
- Full dep-graph cycle detection in bash (Governor-only; Phase 5)
- Schema validation as a hard gate in manifests (informational for now)
