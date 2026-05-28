---
id: phase-17-retrospective
phase: phase-17
status: done
blocks: [block-108, block-109, block-110, block-111]
exit_criteria_met: 4/4
completed_at: 2026-05-27T00:00Z
duration_actual_days: 1
---

# Phase 17 Retrospective — Assertive Brainstorm v2

## 1. Exit criteria

| # | Criterion | Block | Result |
|---|-----------|-------|--------|
| 1 | `protocols/brainstorm-pattern.md` updated to v2 (or new coexisting v2 doc) | block-110 | ✓ |
| 2 | `sdk/brainstorm_context.py`: topic-based context loader → ContextBundle | block-108 | ✓ |
| 3 | `sdk/brainstorm_predictor.py`: per-question Prediction with confidence band | block-109 | ✓ |
| 4 | `templates/brainstorm-v2-questionnaire.md` + `sdk/brainstorm_synthesis.py` → design/<topic>.md | block-110 + 111 | ✓ |

## 2. What was built

**block-108 (Context loader):**
- `sdk/brainstorm_context_schema.py`: `RetroEntry`, `PatternEntry`, `RecommendationEntry`, `AdrEntry`, `StateSnapshot`, `ContextBundle` dataclasses.
- `sdk/brainstorm_context.py`: `load_context(topic) → ContextBundle`; keyword extraction, relevance scoring (frequency × recency weight), graceful degradation on missing files. 39 tests.

**block-109 (Prediction engine):**
- `sdk/prediction_schema.py`: `Question`, `Prediction` (confidence_band/score/rationale/evidence_sources), `PredictionSet`; `CONFIDENCE_HIGH/MED/LOW` per D10.
- `sdk/brainstorm_predictor.py`: `predict(question, context) → Prediction`; `predict_all() → PredictionSet`; evidence scoring (ADR=2×, retro=1×, pattern=1×); D10 confidence thresholds. 36 tests.

**block-110 (Questionnaire template):**
- `protocols/brainstorm-pattern-v2.md`: 3 principles (always recommend, variable options, open answers); confidence band table; session flow; v1 vs v2 table; quality invariants.
- `templates/brainstorm-v2-questionnaire.md`: annotated template with placeholder variables and example rendering.
- `protocols/brainstorm-pattern.md` updated: deprecation header pointing to v2.

**block-111 (Synthesis):**
- `sdk/brainstorm_synthesis.py`: `QuestionResponse`, `SynthesisOutput`; answer classification (accepted/modified/free_text/no_answer); `synthesize()` → `SynthesisOutput`; `render_design_doc()` → structured markdown (summary + decisions table + per-question details); `write_design_doc()` → `design/<slug>.md`. 36 tests.
- `protocols/brainstorm-synthesis.md`: synthesis procedure, invariants, CLI usage.

## 3. Tests added this phase

| Module | Tests |
|--------|-------|
| `sdk/brainstorm_context.py` | 39 |
| `sdk/brainstorm_predictor.py` | 36 |
| `sdk/brainstorm_synthesis.py` | 36 |
| **Total** | **111** |

## 4. Key decisions

- **Rule-based prediction (no LLM calls)**: stdlib-only constraint; also makes predictions deterministic and calibratable. ADRs weighted 2× for authority.
- **Confidence bands per D10**: high≥80%, med 50-80%, low<50%. Low explicitly labeled "AI guessing."
- **`brainstorm_context_schema.py` as separate module**: interface contract for blocks 109 and 111; prevents circular imports.
- **`recommendations` field reserved empty**: `governance/recommendations.md` is future; ContextBundle has the field but loader returns [].
- **`synthesize()` handles missing predictions**: if Question not in PredictionSet, creates low-confidence placeholder. Robust to partial session states.
- **v1 protocol kept**: `protocols/brainstorm-pattern.md` deprecated in place (not deleted) — existing v1 brainstorm artifacts remain valid.

## 5. Execution order

108 (17A) → 109 (17B) → 110 (17B, parallel) → 111 (17C)

Original plan: 109 and 110 in parallel. Executed sequentially per user constraint. All 4 blocks completed in 1 day.

## 6. Issues / surprises

Block-111: initial brainstorm_synthesis.py had a dead-code list comprehension with a NameError. Caught in code review before test run; fixed inline. All 36 tests passed first try after fix.

---

End of phase-17 retrospective.
