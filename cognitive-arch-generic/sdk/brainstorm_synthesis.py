# cognitive-arch / sdk/brainstorm_synthesis.py
# purpose: Synthesis automation for Brainstorm v2.
#   Input: questions + predictions + user responses → design/<topic>.md
#   Handles: accepted predictions, modified predictions, free-text overrides.
#   Output: structured markdown design doc with decisions table + per-question rationale.
# stdlib-only; no external dependencies

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from prediction_schema import CONFIDENCE_HIGH, CONFIDENCE_LOW, CONFIDENCE_MED, Prediction, PredictionSet, Question

DESIGN_DIR = "design"

# Answer classification types
ANSWER_ACCEPTED  = "accepted"    # user accepted AI recommendation verbatim
ANSWER_MODIFIED  = "modified"    # user chose a different listed option
ANSWER_FREE_TEXT = "free_text"   # user wrote their own answer
ANSWER_NONE      = "no_answer"   # no response provided


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class QuestionResponse:
    """Pair of a question, its prediction, and the user's response."""
    question: Question
    prediction: Prediction
    answer: str              # user's actual answer text
    answer_type: str         # ANSWER_* constant


@dataclass
class SynthesisOutput:
    """Result of a synthesis run."""
    topic: str
    generated_at: str
    content: str             # full markdown content
    design_path: str         # relative path (e.g. "design/my-topic.md")
    questions_total: int
    questions_answered: int
    questions_accepted: int  # user accepted AI prediction
    accuracy_rate: float     # accepted / answered (0.0 if no answers)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _arch_path(arch_root: Optional[str]) -> Path:
    return Path(arch_root) if arch_root is not None else Path.cwd()


def _topic_to_filename(topic: str) -> str:
    """Convert topic string to a safe filename slug."""
    slug = re.sub(r"[^\w\s-]", "", topic.lower())
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")
    return slug or "brainstorm"


def _classify_response(
    answer: str,
    question: Question,
    prediction: Prediction,
) -> str:
    """
    Classify a user response as accepted, modified, free_text, or no_answer.

    Rules:
    - no_answer  : answer is empty or whitespace only
    - accepted   : answer matches the AI recommendation (case-insensitive)
    - modified   : answer matches one of the other listed options
    - free_text  : answer doesn't match any listed option
    """
    if not answer or not answer.strip():
        return ANSWER_NONE

    ans = answer.strip().lower()
    pred = prediction.recommended_value.strip().lower()

    if ans == pred:
        return ANSWER_ACCEPTED

    for opt in question.options:
        if ans == opt.strip().lower():
            return ANSWER_MODIFIED

    return ANSWER_FREE_TEXT


def _confidence_label(band: str) -> str:
    labels = {
        CONFIDENCE_HIGH: "🟢 High",
        CONFIDENCE_MED:  "🟡 Medium",
        CONFIDENCE_LOW:  "🔴 Low (AI was guessing)",
    }
    return labels.get(band, band)


def _accuracy_rate(responses: list[QuestionResponse]) -> float:
    answered = [r for r in responses if r.answer_type != ANSWER_NONE]
    if not answered:
        return 0.0
    accepted = [r for r in answered if r.answer_type == ANSWER_ACCEPTED]
    return len(accepted) / len(answered)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_responses(
    questions: list[Question],
    prediction_set: PredictionSet,
    answers: dict[str, str],
) -> list[QuestionResponse]:
    """
    Pair each question with its prediction and the user's answer.

    Parameters
    ----------
    questions : list[Question]
        Questions from the questionnaire.
    prediction_set : PredictionSet
        Predictions from brainstorm_predictor.predict_all().
    answers : dict[str, str]
        Mapping question_id → user answer text.
        Missing question IDs → treated as ANSWER_NONE.

    Returns
    -------
    list[QuestionResponse]
        One entry per question in order.
    """
    result = []
    for q in questions:
        pred = prediction_set.by_id(q.id)
        if pred is None:
            # No prediction exists — create minimal placeholder
            from prediction_schema import CONFIDENCE_LOW
            pred = Prediction(
                question_id=q.id,
                recommended_value=q.default or "(no prediction)",
                confidence_band=CONFIDENCE_LOW,
                confidence_score=0.0,
                rationale="No prediction was generated for this question.",
            )
        answer = answers.get(q.id, "")
        answer_type = _classify_response(answer, q, pred)
        result.append(QuestionResponse(
            question=q, prediction=pred, answer=answer, answer_type=answer_type
        ))
    return result


