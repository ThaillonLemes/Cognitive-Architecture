---
id: block-020
manifest: manifests/block-020-protocol-convention-snippet.md
status: done
gates_passed: 4/4
completed_at: 2026-05-21
agent: implementer
commit: -
duration_actual_days: 1
tok_estimated: ~5000
tok_src: estimated
---

# Block 020 Retrospective — Protocol: convention-snippet-generation

## 1. What was built

- Created `protocols/convention-snippet-generation.md`
- Defined block-kind to axiom mapping table (7 kinds: doc-only, refactor, enhancement, bugfix, feature, gate, discovery)
- Specified core vs optional axiom sets per kind with sorting rule (P→Q→C)
- Documented snippet format: `axioms:` header field + snippet body (one line per axiom)
- Defined 7-step Governor generation procedure
- Staleness detection via PROTOCOLS.md hash in governor-state.md
- Manual fallback for non-SDK sessions

## 2. Tests added

None. Doc-only block.

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| protocol-exists | ✓ | `protocols/convention-snippet-generation.md` created |
| mapping-table | ✓ | 7-kind table with core and optional axiom columns |
| snippet-format | ✓ | `axioms:K,K,...` format documented with example |
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md updated |

## 4. Decisions made

None requiring ADR. Added `gate` and `discovery` kinds to mapping table (present in design/governor-v2.md §4 but not in manifest spec) — harmonizes the two references.

## 5. Deferred to future blocks

None beyond phase-4 scope.

## 6. Token estimate

```
tok_estimated: ~5000  tok_src:estimated
```

## 7. Issues / surprises

Manifest mapping table used `enhancement/bugfix/feature` as kinds; design/governor-v2.md §4 used `implementation/gate/discovery`. Reconciled by including all 7 kinds in the protocol's table.

## 8. Files actually touched

As manifest.

---

End of retrospective.
