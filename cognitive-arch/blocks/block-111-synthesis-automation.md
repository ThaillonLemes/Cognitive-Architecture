---
id: block-111
manifest: manifests/block-111-synthesis-automation.md
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

# Block 111 Retrospective — Synthesis automation

## 1. What was built

- Created `sdk/brainstorm_synthesis.py`: `QuestionResponse` and `SynthesisOutput` dataclasses; `ANSWER_ACCEPTED/MODIFIED/FREE_TEXT/NONE` constants; `_classify_response()` (case-insensitive match against recommended vs alternate vs free-text), `_accuracy_rate()`, `_topic_to_filename()` (safe slug for design/ path), `build_responses()` (pairs Question+Prediction+answer, handles missing predictions with placeholder), `render_design_doc()` (structured markdown: header, summary table with accuracy metrics, decisions table with source emojis, per-question details with rationale), `synthesize()` (main entry point, injectable now_ts), `write_design_doc()` (writes to design/<slug>.md, creates dir); CLI with `--answers-json` and `--stdout`.
- Created `sdk/tests/test_brainstorm_synthesis.py`: 36 tests.
- Created `protocols/brainstorm-synthesis.md`: answer types table, response input format, output structure, accuracy rate interpretation, invariants (no auto-commit, no silent drops, verbatim free-text), CLI usage, output path convention.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| test_classify_accepted | unit | pass |
| test_classify_accepted_case_insensitive | unit | pass |
| test_classify_modified_different_option | unit | pass |
| test_classify_free_text | unit | pass |
| test_classify_no_answer_empty | unit | pass |
| test_classify_no_answer_whitespace | unit | pass |
| test_topic_to_filename_simple | unit | pass |
| test_topic_to_filename_special_chars | unit | pass |
| test_topic_to_filename_hyphenated | unit | pass |
| test_accuracy_rate_all_accepted | unit | pass |
| test_accuracy_rate_none_accepted | unit | pass |
| test_accuracy_rate_no_answers | unit | pass |
| test_build_responses_returns_correct_count | unit | pass |
| test_build_responses_accepted | unit | pass |
| test_build_responses_missing_answer_is_none | unit | pass |
| test_build_responses_missing_prediction_uses_placeholder | unit | pass |
| test_render_design_doc_is_markdown | unit | pass |
| test_render_design_doc_contains_topic | unit | pass |
| test_render_design_doc_has_summary_section | unit | pass |
| test_render_design_doc_has_decisions_section | unit | pass |
| test_render_design_doc_has_details_section | unit | pass |
| test_render_design_doc_contains_answer | unit | pass |
| test_synthesize_returns_output | unit | pass |
| test_synthesize_topic_stored | unit | pass |
| test_synthesize_questions_total | unit | pass |
| test_synthesize_questions_answered | unit | pass |
| test_synthesize_accuracy_rate_all_accepted | unit | pass |
| test_synthesize_accuracy_rate_partial | unit | pass |
| test_synthesize_content_non_empty | unit | pass |
| test_synthesize_custom_timestamp | unit | pass |
| test_synthesize_design_path_contains_topic | unit | pass |
| test_synthesize_empty_questions | unit | pass |
| test_synthesize_all_accepted | unit | pass |
| test_write_design_doc_creates_file | unit | pass |
| test_write_design_doc_correct_path | unit | pass |
| test_write_design_doc_returns_path | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| synthesis-module | ✓ | `sdk/brainstorm_synthesis.py` + `protocols/brainstorm-synthesis.md` created |
| tests-pass | ✓ | 36/36 tests pass |
| dependencies-met | ✓ | block-109 done, block-110 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, this retrospective updated |

## 4. Decisions made

- **Verbatim free-text preservation**: synthesizer never modifies user's free-text answer — stored and rendered exactly as typed. Synthesis distortion risk (manifest §6.1) mitigated by this invariant.
- **No-answer questions not silently dropped**: questions with no response appear in output as "no answer provided." User can detect gaps.
- **`build_responses` handles missing predictions**: if a question has no entry in PredictionSet (possible if predictor was run against different question list), a low-confidence placeholder prediction is created. `synthesize()` is robust to mismatched question/prediction lists.
- **`accuracy_rate` denominator is answered-only**: no-answer questions don't reduce accuracy_rate — they're excluded. This correctly measures AI alignment when users actually respond.
- **Dead code fix**: initial version had a broken `accepted = [r for r in responded for responded in [answered]...]` list comprehension that was removed before the test run.

## 5. Token estimate

```
tok_estimated: ~1300  tok_src:estimated
```

## 6. Issues / surprises

Initial version had a dead-code list comprehension with a NameError (`responded` not in scope). Caught and removed before tests ran — all 36 tests passed first try after fix.

## 7. Files actually touched

- Created: `sdk/brainstorm_synthesis.py`, `sdk/tests/test_brainstorm_synthesis.py`, `protocols/brainstorm-synthesis.md`, this retrospective
- Modified: `INDEX.md`, `STATE.md`, `NEXT.md`, `blocks/BLOCK_LOG.md`, `board.md`, `phases/phase-17.md`

---

End of retrospective.
