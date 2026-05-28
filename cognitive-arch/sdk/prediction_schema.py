# cognitive-arch / sdk/prediction_schema.py
# purpose: Data model for Brainstorm v2 predictions.
#   Prediction is the output of brainstorm_predictor.predict() (block-109).
#   Consumed by questionnaire template (block-110) and synthesis (block-111).
# stdlib-only; no external dependencies

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Confidence band constants (per D10)
CONFIDENCE_HIGH = "high"    # ≥ 80% — strong evidence from context
CONFIDENCE_MED  = "medium"  # 50–80% — some evidence; moderate certainty
CONFIDENCE_LOW  = "low"     # < 50% — AI is guessing; user should override


@dataclass
class Question:
    """
    A brainstorm questionnaire question.

    If options is empty, the question is open-answer (free-text only).
    allow_free_text is always True per Q15 principle — user may always override.
    """
    id: str               # e.g. "Q1", "Q15"
    text: str             # human-readable question
    topic: str            # topic category (used by context loader for relevance)
    options: list[str] = field(default_factory=list)  # [] = open-answer question
    default: str = ""     # fallback recommendation when no evidence found
    allow_free_text: bool = True  # always True per Q15; here for explicitness


@dataclass
class Prediction:
    """
    AI prediction for a single Question.

    The AI recommends but never decides — user always has final say.
    Low confidence predictions are explicitly flagged as "AI guessing here."
    """
    question_id: str
    recommended_value: str      # best recommendation from evidence (option or free-text)
    confidence_band: str        # CONFIDENCE_HIGH | CONFIDENCE_MED | CONFIDENCE_LOW
    confidence_score: float     # 0.0–1.0; calibrated to confidence_band thresholds
    rationale: str              # explanation citing specific evidence
    alternative_options: list[str] = field(default_factory=list)  # other viable choices
    evidence_sources: list[str] = field(default_factory=list)     # block IDs / pattern names

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence_band == CONFIDENCE_HIGH

    @property
    def is_guessing(self) -> bool:
        return self.confidence_band == CONFIDENCE_LOW


@dataclass
class PredictionSet:
    """
    A complete set of predictions for a brainstorm session.
    Produced by brainstorm_predictor.predict_all().
    """
    topic: str
    generated_at: str
    predictions: list[Prediction] = field(default_factory=list)
    context_retro_count: int = 0
    context_pattern_count: int = 0

    def by_id(self, question_id: str) -> Optional[Prediction]:
        """Look up a prediction by question ID."""
        for p in self.predictions:
            if p.question_id == question_id:
                return p
        return None
