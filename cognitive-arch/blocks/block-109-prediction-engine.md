---
id: block-109
manifest: manifests/block-109-prediction-engine.md
status: done
gates_passed: 4/4
completed_at: 2026-05-27T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 1
duration_source: estimated
tok_estimated: ~1300
tok_src: estimated
---

# Block 109 Retrospective — Prediction engine

## 1. What was built

- Created `sdk/prediction_schema.py`: `Question` (id, text, topic, options, default, allow_free_text), `Prediction` (question_id, recommended_value, confidence_band, confidence_score, rationale, alternative_options, evidence_sources; `is_high_confidence` and `is_guessing` properties), `PredictionSet` (topic, generated_at, predictions, context_retro_count, context_pattern_count; `by_id()` method). `CONFIDENCE_HIGH/MED/LOW` constants per D10.
- Created `sdk/brainstorm_predictor.py`: `_count_occurrences()`, `_score_option()` (keyword hit count weighted: ADR=2×, retro=1×, pattern=1×; deduplicates sources), `_compute_confidence()` (D10 thresholds: score≥3 → high; 1-2 → medium; 0 → low), `_build_rationale()` (cites sources; flags low-confidence as "AI guessing"), `predict(question, context) → Prediction` (options-based and open-answer paths), `predict_all(questions, context, now_ts) → PredictionSet`. Pure function design; no LLM calls; stdlib-only.
- Created `sdk/tests/test_brainstorm_predictor.py`: 36 tests.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| test_count_occurrences_found | unit | pass |
| test_count_occurrences_multiple | unit | pass |
| test_count_occurrences_case_insensitive | unit | pass |
| test_count_occurrences_not_found | unit | pass |
| test_count_occurrences_empty_needle | unit | pass |
| test_score_option_retro_match | unit | pass |
| test_score_option_no_match | unit | pass |
| test_score_option_adr_double_weight | unit | pass |
| test_score_option_pattern_match | unit | pass |
| test_score_option_deduplicates_sources | unit | pass |
| test_compute_confidence_high_score | unit | pass |
| test_compute_confidence_medium_score | unit | pass |
| test_compute_confidence_zero_score | unit | pass |
| test_compute_confidence_no_evidence | unit | pass |
| test_compute_confidence_score_2_evidence_3_is_high | unit | pass |
| test_predict_returns_prediction | unit | pass |
| test_predict_question_id_stored | unit | pass |
| test_predict_confidence_band_valid | unit | pass |
| test_predict_recommended_is_one_of_options | unit | pass |
| test_predict_best_option_first | unit | pass |
| test_predict_alternative_options_excludes_recommended | unit | pass |
| test_predict_rationale_non_empty | unit | pass |
| test_predict_evidence_sources_populated | unit | pass |
| test_predict_open_answer_no_options | unit | pass |
| test_predict_open_answer_empty_context | unit | pass |
| test_predict_low_confidence_flags_guessing | unit | pass |
| test_prediction_is_high_confidence | unit | pass |
| test_prediction_is_guessing | unit | pass |
| test_predict_all_returns_prediction_set | unit | pass |
| test_predict_all_correct_count | unit | pass |
| test_predict_all_topic_matches_context | unit | pass |
| test_predict_all_generated_at_present | unit | pass |
| test_predict_all_retro_count | unit | pass |
| test_predict_all_by_id | unit | pass |
| test_predict_all_by_id_missing | unit | pass |
| test_predict_all_custom_timestamp | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| predictor-module | ✓ | `sdk/brainstorm_predictor.py` + `sdk/prediction_schema.py` created |
| tests-pass | ✓ | 36/36 tests pass |
| dependencies-met | ✓ | block-108 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, this retrospective updated |

## 4. Decisions made

- **Rule-based, no LLM**: prediction is pure keyword-frequency over context bundle. No API calls, no randomness, deterministic output. Rationale: stdlib-only constraint; also makes confidence bands calibratable against ground-truth answers.
- **ADR weight = 2×**: Architectural Decision Records represent committed decisions; they are more authoritative than retrospective observations or patterns. A single ADR mention outweighs a pattern mention.
- **Open-answer path**: when `question.options` is empty, predictor synthesizes from best retro title. Low confidence by default unless context is rich. Flags as "AI guessing" when no retro available.
- **`alternative_options` from scored list**: only non-zero-scored options included as "alternatives" unless none exist (then all others returned). Ensures user sees genuinely competing options.

## 5. Token estimate

```
tok_estimated: ~1300  tok_src:estimated
```

## 6. Issues / surprises

None.

## 7. Files actually touched

- Created: `sdk/prediction_schema.py`, `sdk/brainstorm_predictor.py`, `sdk/tests/test_brainstorm_predictor.py`
- Modified: `INDEX.md`, `STATE.md`, `NEXT.md`, `blocks/BLOCK_LOG.md`, `board.md`

---

End of retrospective.
