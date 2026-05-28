---
id: block-008
manifest: manifests/block-008-retrospective-token-fields.md
status: done
gates_passed: 2/2
completed_at: 2026-05-21T00:00Z
agent: main-session
commit: -
duration_actual_days: 0
tok_estimated: ~200
tok_src: estimated
---

# Block 008 Retrospective — Retrospective template — token fields

## 1. What was built

- Added `tok_estimated: ~<NNN>` and `tok_src: estimated` to the YAML frontmatter block in `templates/block-retrospective.md`.
- Added new **Section 6 — Token estimate** with a per-file table and `tok_estimated:` summary line.
- Renumbered former Section 6 (Issues/surprises) → Section 7, and former Section 7 (Files actually touched) → Section 8.
- Inline comment on `tok_src:` explains that `actual` requires Phase 5 SDK.

## 2. Tests added

None (doc-only block).

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| tok-fields-present | ✓ | frontmatter has `tok_estimated:` and `tok_src:` |
| files-updated | ✓ | BLOCK_LOG.md updated at phase close |

## 4. Decisions made

- Chose to add tok fields to frontmatter AND as a body section (not just one location). Frontmatter for machine-parsing; body section for human guidance on how to fill it.

## 5. Deferred to future blocks

- SDK actual token measurement → Phase 5

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| templates/block-retrospective.md | ~3,200 | ~800 |
| _syntax.md | ~5,400 | ~1,350 |

```
tok_estimated: ~200  tok_src:estimated
```

## 7. Issues / surprises

None.

## 8. Files actually touched

- Modified: templates/block-retrospective.md (frontmatter + new section 6 + section renumbering)
- Otherwise as manifest.
