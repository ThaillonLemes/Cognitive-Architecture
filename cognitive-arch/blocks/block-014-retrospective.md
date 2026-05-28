---
id: block-014
manifest: manifests/block-014-validate-manifest-command.md
status: done
gates_passed: 4/4
completed_at: 2026-05-21T00:00Z
agent: main-session
commit: -
duration_actual_days: 0
tok_estimated: ~450
tok_src: estimated
---

# Block 014 Retrospective — Command: validate-manifest

## 1. What was built

- Created `commands/validate-manifest.md` — 9-step AI-executable manifest validation command.
- Step 1: read manifest, extract tier.
- Step 2: load corresponding schema (S/M/L).
- Steps 3-8: check required fields, enum values, pattern constraints, tier file-count constraint, Tier L extras (adr_required/adr_ref), gate structure.
- Step 9: report with pass/fail table + fix suggestions on failure.
- Batch validation note: run Steps 1-9 for each manifest, report N/M valid.
- Both valid and invalid example reports included.

## 2. Tests added

None (doc-only block).

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| command-exists | ✓ | `commands/validate-manifest.md` created |
| schema-reference | ✓ | All 3 schema files referenced; tier-to-schema routing table in Step 2 |
| workflow-complete | ✓ | 9 steps executable by AI without external tooling |
| files-updated | ✓ | BLOCK_LOG.md updated at phase close |

## 4. Decisions made

- Tier constraint check (Step 6) uses a table format mapping tier → range → pass condition. Cleaner than prose for a checklist command.
- Example reports (valid + invalid) included in Step 9. Makes the output format unambiguous.
- Batch validation note kept brief — details belong in Governor dispatch protocol, not here.

## 5. Deferred to future blocks

- Machine-executable validation as a CI gate → Phase 5

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| templates/schemas/manifest-s.schema.json | ~3,200 | ~800 |
| templates/schemas/manifest-m.schema.json | ~3,400 | ~850 |
| templates/schemas/manifest-l.schema.json | ~3,600 | ~900 |
| commands/audit.md | ~4,100 | ~1,025 |

```
tok_estimated: ~450  tok_src:estimated
```

## 7. Issues / surprises

None. The 3 schema files were complete and consistent — command could directly reference their `required` arrays without ambiguity.

## 8. Files actually touched

- Created: commands/validate-manifest.md
- Otherwise as manifest.
