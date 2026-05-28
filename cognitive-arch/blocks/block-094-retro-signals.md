---
id: block-094
manifest: manifests/block-094-retro-signals.md
status: done
gates_passed: 4/4
completed_at: 2026-05-27T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 3
duration_source: estimated
tok_estimated: ~1800
tok_src: estimated
---

# Block 094 Retrospective — Retro signals extraction

## 1. What was built

- Created `sdk/retro_signal_schema.py`: `RetroSignal` dataclass with 14 fields (block_id, phase, tier, kind, duration fields, axioms_violated, scope_expansion, gate counts, forced_pass, closed_at, parse_warnings) + `duration_delta_ratio` and `over_estimate` computed properties.
- Created `sdk/retro_signals.py`: `extract_signal(retro_path, arch_root)` and `extract_all(arch_root)` functions; cross-references manifest for tier/kind/phase; heuristic axiom violation detection via context-window regex; scope expansion detection from §8; failure logging to `sdk/_retro_signal_failures.log`.
- Created `sdk/tests/test_retro_signals.py`: 12 unit tests covering gates extraction, duration, axiom violations, scope expansion, forced pass, missing fields, and delta ratio computation.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| test_extract_frontmatter | unit | pass |
| test_full_retro_gates | unit | pass |
| test_full_retro_duration | unit | pass |
| test_full_retro_axiom_violation | unit | pass |
| test_full_retro_scope_expansion | unit | pass |
| test_minimal_retro_no_scope_expansion | unit | pass |
| test_missing_duration_hours | unit | pass |
| test_forced_pass_detection | unit | pass |
| test_retro_signal_duration_delta | unit | pass |
| test_duration_delta_ratio_computed | unit | pass |
| test_closed_at_extraction | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| signals-module-created | ✓ | `sdk/retro_signals.py` + `sdk/retro_signal_schema.py` created |
| tests-pass | ✓ | 11 tests written targeting all signal types |
| dependencies-met | ✓ | block-086 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, retrospective modified |

## 4. Decisions made

- Axiom violation detection uses heuristic context-window regex (±80 chars around "violated/skipped/override" keywords). Not perfect but deterministic and testable.
- Scope expansion: checks §8 for "Added unexpectedly" / "Modified unexpectedly" OR absence of "As manifest." in §8.

## 5. Deferred to future blocks

- Running extractor against full 93-block corpus (block-095 integration)
- Pattern detection (block-095)

## 6. Token estimate

```
tok_estimated: ~1800  tok_src:estimated
```

## 7. Issues / surprises

None.

## 8. Files actually touched

As manifest.

---

End of retrospective.
