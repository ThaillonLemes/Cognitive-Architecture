---
id: block-087
manifest: manifests/block-087-adr-reintroduction.md
status: done
gates_passed: 2/2
completed_at: 2026-05-27T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 1
duration_source: estimated
tok_estimated: ~1200
tok_src: estimated
---

# Block 087 Retrospective — ADR reintroduction

## 1. What was built

- Created `decisions/ADR-003-tier-system-S-M-L.md`: documents the three-tier manifest system decision (phase-2 origin), alternatives considered, and consequences. Marked `backfilled: true`.
- Created `decisions/ADR-004-governor-v2-python-sdk.md`: documents the Python stdlib-only SDK adoption decision (phase-4 origin), alternatives (TS, Bash, external orchestration). Marked `backfilled: true`.
- Created `decisions/ADR-005-group-m-axioms-split.md`: documents the decision to keep Group M axioms in the MMORPG application layer only, not in the canonical source. Marked `backfilled: true`.

## 2. Tests added

None — doc-only block.

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| three-adrs-created | ✓ | ADR-003, ADR-004, ADR-005 created in `decisions/` |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-087-adr-reintroduction.md modified |

## 4. Decisions made

None requiring new ADRs (this block IS the ADR creation).

## 5. Deferred to future blocks

- Remaining historical decisions (only top-3 by consequence were backfilled per manifest scope).
- ADR template update (Phase 13).

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `templates/ADR.md` | ~1,100 | ~275 |
| `decisions/ADR-001-structure-option-a.md` | ~1,500 | ~375 |
| `PROTOCOLS.md` | ~4,200 | ~1,050 |

```
tok_estimated: ~1700  tok_src:estimated
```

## 7. Issues / surprises

- Group M context required reading PROTOCOLS.md to confirm it does NOT appear in canonical source (P/Q/C/S only). The ADR correctly documents the split decision.

## 8. Files actually touched

As manifest.

---

End of retrospective.
