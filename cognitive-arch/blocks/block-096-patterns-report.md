---
id: block-096
manifest: manifests/block-096-patterns-report.md
status: done
gates_passed: 3/3
completed_at: 2026-05-27T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 1
duration_source: estimated
tok_estimated: ~800
tok_src: estimated
---

# Block 096 Retrospective — patterns.md generator

## 1. What was built

- Created `sdk/patterns_report.py`: `render(patterns)` → markdown string; `write_report(patterns, arch_root)` → writes `governance/patterns.md`. Severity ordering (critical→warn→info), emoji labels, top-5 summary table, full detail section per pattern with evidence block list and recommendation field. Deterministic output.
- Generated initial `governance/patterns.md` from current corpus: one INFO pattern detected (velocity-data-gap across all 85 pre-block-086 blocks). Noted as expected/exempt.

## 2. Tests added

None — S-tier block; determinism testable by visual inspection.

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| report-generator-created | ✓ | `sdk/patterns_report.py` + `governance/patterns.md` created |
| dependencies-met | ✓ | block-095 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, retrospective modified |

## 4. Decisions made

- Top-5 summary table in addition to full detail sections: gives fast overview without scrolling entire file.
- `governance/patterns.md` is overwrite-only (not versioned). Historical patterns visible via git log.

## 5. Deferred to future blocks

- Recommendation text in patterns.md (populated by block-097 engine).
- HTML version of patterns (Phase 16 dashboard).

## 6. Token estimate

```
tok_estimated: ~800  tok_src:estimated
```

## 7. Issues / surprises

Initial run shows 85-block velocity-data-gap which is expected (all pre-block-086). No false positives.

## 8. Files actually touched

As manifest.

---

End of retrospective.
