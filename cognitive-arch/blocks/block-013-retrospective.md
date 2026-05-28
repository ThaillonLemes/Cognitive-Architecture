---
id: block-013
manifest: manifests/block-013-schema-tier-l.md
status: done
gates_passed: 3/3
completed_at: 2026-05-21T00:00Z
agent: main-session
commit: -
duration_actual_days: 0
tok_estimated: ~250
tok_src: estimated
---

# Block 013 Retrospective — JSON Schema — Tier L manifest

## 1. What was built

- Created `templates/schemas/manifest-l.schema.json` — JSON Schema draft-07 for Tier L manifests.
- Required fields: same as S/M + `adr_required` (must be `true`) + `owner`.
- `adr_ref` conditionally required via JSON Schema `if/then`: if `adr_required: true` then `adr_ref` required.
- Optional fields: `cross_repo`, `rollback_plan`, `review_required`, `estimated_hours`.
- `gates` minItems raised to 2 (Tier L blocks must have at least 2 gates).
- Tier L constraint: len(modify) + len(create) ≥ 9 OR cross_repo:true — in `$comment`.
- No existing Tier L manifests to validate against (forward-looking schema).

## 2. Tests added

None.

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| schema-exists | ✓ | `templates/schemas/manifest-l.schema.json` created |
| tier-l-constraint | ✓ | ≥9 files constraint documented; cross_repo escape hatch present |
| required-fields-covered | ✓ | adr_required required and constrained to true; owner required |
| files-updated | ✓ | BLOCK_LOG.md updated at phase close |

## 4. Decisions made

- Used JSON Schema `if/then` to make `adr_ref` conditionally required when `adr_required: true`. This is valid in draft-07 and avoids requiring `adr_ref` when it's not applicable.
- `adr_required` enum is `[true]` — enforces that it can only ever be `true` for Tier L (cannot be false).

## 5. Deferred to future blocks

- Machine-executable validation → Phase 5
- First actual Tier L block (none in current roadmap through Phase 5)

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| PROTOCOLS.md | ~7,700 | ~1,925 |
| INDEX.md | ~11,700 | ~2,925 |

```
tok_estimated: ~250  tok_src:estimated
```

## 7. Issues / surprises

None. No existing Tier L manifests to validate against — schema is forward-compatible by design.

## 8. Files actually touched

- Created: templates/schemas/manifest-l.schema.json
- Otherwise as manifest.
