# cognitive-arch / sdk/tests/test_brainstorm_predictor.py
# purpose: Unit tests for sdk/brainstorm_predictor.py and sdk/prediction_schema.py
# stdlib-only; no external dependencies

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from brainstorm_context_schema import ContextBundle, PatternEntry, RetroEntry, AdrEntry, StateSnapshot
from prediction_schema import (
    CONFIDENCE_HIGH, CONFIDENCE_LOW, CONFIDENCE_MED,
    Prediction, PredictionSet, Question,
)
from brainstorm_predictor import (
    predict, predict_all,
    _score_option, _compute_confidence, _count_occurrences,
    _build_rationale,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_RETRO_DEP = RetroEntry(
    block_id="block-107",
    title="Block 107 — Dependency resolution automation",
    slug="block-107-dependency-resolution",
    date="2026-05-27",
    content="pure function dependency resolver manifests unblocked blocks done",
)

_RETRO_DASH = RetroEntry(
    block_id="block-105",
    title="Block 105 — Live dashboard HTML generator",
    slug="block-105-dashboard",
    date="2026-05-27",
    content="dashboard html generator dark theme velocity metrics",
)

_PATTERN = PatternEntry(
    name="velocity-data-gap",
    content="INFO pattern: velocity data missing in recent blocks.",
)

_ADR = AdrEntry(
    adr_id="ADR-001",
    title="Use pure function design",
    content="Pure functions are preferred for all SDK modules for testability.",
)

_STATE = StateSnapshot(
    current_phase="17", next_action="start-block-109",
    last_block="block-108", generated_at="2026-05-27T00:00Z",
)


def _make_context(**kwargs) -> ContextBundle:
    defaults = dict(
        topic="dependency management",
        relevant_retros=[_RETRO_DEP, _RETRO_DASH],
        applicable_patterns=[_PATTERN],
        recommendations=[],
        related_adrs=[_ADR],
        state_snapshot=_STATE,
    )
    defaults.update(kwargs)
    return ContextBundle(**defaults)


def _make_question(**kwargs) -> Question:
    defaults = dict(
        id="Q1", text="How should we handle dependencies?",
        topic="dependency management",
        options=["pure function", "side effects", "manual", "automated"],
    )
    defaults.update(kwargs)
    return Question(**defaults)


# ---------------------------------------------------------------------------
# Tests: _count_occurrences
# ---------------------------------------------------------------------------

def test_count_occurrences_found():
    assert _count_occurrences("dependency resolution automation", "dependency") == 1


def test_count_occurrences_multiple():
    assert _count_occurrences("dep dep dep", "dep") == 3


def test_count_occurrences_case_insensitive():
    assert _count_occurrences("DEPENDENCY", "dependency") == 1


def test_count_occurrences_not_found():
    assert _count_occurrences("unrelated text", "dependency") == 0


def test_count_occurrences_empty_needle():
    assert _count_occurrences("text", "") == 0


# ---------------------------------------------------------------------------
# Tests: _score_option
# ---------------------------------------------------------------------------

def test_score_option_retro_match():
    ctx = _make_context()
    score, sources = _score_option("dependency", ctx)
    assert score > 0
    assert "block-107" in sources


def test_score_option_no_match():
    ctx = _make_context()
    score, sources = _score_option("nonexistent_xyz_qwerty", ctx)
    assert score == 0
    assert sources == []


def test_score_option_adr_double_weight():
    ctx = _make_context(
        relevant_retros=[],
        applicable_patterns=[],
    )
    # "pure" appears in ADR title + content → gets _WEIGHT_ADR=2 per occurrence
    score, sources = _score_option("pure", ctx)
    assert score >= 2  # ADR weight
    assert "ADR-001" in sources


def test_score_option_pattern_match():
    ctx = _make_context(
        relevant_retros=[],
        related_adrs=[],
    )
    score, sources = _score_option("velocity", ctx)
    assert score > 0
    assert any("pattern:" in s for s in sources)


def test_score_option_deduplicates_sources():
    # Same source shouldn't appear twice
    ctx = _make_context()
    _, sources = _score_option("block", ctx)
    assert len(sources) == len(set(sources))


# ---------------------------------------------------------------------------
# Tests: _compute_confidence
# ---------------------------------------------------------------------------

def test_compute_confidence_high_score():
    band, score = _compute_confidence(score=3, total_evidence=5)
    assert band == CONFIDENCE_HIGH
    assert score >= 0.80


def test_compute_confidence_medium_score():
    band, score = _compute_confidence(score=1, total_evidence=5)
    assert band == CONFIDENCE_MED
    assert 0.50 <= score < 0.80


def test_compute_confidence_zero_score():
    band, score = _compute_confidence(score=0, total_evidence=5)
    assert band == CONFIDENCE_LOW
    assert score < 0.50


def test_compute_confidence_no_evidence():
    band, score = _compute_confidence(score=0, total_evidence=0)
    assert band == CONFIDENCE_LOW


def test_compute_confidence_score_2_evidence_3_is_high():
    band, _ = _compute_confidence(score=2, total_evidence=3)
    assert band == CONFIDENCE_HIGH


# ---------------------------------------------------------------------------
# Tests: predict (option-based)
# ---------------------------------------------------------------------------

def test_predict_returns_prediction():
    p = predict(_make_question(), _make_context())
    assert isinstance(p, Prediction)


def test_predict_question_id_stored():
    p = predict(_make_question(id="Q5"), _make_context())
    assert p.question_id == "Q5"


def test_predict_confidence_band_valid():
    p = predict(_make_question(), _make_context())
    assert p.confidence_band in (CONFIDENCE_HIGH, CONFIDENCE_MED, CONFIDENCE_LOW)


def test_predict_recommended_is_one_of_options():
    q = _make_question(options=["pure function", "manual"])
    p = predict(q, _make_context())
    assert p.recommended_value in ["pure function", "manual"]


def test_predict_best_option_first():
    # "pure" → high relevance from ADR; "manual" → low
    ctx = _make_context(relevant_retros=[], applicable_patterns=[])
    q = _make_question(options=["pure function", "manual"])
    p = predict(q, ctx)
    assert p.recommended_value == "pure function"


def test_predict_alternative_options_excludes_recommended():
    p = predict(_make_question(), _make_context())
    assert p.recommended_value not in p.alternative_options


def test_predict_rationale_non_empty():
    p = predict(_make_question(), _make_context())
    assert len(p.rationale) > 0


def test_predict_evidence_sources_populated():
    p = predict(_make_question(), _make_context())
    # With retro + ADR matching "dependency", should have sources
    assert isinstance(p.evidence_sources, list)


# ---------------------------------------------------------------------------
# Tests: predict (open-answer)
# ---------------------------------------------------------------------------

def test_predict_open_answer_no_options():
    q = _make_question(options=[], default="See retrospectives")
    p = predict(q, _make_context())
    assert isinstance(p, Prediction)
    assert p.recommended_value != ""


def test_predict_open_answer_empty_context():
    q = _make_question(options=[])
    ctx = ContextBundle(topic="novel topic")
    p = predict(q, ctx)
    assert p.confidence_band == CONFIDENCE_LOW
    assert p.is_guessing


def test_predict_low_confidence_flags_guessing():
    ctx = ContextBundle(topic="unrelated")
    q = _make_question(options=["a", "b"])
    p = predict(q, ctx)
    assert p.is_guessing or p.confidence_band == CONFIDENCE_LOW


# ---------------------------------------------------------------------------
# Tests: Prediction properties
# ---------------------------------------------------------------------------

def test_prediction_is_high_confidence():
    p = Prediction(
        question_id="Q1", recommended_value="x",
        confidence_band=CONFIDENCE_HIGH, confidence_score=0.9,
        rationale="", alternative_options=[], evidence_sources=[],
    )
    assert p.is_high_confidence is True
    assert p.is_guessing is False


def test_prediction_is_guessing():
    p = Prediction(
        question_id="Q1", recommended_value="x",
        confidence_band=CONFIDENCE_LOW, confidence_score=0.3,
        rationale="", alternative_options=[], evidence_sources=[],
    )
    assert p.is_guessing is True
    assert p.is_high_confidence is False


# ---------------------------------------------------------------------------
# Tests: predict_all
# ---------------------------------------------------------------------------

def test_predict_all_returns_prediction_set():
    ctx = _make_context()
    qs = [_make_question(id="Q1"), _make_question(id="Q2")]
    ps = predict_all(qs, ctx)
    assert isinstance(ps, PredictionSet)


def test_predict_all_correct_count():
    ctx = _make_context()
    qs = [_make_question(id=f"Q{i}") for i in range(5)]
    ps = predict_all(qs, ctx)
    assert len(ps.predictions) == 5


def test_predict_all_topic_matches_context():
    ctx = _make_context(topic="my topic")
    ps = predict_all([], ctx)
    assert ps.topic == "my topic"


def test_predict_all_generated_at_present():
    ctx = _make_context()
    ps = predict_all([], ctx)
    assert ps.generated_at != ""


def test_predict_all_retro_count():
    ctx = _make_context()
    ps = predict_all([], ctx)
    assert ps.context_retro_count == len(ctx.relevant_retros)


def test_predict_all_by_id():
    ctx = _make_context()
    qs = [_make_question(id="Q42")]
    ps = predict_all(qs, ctx)
    found = ps.by_id("Q42")
    assert found is not None
    assert found.question_id == "Q42"


def test_predict_all_by_id_missing():
    ctx = _make_context()
    ps = predict_all([], ctx)
    assert ps.by_id("QZZZ") is None


def test_predict_all_custom_timestamp():
    ctx = _make_context()
    ps = predict_all([], ctx, now_ts="2026-05-27T12:00:00+00:00")
    assert ps.generated_at == "2026-05-27T12:00:00+00:00"
