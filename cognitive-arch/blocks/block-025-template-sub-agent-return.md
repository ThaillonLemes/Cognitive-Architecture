---
id: block-025
manifest: manifests/block-025-template-sub-agent-return.md
status: done
gates_passed: 4/4
completed_at: 2026-05-21
agent: implementer
commit: -
duration_actual_days: 1
tok_estimated: ~3000
tok_src: estimated
---

# Block 025 Retrospective — Template: sub-agent-return

## 1. What was built

- Created `templates/sub-agent-return.md`
- Base template with all required fields as placeholders with comments
- 4 status-specific examples: done, partial, blocked, scope-exceeded
- Field rules section (5 clarifying rules)
- `evidence:` line format for gate failures

## 2. Tests added

None. Doc-only block.

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| template-exists | ✓ | `templates/sub-agent-return.md` created |
| all-status-variants | ✓ | Examples for done, partial, blocked, scope-exceeded |
| required-fields | ✓ | All 14 required fields with placeholders and comments |
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md updated |

## 4. Decisions made

None.

## 5. Deferred to future blocks

None.

## 6. Token estimate

```
tok_estimated: ~3000  tok_src:estimated
```

## 7. Issues / surprises

None.

## 8. Files actually touched

As manifest.

---

End of retrospective.