def render_design_doc(
    topic: str,
    responses: list[QuestionResponse],
    generated_at: str,
) -> str:
    """
    Render a structured design document in markdown from the synthesis input.

    Sections: header, summary table, decisions table, decision details.
    """
    answered = [r for r in responses if r.answer_type != ANSWER_NONE]
    accepted = [r for r in answered if r.answer_type == ANSWER_ACCEPTED]
    acc_rate = _accuracy_rate(responses)

    # --- Summary table ---
    summary_rows = "\n".join([
        f"| Questions total | {len(responses)} |",
        f"| Answered | {len(answered)} |",
        f"| AI predictions accepted | {len(accepted)} ({acc_rate * 100:.0f}%) |",
        f"| Modified answers | {len([r for r in answered if r.answer_type == ANSWER_MODIFIED])} |",
        f"| Free-text answers | {len([r for r in answered if r.answer_type == ANSWER_FREE_TEXT])} |",
    ])

    # --- Decisions table ---
    def _table_row(r: QuestionResponse) -> str:
        display_answer = r.answer if r.answer else "*no answer*"
        src_emoji = {"accepted": "✅", "modified": "🔄", "free_text": "✍️", "no_answer": "⬜"}
        src = src_emoji.get(r.answer_type, "?")
        conf = _confidence_label(r.prediction.confidence_band).split()[0]  # just emoji
        return (
            f"| {r.question.id} | {r.question.text[:60]}{'…' if len(r.question.text) > 60 else ''} "
            f"| {display_answer[:40]} | {src} | {conf} |"
        )

    decisions_rows = "\n".join(_table_row(r) for r in responses)

    # --- Per-question details ---
    detail_sections = []
    for r in responses:
        display_answer = r.answer if r.answer else "*no answer provided*"
        answer_label = {
            ANSWER_ACCEPTED:  "Accepted AI recommendation",
            ANSWER_MODIFIED:  "Modified (chose alternate option)",
            ANSWER_FREE_TEXT: "Free-text answer",
            ANSWER_NONE:      "No response",
        }.get(r.answer_type, r.answer_type)

        detail_sections.append(
            f"### {r.question.id} — {r.question.text}\n\n"
            f"**Decision:** {display_answer}\n\n"
            f"**Source:** {answer_label}\n\n"
            f"**AI predicted:** {r.prediction.recommended_value} "
            f"({_confidence_label(r.prediction.confidence_band)})\n\n"
            f"**AI rationale:** {r.prediction.rationale}\n"
        )

    details_block = "\n---\n\n".join(detail_sections)

    return f"""# Design: {topic}

*Synthesized from Brainstorm v2 session*
*Generated: {generated_at}*

---

## Summary

| Metric | Value |
|--------|-------|
{summary_rows}

---

## Decisions Table

| ID | Question | Decision | Source | Confidence |
|----|----------|----------|--------|------------|
{decisions_rows}

---

## Decision Details

{details_block}

---

*Generated by `sdk/brainstorm_synthesis.py`.*
*Protocol: `protocols/brainstorm-synthesis.md`.*
*Review before committing to `design/` — AI synthesizes, human decides.*
"""


