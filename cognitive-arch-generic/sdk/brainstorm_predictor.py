# cognitive-arch / sdk/brainstorm_predictor.py
# purpose: Rule-based prediction engine for Brainstorm v2.
#   Input: Question + ContextBundle → Prediction.
#   Strategy: score each option by evidence in context (retros × ADRs × patterns),
#   rank by score × recency, choose best, assign confidence band per D10.
#   Pure function design — no side effects, no LLM calls, stdlib-only.
# stdlib-only; no external dependencies

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from brainstorm_context_schema import ContextBundle
from prediction_schema import (
    CONFIDENCE_HIGH, CONFIDENCE_LOW, CONFIDENCE_MED,
    Prediction, PredictionSet, Question,
)

# Confidence score anchors (D10: high ≥80%, med 50-80%, low <50%)
_SCORE_HIGH = 0.85
_SCORE_MED  = 0.65
_SCORE_LOW  = 0.30

# Evidence weights: ADRs are authoritative → 2×; retros → 1×; patterns → 1×
_WEIGHT_ADR     = 2
_WEIGHT_RETRO   = 1
_WEIGHT_PATTERN = 1


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _count_occurrences(text: str, needle: str) -> int:
    """Count non-overlapping case-insensitive occurrences of needle in text."""
    if not needle or not text:
        return 0
    return text.lower().count(needle.lower())


def _score_option(
    option: str,
    context: ContextBundle,
) -> tuple[int, list[str]]:
    """
    Score an option against the context bundle.

    Returns
    -------
    (score, sources)
        score   — weighted hit count (ADR=2, retro=1, pattern=1)
        sources — list of evidence source identifiers
    """
    score = 0
    sources: list[str] = []
    option_lower = option.lower()

    # Retros
    for retro in context.relevant_retros:
        hits = _count_occurrences(retro.title + " " + retro.content, option_lower)
        if hits:
            score += hits * _WEIGHT_RETRO
            sources.append(retro.block_id)

    # Patterns
    for pattern in context.applicable_patterns:
        hits = _count_occurrences(pattern.name + " " + pattern.content, option_lower)
        if hits:
            score += hits * _WEIGHT_PATTERN
            sources.append(f"pattern:{pattern.name}")

    # ADRs (authoritative — 2× weight per hit)
    for adr in context.related_adrs:
        hits = _count_occurrences(adr.title + " " + adr.content, option_lower)
        if hits:
            score += hits * _WEIGHT_ADR
            sources.append(adr.adr_id)

    # Deduplicate sources
    seen: set[str] = set()
    unique_sources = []
    for s in sources:
        if s not in seen:
            seen.add(s)
            unique_sources.append(s)

    return score, unique_sources


def _total_evidence_size(context: ContextBundle) -> int:
    """Total number of evidence items in the context bundle."""
    return (
        len(context.relevant_retros)
        + len(context.applicable_patterns)
        + len(context.related_adrs)
    )


def _compute_confidence(score: int, total_evidence: int) -> tuple[str, float]:
    """
    Map evidence score to confidence band and scalar.

    Rules (D10):
      high   — score >= 3  OR (score >= 2 AND evidence >= 3)
      medium — score == 1 or 2
      low    — score == 0  (AI guessing)
    """
    if total_evidence == 0 or score == 0:
        return CONFIDENCE_LOW, _SCORE_LOW
    if score >= 3 or (score >= 2 and total_evidence >= 3):
        return CONFIDENCE_HIGH, _SCORE_HIGH
    if score >= 1:
        return CONFIDENCE_MED, _SCORE_MED
    return CONFIDENCE_LOW, _SCORE_LOW


