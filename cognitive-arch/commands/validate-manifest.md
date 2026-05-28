# Command: /validate-manifest

BRIEF: AI-driven manifest validation against JSON Schema. No machine tooling required — executed by reasoning. Checks required fields, enum values, tier constraints, date format.

---

## Trigger

Use when:
- `/validate-manifest <path>`
- "validate the manifest for block-NNN"
- "check if manifests/block-NNN-slug.md is valid"
- Called by Governor before dispatching a block

Auto-execute without asking for confirmation.

---

## Step 1 — Read manifest

Read the target manifest file.

Extract `tier:` from the YAML frontmatter (first value between `---` delimiters).

```
tier: S  →  load manifest-s.schema.json
tier: M  →  load manifest-m.schema.json
tier: L  →  load manifest-l.schema.json
```

If `tier:` is missing or not S/M/L → FAIL immediately: "tier field missing or invalid."

---

## Step 2 — Load schema

Load the appropriate schema file:
- `templates/schemas/manifest-s.schema.json`
- `templates/schemas/manifest-m.schema.json`
- `templates/schemas/manifest-l.schema.json`

---

## Step 3 — Check required fields

For each field listed in the schema's `"required"` array, verify it is present in the manifest frontmatter.

**Tier S required:** `id`, `tier`, `kind`, `phase`, `status`, `files`, `gates`, `created_at`
**Tier M required:** same as Tier S
**Tier L required:** same as Tier S + `adr_required`, `owner`

For each missing required field → record FAIL.

---

## Step 4 — Check enum values

Verify fields with `enum` constraints:

| Field | Valid values |
|-------|-------------|
| `tier` | S \| M \| L |
| `kind` | doc-only \| refactor \| enhancement \| bugfix \| feature |
| `status` | planned \| wip \| done \| blocked \| cancelled |

For each invalid value → record FAIL with: "field `X` has invalid value `Y`. Expected one of: Z"

---

## Step 5 — Check patterns

| Field | Pattern | Example |
|-------|---------|---------|
| `id` | `^block-\d{3}$` | block-007 |
| `phase` | `^phase-\d+$` | phase-2 |
| `created_at` | `^YYYY-MM-DD$` | 2026-05-21 |
| each item in `dependencies` | `^block-\d{3}$` | block-006 |

For each pattern mismatch → record FAIL.

---

## Step 6 — Check tier constraint (file count)

Count: `len(files.modify) + len(files.create)` = **N**

| Tier | Constraint | Pass condition |
|------|-----------|----------------|
| S | ≤ 2 | N ≤ 2 |
| M | 3–8 | 3 ≤ N ≤ 8 |
| L | ≥ 9 OR cross_repo:true | N ≥ 9 OR cross_repo is present and true |

If constraint fails → record FAIL: "Tier X requires N files modified/created. Found: Y"

---

## Step 7 — Tier L extras

If tier is L:
- `adr_required` must be `true` → FAIL if false or missing
- `adr_ref` must be present when `adr_required: true` → FAIL if missing
- `adr_ref` must match pattern `^decisions/ADR-\d{3}.*\.md$` → FAIL if not

---

## Step 8 — Check gates

Verify `gates:` is a non-empty array.
For each gate object:
- Must have `name` (string) → FAIL if missing
- Must have `type` (string) → FAIL if missing
- If type is `file-changed` or `file-exists`: must have `paths` → WARN if missing
- If type is `manual`: must have `description` → WARN if missing

---

## Step 9 — Report

Output validation result in this format:

```
validate-manifest: manifests/block-NNN-slug.md
schema: manifest-{tier}.schema.json
────────────────────────────────────────
required-fields:      PASS  (8/8 present)
enum-values:          PASS
patterns:             PASS  (id, phase, created_at, deps)
tier-constraint:      PASS  (Tier S: 1 file, ≤ 2 ✓)
tier-L-extras:        N/A
gates-structure:      PASS  (3 gates, all valid)
────────────────────────────────────────
overall:              VALID
```

If any FAIL:
```
validate-manifest: manifests/block-NNN-slug.md
schema: manifest-{tier}.schema.json
────────────────────────────────────────
required-fields:      FAIL  — missing: [adr_required]
enum-values:          PASS
patterns:             FAIL  — id "block-07" does not match ^block-\d{3}$
tier-constraint:      PASS
tier-L-extras:        FAIL  — adr_required missing
gates-structure:      PASS
────────────────────────────────────────
overall:              INVALID (2 failures)

Fix:
  1. id: "block-07" → "block-007"
  2. Add adr_required: true to frontmatter
  3. Add adr_ref: "decisions/ADR-NNN-slug.md" to frontmatter
```

---

## Batch validation

To validate all manifests in a phase:

1. List: `manifests/block-NNN-*.md` for blocks in the phase
2. Run Steps 1–9 for each
3. Report summary: `N/M valid`

---

## Notes

- This command uses AI reasoning — no JSON Schema tooling required
- Machine-executable validation (automated CI gate) → Phase 5 / v2.0
- Schema files are the source of truth: `templates/schemas/manifest-{s,m,l}.schema.json`
- If a manifest has `axiom_override:` field, validation passes (override is documented, not a violation)

End of validate-manifest command.
