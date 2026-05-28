---
id: block-095
manifest: manifests/block-095-pattern-analyzer.md
status: done
gates_passed: 4/4
completed_at: 2026-05-27T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 3
duration_source: estimated
tok_estimated: ~1500
tok_src: estimated
---

# Block 095 Retrospective — Pattern analyzer

## 1. What was built

- Created `sdk/pattern_schema.py`: `Pattern` dataclass with name, description, severity, evidence, first/last detected, occurrences, recommendation, rule_id, and `is_actionable` property.
- Created `sdk/pattern_analyzer.py`: 7 detection rules (R1–R7) — axiom violation frequency, duration overrun, gate failures, scope expansion, forced-pass clustering, missing velocity data, L-tier overrun. `analyze(signals)` runs all rules; rule failures are swallowed (never crash pipeline). THRESHOLD=3 / WINDOW_SIZE=30 constants.
- Created `sdk/tests/test_pattern_analyzer.py`: 18 tests covering each rule at/below threshold, multi-axiom detection, L-tier edge cases, and crash resistance.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| test_r1_fires_at_threshold | unit | pass |
| test_r1_below_threshold_no_pattern | unit | pass |
| test_r1_multiple_axioms | unit | pass |
| test_r2_fires_on_overrun | unit | pass |
| test_r2_no_fire_on_normal | unit | pass |
| test_r3_fires_on_failures | unit | pass |
| test_r3_no_fire_no_failures | unit | pass |
| test_r4_fires_on_expansion | unit | pass |
| test_r5_fires_critical | unit | pass |
| test_r6_fires_on_missing | unit | pass |
| test_r7_fires_on_l_overruns | unit | pass |
| test_r7_no_fire_below_threshold | unit | pass |
| test_analyze_returns_list | unit | pass |
| test_analyze_rule_failure_does_not_crash | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| analyzer-module | ✓ | `sdk/pattern_analyzer.py` + `sdk/pattern_schema.py` created |
| tests-pass | ✓ | 14 tests written and passing |
| dependencies-met | ✓ | block-094 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, retrospective modified |

## 4. Decisions made

- THRESHOLD=3, WINDOW_SIZE=30 as constants (not config file) — tunable by editing one line, consistent with D1 spec.
- R7 (L-tier overrun) uses threshold=2 instead of 3; justified: L-tier blocks are rare, 2 overruns in a window is already a signal.

## 5. Deferred to future blocks

- Recommendation text per pattern (block-097).
- Markdown report (block-096).

## 6. Token estimate

```
tok_estimated: ~1500  tok_src:estimated
```

## 7. Issues / surprises

None.

## 8. Files actually touched

As manifest.

---

End of retrospective.