def _build_rationale(
    question: Question,
    recommended: str,
    sources: list[str],
    confidence: str,
) -> str:
    """Build a human-readable rationale string."""
    if confidence == CONFIDENCE_LOW:
        if question.options:
            return (
                f"[AI guessing — no direct evidence found] "
                f"Defaulting to '{recommended}' as starting point. "
                f"Override with your own judgment."
            )
        else:
            return "[AI guessing — no direct evidence found] Please provide your own answer."

    source_str = ", ".join(sources[:4]) if sources else "context"
    if confidence == CONFIDENCE_HIGH:
        prefix = "Strong evidence in context"
    else:
        prefix = "Some evidence in context"

    return f"{prefix} ({source_str}) supports '{recommended}'."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict(question: Question, context: ContextBundle) -> Prediction:
    """
    Generate a Prediction for a single question given a ContextBundle.

    Parameters
    ----------
    question : Question
        The brainstorm question to predict.
    context : ContextBundle
        Pre-loaded context from brainstorm_context.load_context().

    Returns
    -------
    Prediction
        Always returns a Prediction (never raises). Low-confidence
        predictions are flagged explicitly in confidence_band and rationale.
    """
    total_evidence = _total_evidence_size(context)

    if not question.options:
        # Open-answer: synthesise from best retro title or use default
        best_retro = context.relevant_retros[0] if context.relevant_retros else None
        if best_retro:
            recommended = best_retro.title.split("—")[-1].strip() if "—" in best_retro.title else best_retro.block_id
            confidence, conf_score = _compute_confidence(1, total_evidence)
            sources = [best_retro.block_id]
        else:
            recommended = question.default or "See context for details"
            confidence, conf_score = CONFIDENCE_LOW, _SCORE_LOW
            sources = []

        rationale = _build_rationale(question, recommended, sources, confidence)
        return Prediction(
            question_id=question.id,
            recommended_value=recommended,
            confidence_band=confidence,
            confidence_score=conf_score,
            rationale=rationale,
            alternative_options=[],
            evidence_sources=sources,
        )

    # Option-based question: score each option
    scored = []
    all_sources: dict[str, list[str]] = {}
    for opt in question.options:
        sc, srcs = _score_option(opt, context)
        scored.append((opt, sc))
        all_sources[opt] = srcs

    # Sort by score descending; tie-break by original order
    scored.sort(key=lambda t: t[1], reverse=True)
    best_opt, best_score = scored[0]
    best_sources = all_sources[best_opt]

    confidence, conf_score = _compute_confidence(best_score, total_evidence)
    rationale = _build_rationale(question, best_opt, best_sources, confidence)

    # Alternatives: all other options with any evidence, or just the rest
    alternatives = [opt for opt, sc in scored[1:] if sc > 0]
    if not alternatives:
        alternatives = [opt for opt, _ in scored[1:]]

    return Prediction(
        question_id=question.id,
        recommended_value=best_opt,
        confidence_band=confidence,
        confidence_score=conf_score,
        rationale=rationale,
        alternative_options=alternatives,
        evidence_sources=best_sources,
    )


def predict_all(
    questions: list[Question],
    context: ContextBundle,
    now_ts: Optional[str] = None,
) -> PredictionSet:
    """
    Generate predictions for all questions in a brainstorm session.

    Parameters
    ----------
    questions : list[Question]
        All questions in the questionnaire.
    context : ContextBundle
        Pre-loaded context for the session topic.
    now_ts : str, optional
        ISO timestamp. Defaults to current UTC time.

    Returns
    -------
    PredictionSet
        One Prediction per Question, in order.
    """
    generated_at = now_ts if now_ts else datetime.now(timezone.utc).isoformat()
    predictions = [predict(q, context) for q in questions]

    return PredictionSet(
        topic=context.topic,
        generated_at=generated_at,
        predictions=predictions,
        context_retro_count=len(context.relevant_retros),
        context_pattern_count=len(context.applicable_patterns),
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Brainstorm predictor — demo mode")
    parser.add_argument("topic", help="Brainstorm topic")
    parser.add_argument("--arch-root", default=".", help="Root of cognitive-arch project")
    args = parser.parse_args()

    from brainstorm_context import load_context

    context = load_context(args.topic, arch_root=args.arch_root)

    # Demo: one generic question
    demo_q = Question(
        id="Q1",
        text=f"What is the most pressing concern for '{args.topic}'?",
        topic=args.topic,
        options=["performance", "reliability", "maintainability", "cost"],
    )

    p = predict(demo_q, context)
    print(json.dumps({
        "question": demo_q.text,
        "recommended": p.recommended_value,
        "confidence": p.confidence_band,
        "rationale": p.rationale,
        "sources": p.evidence_sources,
    }, indent=2))
