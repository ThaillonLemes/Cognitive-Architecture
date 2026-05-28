---
id: block-019
manifest: manifests/block-019-protocol-sub-agent-contract.md
status: done
gates_passed: 4/4
completed_at: 2026-05-21
agent: implementer
commit: -
duration_actual_days: 1
tok_estimated: ~4000
tok_src: estimated
---

# Block 019 Retrospective — Protocol: sub-agent-contract

## 1. What was built

- Created `protocols/sub-agent-contract.md`
- Defined 6-step sub-agent obligation sequence (parse → read → execute → gates → retro → return)
- Listed 6 prohibited actions with rationale
- Full return package format spec (all fields from `_syntax.md`)
- Status values table (5 states: done/partial/blocked/scope-exceeded/needs-decision)
- Gate failure protocol (evidence line format)
- Scope expansion protocol (behavior per scope:closed / open / two-phase)
- Failure escalation flow

## 2. Tests added

None. Doc-only block.

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| protocol-exists | ✓ | `protocols/sub-agent-contract.md` created |
| return-package-spec | ✓ | complete return package format with all fields and rules |
| lifecycle-defined | ✓ | 6-step lifecycle defined in obligation sequence |
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md updated |

## 4. Decisions made

None.

## 5. Deferred to future blocks

- Return package template → block-025
- Governor-side validation of return → block-021 (governor-dispatch)

## 6. Token estimate

```
tok_estimated: ~4000  tok_src:estimated
```

## 7. Issues / surprises

None.

## 8. Files actually touched

As manifest.

---

End of retrospective.