def synthesize(
    topic: str,
    questions: list[Question],
    prediction_set: PredictionSet,
    answers: dict[str, str],
    arch_root: Optional[str] = None,
    now_ts: Optional[str] = None,
) -> SynthesisOutput:
    """
    Synthesize a design document from brainstorm responses.

    Parameters
    ----------
    topic : str
        Brainstorm topic (used as design doc title and filename).
    questions : list[Question]
        All questions in the questionnaire.
    prediction_set : PredictionSet
        Predictions from brainstorm_predictor.predict_all().
    answers : dict[str, str]
        User responses: question_id → answer text.
    arch_root : str, optional
        Project root (used to compute design_path only; does not write file).
    now_ts : str, optional
        ISO timestamp for generated_at. Defaults to UTC now.

    Returns
    -------
    SynthesisOutput
        Includes rendered content (does not write to disk; call write_design_doc()).
    """
    generated_at = now_ts if now_ts else datetime.now(timezone.utc).isoformat()

    responses = build_responses(questions, prediction_set, answers)
    content = render_design_doc(topic, responses, generated_at)

    n_answered  = sum(1 for r in responses if r.answer_type != ANSWER_NONE)
    n_accepted  = sum(1 for r in responses if r.answer_type == ANSWER_ACCEPTED)
    acc_rate    = n_accepted / n_answered if n_answered else 0.0

    slug = _topic_to_filename(topic)
    design_path = f"{DESIGN_DIR}/{slug}.md"

    return SynthesisOutput(
        topic=topic,
        generated_at=generated_at,
        content=content,
        design_path=design_path,
        questions_total=len(questions),
        questions_answered=n_answered,
        questions_accepted=n_accepted,
        accuracy_rate=acc_rate,
    )


def write_design_doc(
    output: SynthesisOutput,
    arch_root: Optional[str] = None,
    decisions: Optional[list] = None,
    no_adr: bool = False,
) -> Path:
    """
    Write the synthesized design document to design/<topic>.md.
    Creates the design/ directory if it doesn't exist.
    Returns the output path.

    If `decisions` is provided and `no_adr` is False, calls adr_drafter.generate()
    for decisions with significance:high or significance:medium after writing the doc.
    Import failure of adr_drafter never blocks synthesis (try/except).
    """
    root = _arch_path(arch_root)
    out_path = root / output.design_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output.content, encoding="utf-8")

    # Post-synthesis ADR trigger (Phase 19)
    if decisions and not no_adr:
        try:
            import sys as _sys
            _sdk = str(Path(__file__).parent)
            if _sdk not in _sys.path:
                _sys.path.insert(0, _sdk)
            from adr_drafter import AdrDrafter
            # Attach synthesis_source to each decision that lacks it
            for d in decisions:
                if not d.get("synthesis_source"):
                    d["synthesis_source"] = output.design_path
            created = AdrDrafter(root).generate(decisions)
            if created:
                print(f"  [synthesis] {len(created)} ADR draft(s) created in design/adrs/")
        except Exception:
            pass  # ADR failure must never block synthesis

    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Brainstorm v2 synthesis")
    parser.add_argument("topic", help="Brainstorm topic string")
    parser.add_argument("--arch-root", default=".", help="Root of cognitive-arch project")
    parser.add_argument("--answers-json", default=None,
                        help="JSON string or file path: {question_id: answer_text}")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout instead of writing file")
    parser.add_argument("--no-adr", action="store_true", help="Disable automatic ADR draft generation")
    args = parser.parse_args()

    # Demo mode with empty answers
    answers: dict[str, str] = {}
    if args.answers_json:
        try:
            answers = json.loads(args.answers_json)
        except (json.JSONDecodeError, ValueError):
            try:
                answers = json.loads(Path(args.answers_json).read_text(encoding="utf-8"))
            except Exception:
                pass

    from brainstorm_context import load_context
    from brainstorm_predictor import predict_all

    context = load_context(args.topic, arch_root=args.arch_root)
    prediction_set = predict_all([], context)  # no questions in demo mode

    result = synthesize(args.topic, [], prediction_set, answers, arch_root=args.arch_root)

    if args.stdout:
        print(result.content)
    else:
        path = write_design_doc(result, arch_root=args.arch_root, no_adr=args.no_adr)
        print(f"Design doc written: {path}")
        print(f"Questions: {result.questions_total} | Answered: {result.questions_answered} | Accepted: {result.questions_accepted}")
