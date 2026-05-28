---
id: block-080
tier: S
kind: implementation
phase: phase-10
scope: phase-bound
status: planned
security: false
dependencies:
  - block-079
files:
  read:
    - protocols/block-close-checklist.md
    - templates/manifest-medium.md
    - templates/manifest-large.md
    - templates/manifest-small.md
  modify:
    - protocols/block-close-checklist.md
    - templates/manifest-medium.md
    - templates/manifest-large.md
    - templates/manifest-small.md
  create: []
gates:
  - name: security-field-in-medium-manifest
    type: command
    cmd: "grep -q \"security:\" templates/manifest-medium.md"
    expect: exit 0
  - name: security-review-in-checklist
    type: command
    cmd: "grep -q \"security-review\" protocols/block-close-checklist.md"
    expect: exit 0
  - name: checklist-changed
    type: file-changed
    paths:
      - protocols/block-close-checklist.md
  - name: manifest-templates-changed
    type: file-changed
    paths:
      - templates/manifest-medium.md
      - templates/manifest-large.md
created_at: 2026-05-23
last_updated: 2026-05-23
---

# block-080 — Security Gate Integration

## Purpose

Wire the Phase 10 security infrastructure into the standard block lifecycle. This block modifies four existing files to close the loop: the block-close checklist gains a conditional security-review step, and all three manifest templates gain a `security:` field with a default value of `false`.

After this block, every new manifest created from any template will include the `security:` field from the moment of creation, and the block-close checklist will enforce the security-review gate whenever that field is set to `true`.

---

## Context

Phase 10 has established the axioms (block-076), the conventions document (block-077), the threat model template and guide (block-078), and the review command (block-079). None of these changes affect the workflow unless they are connected to the existing process infrastructure. This block performs that connection.

The integration has two surfaces:

1. **Manifest templates** — developers create new block manifests by copying a template. If `security: false` is already in the template, it will be in every new manifest. Developers only need to change `false` to `true` when the block touches a security-critical surface. This is lower friction than remembering to add the field.

2. **Block-close checklist** — the checklist is the canonical gate for closing a block. Adding the security-review step here makes it impossible to close a security-critical block without having consciously addressed the gate (even if only to document that it was skipped with a reason, which would itself be visible and auditable).

---

## Changes Required

### Change 1 — `protocols/block-close-checklist.md`

Add the following step to the block-close checklist. It must be placed after the standard functional verification steps (tests pass, files match manifest) and before the final "mark block as closed" step. The step must be clearly conditional:

```
## Security Gate (conditional)

If the block's manifest has `security: true`:

1. Run `commands/security-review.md` against this block.
2. Record the result (PASS / WARN / FAIL) in the block's retrospective notes.
3. A FAIL result prevents block close. Resolve all FAIL findings and re-run the review.
4. A WARN result allows block close only if all warnings are explicitly acknowledged in writing with a named owner and rationale.
5. A PASS result allows block close with no additional action.

If the block's manifest has `security: false`: skip this step.
```

The wording above is normative. Adapt formatting to match the existing checklist style, but do not omit or weaken any of the five sub-steps.

### Change 2 — `templates/manifest-medium.md`

Add the following field to the frontmatter of the manifest-medium template, immediately after the `status:` field:

```yaml
security: false
```

The comment or inline documentation for this field (if the template uses inline comments) should read: `# set to true for blocks touching auth, networking, or persistent data`.

### Change 3 — `templates/manifest-large.md`

Apply the same change as Change 2. Add `security: false` immediately after the `status:` field, with the same inline comment.

### Change 4 — `templates/manifest-small.md`

Apply the same change as Changes 2 and 3. The small manifest template may have fewer frontmatter fields; place `security: false` after `status:` regardless of what other fields are present.

---

## Implementation Steps

1. Read `protocols/block-close-checklist.md` to understand the existing checklist structure and formatting conventions.
2. Add the Security Gate section to the checklist as described in Change 1. Match existing heading levels and list formatting.
3. Read `templates/manifest-medium.md`. Locate the `status:` line in the frontmatter. Insert `security: false` on the line immediately following it.
4. Read `templates/manifest-large.md`. Apply the same insertion.
5. Read `templates/manifest-small.md`. Apply the same insertion.
6. Verify all four files are modified and syntactically correct (YAML frontmatter must remain valid).

---

## Acceptance Criteria

- `protocols/block-close-checklist.md` contains the text "security-review" and a conditional step referencing `security: true`.
- `protocols/block-close-checklist.md` states that a FAIL result prevents block close.
- `templates/manifest-medium.md` frontmatter contains `security: false`.
- `templates/manifest-large.md` frontmatter contains `security: false`.
- `templates/manifest-small.md` frontmatter contains `security: false`.
- All four files remain syntactically valid after modification.
- `grep -q "security:" templates/manifest-medium.md` exits 0.
- `grep -q "security-review" protocols/block-close-checklist.md` exits 0.

---

## Phase Completion

Closing block-080 completes Phase 10. At that point:

- The five S axioms are in `PROTOCOLS.md` alongside P, Q, and C.
- `protocols/stack-addenda/security.md` provides concrete conventions for all stacks.
- `templates/threat-model.md` and `protocols/threat-model-generation.md` support S4 compliance.
- `commands/security-review.md` provides the executable S5 gate.
- The block-close checklist enforces the gate conditionally.
- All manifest templates default to `security: false`, making opt-in explicit and auditable.

Security is now a first-class concern in the architecture, not an afterthought.

---

## Notes

- This block is the final block in Phase 10 and the last dependency in the 10A→10B→10C→10D chain.
- The `security: false` default is intentional. Not every block touches security-critical surfaces. Defaulting to `true` would create review burden on documentation, refactoring, and tooling blocks that have no security surface. The opt-in model means the field's presence is universal (every manifest has it) while the gate is selective (only `security: true` blocks trigger the review).
- After this block closes, the Phase 10 exit criteria should be verified in full before the phase is marked complete.
