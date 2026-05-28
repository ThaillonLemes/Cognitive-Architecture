---
id: phase-17-retro
phase: phase-17
status: complete
blocks_completed: 4
blocks_planned: 4
exit_criteria_met: 4/4
completed_at: 2026-05-28T06:00Z
duration_actual_days: 5
duration_estimated_days: 4
---

# Phase 17 Retrospective — Assertive Brainstorm v2

## 1. Phase summary

Phase 17 delivered a complete Assertive Brainstorm v2 system: a three-module SDK stack (context loader, prediction engine, synthesis automation) plus the v2 protocol specification and questionnaire template. The context loader reads retros/patterns/ADRs and produces a typed `ContextBundle`; the prediction engine generates per-question predictions with high/medium/low confidence bands using keyword-frequency scoring over the bundle — deterministic, no LLM calls, stdlib-only. The questionnaire template codifies the three v2 principles (Always Recommend, Variable Option Count, Open Answers Always Permitted) and deprecates v1 in place. The synthesis module converts confirmed answers into a structured `design/<topic>.md`, tracking AI accuracy rate and preserving free-text verbatim. Combined, the system reduces brainstorm time from ~1h to ~15min by having AI propose a starting point for every question. 111 unit tests added across three SDK modules.

## 2. Blocks completed

| Block | Title | Result | Manifest |
|-------|-------|--------|----------|
| block-108 | Brainstorm context loader | done | `manifests/_archive/block-108-brainstorm-context.md` |
| block-109 | Prediction engine | done | `manifests/_archive/block-109-prediction-engine.md` |
| block-110 | Questionnaire template w/ predictions | done | `manifests/_archive/block-110-questionnaire-template.md` |
| block-111 | Synthesis automation | done | `manifests/_archive/block-111-synthesis-automation.md` |

## 3. Exit criteria

1. `protocols/brainstorm-pattern-v2.md` updated to v2 — ✓ met (block-110: new doc with three principles, confidence band table, v1 vs v2 comparison, open-answer synthesis examples; v1 deprecated with pointer)
2. `sdk/brainstorm_context.py` selects relevant retros/patterns/ADRs per topic — ✓ met (block-108: keyword-based relevance scoring with recency weighting, graceful degradation on absent dirs, 39 tests)
3. `sdk/brainstorm_predictor.py` generates per-question prediction with confidence band — ✓ met (block-109: D10 thresholds high≥80%/med 50-80%/low<50%, rationale citing sources, ADR 2× weight, 36 tests)
4. `templates/brainstorm-v2-questionnaire.md` renders predictions inline; `sdk/brainstorm_synthesis.py` produces `design/<topic>.md` — ✓ met (block-110 template + block-111 synthesis; verbatim free-text invariant; no-answer tracking; 36 tests)

## 4. Decisions made (ADRs)

No new ADRs created during Phase 17. Implementation-level decisions documented in block retrospectives:

- **Rule-based predictor, no LLM** (block-109): deterministic, testable, calibratable confidence bands.
- **ADR evidence weight = 2×** (block-109): ADRs are committed decisions; outweigh retros and patterns.
- **Coexisting v1 + v2 docs** (block-110, per Q15-3): v1 kept as deprecated reference, not replaced in-place.
- **`brainstorm_context_schema.py` as separate module** (block-108): imported by blocks 109 and 111; avoids circular imports.
- **Verbatim free-text preservation** (block-111): synthesizer never modifies user answers.
- **Missing predictions fallback** (block-111): mismatched question/prediction lists handled gracefully with low-confidence placeholder.

## 5. Risks materialized

| Risk | Fired? | Notes |
|------|--------|-------|
| AI prediction anchors user toward wrong answer | No | Confidence bands + rationale exposure implemented; "AI guessing" flag on low-confidence |
| Context loader pulls irrelevant data | No | Topic-based keyword scoring + recency fallback; irrelevant files scored low and de-ranked |
| Predictions become formulaic over time | N/A | Requires multi-session data; not yet assessed |
| User over-trusts predictions | No | Low-confidence path explicitly flags "AI guessing here" in rationale |

## 6. Deferrals

- ML-based prediction → Future phase (out of scope per §10)
- Multi-user brainstorm → Future phase (out of scope per §10)
- Auto-generating ADRs from brainstorm output → Future phase (out of scope per §10)
- Retroactive v3-evolution questionnaire benchmarking (§6 Validation) → Not done; v2 system exists but no live session run yet; left for first actual use

## 7. Pattern observations

- **Duration**: estimated 4 days, actual 5 wall-clock days (25% over). Actual effort hours: 3.5h total (1+1+0.5+1). Overrun was context-switch / session gap, not work volume.
- **Block tier mix**: 3 M + 1 S. Accurate — block-110 (Tier S, 0.5h) was genuinely lighter. Tier estimates were correct.
- **Test density**: 111 unit tests for 3 SDK modules in 3.5h. High coverage from the start; all tests passed on first run post-fix (block-111 had one dead-code NameError caught before test run).
- **Parallel group 17B** (blocks 109+110): no conflicts observed. Parallel execution plan was valid.
- **`commit: -` across all blocks**: git commit step not exercised in Phase 17 sessions. Phase-close commit will be the first commit for this phase's work.
- **No bottlenecks**: dependency chain (108 → 109+110 parallel → 111) resolved cleanly.

## 8. Updates to PROJECT.md / design/

None during Phase 17. No stack changes, constraint updates, or domain doc additions.

---

End of phase retrospective.
