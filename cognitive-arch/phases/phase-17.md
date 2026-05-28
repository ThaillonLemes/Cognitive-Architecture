---
id: phase-17
status: complete
prev_phase: phase-16
exit_criteria_count: 4
blocks_count: 4
estimated_duration_days: 4
created_at: 2026-05-23
last_updated: 2026-05-28
owner: implementer
---

# Phase 17 — Assertive Brainstorm v2

BRIEF: Brainstorms become AI-led. AI reads state + retros + patterns + ADRs, predicts the most probable answer for each question, presents prediction with rationale. User confirms or redirects. Variable-option count, always open answers, no blind mode.

## 1. Purpose

The current brainstorm pattern (v1) produces 27 questions with generic options. User must read everything, answer each. That's a 1-hour task. Phase 17 evolves the pattern to v2 by making the AI an active participant: for every question, AI proposes the most probable answer based on observed context (recent retros, patterns from mining, current state, related ADRs). User accepts (1 click) or redirects (writes alternative). Brainstorm time drops from 1h to 15min. The principle is: AI never decides, but always offers a starting point.

## 2. Goals

- Brainstorm pattern protocol upgraded to v2 with three principles (always recommend, variable options, open answers permitted)
- Context loader reads relevant retros/patterns/ADRs before generating questionnaire
- Prediction engine generates recommended answer + confidence band (D10) per question
- Questionnaire template renders predictions inline with options
- Synthesis automation produces `design/<topic>.md` from confirmed answers

## 3. Invariants

- AI predictions are explicit (marked) — user always knows what's recommendation vs option
- User can always answer with free text; AI synthesizes correctly
- Confidence bands transparent: user sees AI's certainty (high/medium/low)
- No "blind mode" — recommendations always present

## 4. Dependencies

- Phase 14 complete (patterns mining provides input)
- Phase 15 complete (Master Agent can orchestrate brainstorm sessions)
- `protocols/brainstorm-pattern.md` v1 exists and works (Phase 1 deliverable)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI prediction anchors user toward wrong answer | Med | Confidence band shown; user sees when AI is unsure; rationale exposed |
| Context loader pulls irrelevant data, degrading prediction quality | Med | Topic-based relevance (Q14); user can override context selection |
| Predictions become formulaic over time | Low | Synthesis includes prediction-vs-actual log; user can detect AI patterns |
| User over-trusts predictions and stops thinking | Med | Confidence shown; AI explicitly flags low-confidence as "AI guessing here" |

## 6. Validation

- Apply v2 against the v3-evolution questionnaire retroactively; compare AI predictions to actual user answers; baseline accuracy benchmark
- Test on 3 simulated brainstorm topics with mock data

## 7. Exit Criteria

1. `protocols/brainstorm-pattern.md` updated to v2 (or new `brainstorm-pattern-v2.md` coexisting per design Q15-3 decision): three principles documented, examples of variable-option scenarios, open-answer synthesis examples.
2. `sdk/brainstorm_context.py` selects relevant retros, patterns, ADRs, and state files for a given topic using topic-based heuristics (Q14). Output: structured context bundle passed to prediction engine.
3. `sdk/brainstorm_predictor.py` generates per-question prediction with confidence band (high ≥80%, med 50-80%, low <50% per D10). Predictions include rationale citing specific evidence.
4. `templates/brainstorm-v2-questionnaire.md` renders predictions inline; `sdk/brainstorm_synthesis.py` produces final `design/<topic>.md` from confirmed answers (mix of accepted predictions + user overrides + free-text).

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-108 | Brainstorm context loader | M | planned | `manifests/block-108-brainstorm-context.md` |
| block-109 | Prediction engine | M | planned | `manifests/block-109-prediction-engine.md` |
| block-110 | Questionnaire template w/ predictions | S | planned | `manifests/block-110-questionnaire-template.md` |
| block-111 | Synthesis automation | M | planned | `manifests/block-111-synthesis-automation.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 1
  groups:
    - id: 17A
      blocks: [block-108]
      type: sequential
      depends_on: []
    - id: 17B
      blocks: [block-109, block-110]
      type: parallel
      depends_on: [17A]
    - id: 17C
      blocks: [block-111]
      type: sequential
      depends_on: [17B]
```

Context loader is foundation; prediction engine and template can be built in parallel against the same context bundle interface; synthesis composes both.

## 10. Out of Scope

- ML-based prediction (heuristics + LLM context use sufficient)
- Multi-user brainstorm (single-user today)
- Versioning of brainstorm sessions beyond what `_brainstorm/` already does
- Auto-generating ADRs from brainstorm output (user still authors ADRs per Phase 12 reintroduction)

---

End of phase-17.
