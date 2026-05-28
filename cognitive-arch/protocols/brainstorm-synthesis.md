# Protocol: Brainstorm Synthesis
# Purpose: Procedure for converting user responses to a design document via brainstorm_synthesis.py.
# Part of: Brainstorm v2 flow (protocols/brainstorm-pattern-v2.md)
# Created: block-111 (Phase 17)

---

## 1. Overview

Synthesis is the final step of a Brainstorm v2 session. It takes the filled questionnaire
(questions + predictions + user responses) and produces `design/<topic>.md` — a structured
markdown document with a decisions table, per-question rationale, and accuracy summary.

```
brainstorm_context.load_context(topic)
    → ContextBundle

brainstorm_predictor.predict_all(questions, context)
    → PredictionSet

[User reviews and responds]

brainstorm_synthesis.synthesize(topic, questions, predictions, answers)
    → SynthesisOutput

brainstorm_synthesis.write_design_doc(output, arch_root)
    → design/<topic>.md
```

---

## 2. Answer Types

| Type | Code | Description | Example |
|------|------|-------------|---------|
| Accepted | `accepted` | User chose the AI recommendation verbatim | "manifest-based" = AI pick |
| Modified | `modified` | User chose a different listed option | "manual" instead of "manifest-based" |
| Free text | `free_text` | User wrote their own answer not in the list | "use a custom registry with TTL" |
| No answer | `no_answer` | No response provided | *(blank)* |

All types are preserved verbatim in the output design document.

---

## 3. Response Input Format

Responses are passed as `dict[str, str]` mapping question IDs to answer text:

```python
answers = {
    "Q1": "manifest-based",          # accepted (matches AI recommendation)
    "Q2": "class-based",             # modified (different option)
    "Q3": "LRU with 1h TTL on STATE.md hash",  # free text
    # "Q4" not provided              # treated as no_answer
}
```

---

## 4. Output Structure

`design/<topic>.md` contains:

```markdown
# Design: <topic>

## Summary
| Metric | Value |
| Questions total | N |
| Answered | N |
| AI predictions accepted | N (X%) |
| Modified answers | N |
| Free-text answers | N |

## Decisions Table
| ID | Question | Decision | Source | Confidence |
| Q1 | How should... | manifest-based | ✅ | 🟢 |

## Decision Details
### Q1 — How should dependencies be tracked?
**Decision:** manifest-based
**Source:** Accepted AI recommendation
**AI predicted:** manifest-based (🟢 High)
**AI rationale:** block-107 and ADR-001 support manifest-based approach.
```

---

## 5. Accuracy Rate

`SynthesisOutput.accuracy_rate` = (questions accepted) / (questions answered).

This is a measure of how well the AI's predictions aligned with user intent. It is NOT a
quality metric — a low accuracy rate simply means the user had strong opinions that differed
from the AI's evidence-based inferences.

Typical accuracy rates:
- > 70%: Context was highly relevant; good evidence alignment
- 40-70%: Mixed alignment; some domain-specific choices
- < 40%: Topic was novel or AI evidence was outdated

---

## 6. Invariants

- User's free-text answer is NEVER modified by the synthesizer — preserved verbatim.
- No-answer questions are included in output as "no answer provided" — not silently dropped.
- The design doc is for review before committing — user must check before `git add design/<topic>.md`.
- Synthesis does NOT auto-create ADRs (user authors ADRs separately per Phase 12 protocol).
- Synthesis does NOT overwrite a design doc without user awareness (write_design_doc is explicit).

---

## 7. CLI Usage

```bash
# Synthesize from a JSON answers file
python sdk/brainstorm_synthesis.py "dependency management" \
    --arch-root . \
    --answers-json '{"Q1":"manifest-based","Q2":"pure function"}'

# Print to stdout instead of writing file
python sdk/brainstorm_synthesis.py "dashboard design" \
    --arch-root . --stdout
```

---

## 8. Output Path Convention

```
design/<topic-slug>.md
```

Where `<topic-slug>` is the topic string lowercased with spaces/hyphens normalized to `-`:
- "dependency management" → `design/dependency-management.md`
- "post-pause-briefing" → `design/post-pause-briefing.md`

If `design/` directory doesn't exist, it is created automatically.

---

End of brainstorm-synthesis protocol.
