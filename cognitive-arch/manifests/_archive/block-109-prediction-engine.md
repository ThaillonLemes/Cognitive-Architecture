---
id: block-109
tier: M
kind: implementation
phase: phase-17
scope: phase-bound
status: pending
security: false
dependencies: [block-108]
files:
  read:
    - sdk/brainstorm_context.py
    - sdk/brainstorm_context_schema.py
    - design/arch-v3.md
    - _brainstorm/v3-evolution-questionnaire.md
  modify: []
  create:
    - sdk/brainstorm_predictor.py
    - sdk/tests/test_brainstorm_predictor.py
    - sdk/prediction_schema.py
gates:
  - name: predictor-module
    type: file-changed
    paths: [sdk/brainstorm_predictor.py, sdk/prediction_schema.py]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_brainstorm_predictor.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-108]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-109-prediction-engine.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 109 — Prediction engine

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

For each brainstorm question, given context bundle from block-108, generate a Prediction record: recommended option (or free-text recommendation), confidence band (high ≥80%, med 50-80%, low <50% per D10), and rationale citing evidence from the context.

## 2. Dependencies

- block-108 (context bundle is input)

## 3. Files

- **Read:** context module + schema, arch-v3, the v3-evolution questionnaire (test corpus — predictor will be validated against your actual answers)
- **Modify:** —
- **Create:** `sdk/brainstorm_predictor.py`, test file, `sdk/prediction_schema.py`

## 4. Validation

- Predictor exposes: `predict(question: Question, context: ContextBundle) -> Prediction`
- Prediction includes: recommended_value, confidence_band, rationale (citing specific evidence), alternative_options
- Confidence bands: high ≥80% (strong evidence), medium 50-80%, low <50% (AI flags as guessing)
- Retrospective test: run against v3-evolution questionnaire, measure agreement with actual recorded user answers; target ≥60% match for high-confidence predictions

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Predictions anchor user toward wrong answer | High | Confidence band visible; rationale exposed; user always has open-answer option (Q15 principle) |
| Confidence overestimated | Med | Conservative thresholds; calibration tested against ground-truth questionnaire |
| Predictions become formulaic | Med | Each prediction includes evidence — user can detect when AI is just pattern-matching |

## 7. Out of Scope

- ML-trained predictor (rule-based + LLM-context-use sufficient for v1)
- Multi-question dependency awareness (each question predicted independently for v1)
- User-feedback learning loop (future enhancement)

## 8. New Abstraction

`Prediction` dataclass. Justification: consumed by questionnaire template (block-110), synthesis (block-111), Master Agent (for future brainstorm orchestration). Rule of Three met.
