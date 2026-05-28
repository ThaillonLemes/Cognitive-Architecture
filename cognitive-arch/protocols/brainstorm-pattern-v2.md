# Protocol: Brainstorm Pattern v2
# Purpose: AI-led brainstorming with per-question recommendations, confidence bands, and open answers.
# Supersedes: protocols/brainstorm-pattern.md (v1)
# Created: block-110 (Phase 17)

---

## 1. Three Principles (v2 upgrade over v1)

### P1 — Always Recommend
For every question, the AI proposes the most probable answer based on project context
(recent retrospectives, detected patterns, related ADRs, current STATE). The recommendation
is explicit and labeled, never hidden or generic. User sees: *what AI proposes + why*.

### P2 — Variable Option Count
Questions may have 0, 2, 3, or 4+ options. There is no fixed count. The number of options
reflects the actual decision space:
- 0 options = open-answer (free-text only, no choices provided)
- 2 options = binary decision
- 3–4 options = typical multi-choice
- 5+ options = exploratory (user may merge or override)

### P3 — Open Answers Always Permitted
Per Q15: the user may always provide a free-text answer that is not one of the listed options.
The brainstorm template always shows an "Other (write your own)" field below the options.
AI synthesis handles free-text answers; they are never lost.

---

## 2. Confidence Bands (D10)

Every AI recommendation carries a confidence band:

| Band | Score | Meaning | Display |
|------|-------|---------|---------|
| `high` | ≥ 80% | Strong evidence in context; ADR or ≥3 corroborating items | 🟢 **High confidence** |
| `medium` | 50–80% | Some evidence; reasonable inference | 🟡 **Medium confidence** |
| `low` | < 50% | No direct evidence; AI is guessing | 🔴 **Low confidence — please override** |

Low-confidence recommendations are **always labeled** "AI guessing here." User should treat
them as placeholders and write their own answer.

---

## 3. Question Rendering Format

Each question in a v2 questionnaire renders as:

```markdown
### Q{n}. {Title}

**{Question text}**

🤖 **AI recommends:** {recommended_value}
📊 **Confidence:** {HIGH|MED|LOW — emoji + label}
💡 **Rationale:** {Evidence citation, e.g. "block-107, ADR-001 support 'pure function' approach."}

**Options:**
1. **{Option A}** {← AI pick if recommended}
2. **{Option B}**
3. **{Option C}** *(if variable count)*

> 💬 **Other (free text):** _______________
```

---

## 4. Session Flow

```
1. Load context:    brainstorm_context.load_context(topic) → ContextBundle
2. Generate questions: define Question list (from topic knowledge)
3. Predict all:     brainstorm_predictor.predict_all(questions, context) → PredictionSet
4. Render template: fill brainstorm-v2-questionnaire.md with predictions inline
5. User responds:   accepts predictions (1-click = "yes"), redirects, or free-texts
6. Synthesize:      brainstorm_synthesis.synthesize(responses, context) → design/<topic>.md
```

Steps 1–4 produce the questionnaire file at `_brainstorm/<topic>-v2-questionnaire.md`.
Steps 5–6 are user-driven; AI facilitates, never decides.

---

## 5. Difference from v1

| Aspect | v1 (deprecated) | v2 (current) |
|--------|-----------------|--------------|
| AI recommendation | "(Recommended)" note, optional | Always present, never optional |
| Confidence | Not shown | Explicit: high/medium/low per D10 |
| Option count | Fixed (usually 3-4) | Variable (0 to N) |
| Open answers | Mentioned but not enforced | Template always shows free-text field |
| Context loading | Manual (AI reads from memory) | Automated (`brainstorm_context.load_context()`) |
| Synthesis | Manual AI → design doc | Automated via `brainstorm_synthesis.py` (block-111) |

---

## 6. Implementation Modules

| Module | Role |
|--------|------|
| `sdk/brainstorm_context.py` | Context loader: gathers retros, patterns, ADRs, state |
| `sdk/brainstorm_context_schema.py` | ContextBundle, RetroEntry, PatternEntry, etc. |
| `sdk/brainstorm_predictor.py` | Prediction engine: predict() → Prediction with confidence |
| `sdk/prediction_schema.py` | Question, Prediction, PredictionSet dataclasses |
| `sdk/brainstorm_synthesis.py` | Synthesis automation (block-111) |
| `templates/brainstorm-v2-questionnaire.md` | Template for rendering a session |

---

## 7. Quality Invariants

- Every question MUST have an AI recommendation before the user responds.
- Confidence band MUST be shown alongside every recommendation.
- Low-confidence recommendations MUST be labeled "AI guessing here."
- The template MUST always show an open-answer option below the options list.
- User's free-text answer MUST be preserved verbatim in synthesis input.
- AI NEVER decides — it recommends and explains; the user confirms or redirects.

---

## 8. Example: One Question

```markdown
### Q1. How should dependencies between blocks be tracked?

**AI recommends:** Manifest `dependencies:` field + resolver automation
📊 **Confidence:** 🟢 High (block-107, protocols/dependency-resolution.md)
💡 **Rationale:** Strong evidence in context (block-107) that manifest-based tracking
    with automated resolution (dependency_resolver.py) is established practice.

**Options:**
1. **Manifest `dependencies:` + automated resolver** ← AI pick
2. **Manual board.md updates only**
3. **External task tracker (GitHub Issues, etc.)**

> 💬 **Other (free text):** _______________
```

---

## 9. File Locations

| File | Path |
|------|------|
| Questionnaire scratchpad | `_brainstorm/<topic>-v2-questionnaire.md` |
| Synthesized design doc | `design/<topic>.md` |
| ADR outputs | `decisions/ADR-NNN-<title>.md` |

---

End of brainstorm-pattern-v2.
