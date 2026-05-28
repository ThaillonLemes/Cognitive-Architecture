# cognitive-arch / sdk/tests/test_brainstorm_synthesis.py
# purpose: Unit tests for sdk/brainstorm_synthesis.py
# stdlib-only; no external dependencies

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from brainstorm_context_schema import ContextBundle
from prediction_schema import (
    CONFIDENCE_HIGH, CONFIDENCE_LOW, CONFIDENCE_MED,
    Prediction, PredictionSet, Question,
)
from brainstorm_synthesis import (
    ANSWER_ACCEPTED, ANSWER_FREE_TEXT, ANSWER_MODIFIED, ANSWER_NONE,
    QuestionResponse, SynthesisOutput,
    synthesize, write_design_doc, build_responses, render_design_doc,
    _classify_response, _accuracy_rate, _topic_to_filename,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_NOW_TS = "2026-05-27T00:00:00+00:00"

_Q1 = Question(
    id="Q1", text="How should dependencies be tracked?",
    topic="dependency management",
    options=["manifest-based", "manual", "external-tracker"],
)

_Q2 = Question(
    id="Q2", text="What design pattern should be used?",
    topic="design",
    options=["pure function", "class-based", "procedural"],
)

_Q3 = Question(
    id="Q3", text="Describe the cache policy.", topic="caching",
    options=[],  # open-answer
)

_P1 = Prediction(
    question_id="Q1",
    recommended_value="manifest-based",
    confidence_band=CONFIDENCE_HIGH,
    confidence_score=0.85,
    rationale="block-107 and ADR-001 support manifest-based approach.",
    alternative_options=["manual", "external-tracker"],
    evidence_sources=["block-107", "ADR-001"],
)

_P2 = Prediction(
    question_id="Q2",
    recommended_value="pure function",
    confidence_band=CONFIDENCE_MED,
    confidence_score=0.65,
    rationale="Some evidence for pure function design from recent retros.",
    alternative_options=["class-based"],
    evidence_sources=["block-107"],
)

_P3 = Prediction(
    question_id="Q3",
    recommended_value="LRU with 1-hour TTL",
    confidence_band=CONFIDENCE_LOW,
    confidence_score=0.30,
    rationale="[AI guessing] No direct evidence found.",
    alternative_options=[],
    evidence_sources=[],
)


def _make_pset(*predictions) -> PredictionSet:
    return PredictionSet(
        topic="test topic",
        generated_at=_NOW_TS,
        predictions=list(predictions),
        context_retro_count=2,
        context_pattern_count=1,
    )


# ---------------------------------------------------------------------------
# Tests: _classify_response
# ---------------------------------------------------------------------------

def test_classify_accepted():
    r = _classify_response("manifest-based", _Q1, _P1)
    assert r == ANSWER_ACCEPTED


def test_classify_accepted_case_insensitive():
    r = _classify_response("Manifest-Based", _Q1, _P1)
    assert r == ANSWER_ACCEPTED


def test_classify_modified_different_option():
    r = _classify_response("manual", _Q1, _P1)
    assert r == ANSWER_MODIFIED


def test_classify_free_text():
    r = _classify_response("use a completely custom registry", _Q1, _P1)
    assert r == ANSWER_FREE_TEXT


def test_classify_no_answer_empty():
    r = _classify_response("", _Q1, _P1)
    assert r == ANSWER_NONE


def test_classify_no_answer_whitespace():
    r = _classify_response("   ", _Q1, _P1)
    assert r == ANSWER_NONE


# ---------------------------------------------------------------------------
# Tests: _topic_to_filename
# ---------------------------------------------------------------------------

def test_topic_to_filename_simple():
    assert _topic_to_filename("dependency management") == "dependency-management"


def test_topic_to_filename_special_chars():
    fname = _topic_to_filename("auth & session (v2)")
    assert "/" not in fname
    assert len(fname) > 0


def test_topic_to_filename_hyphenated():
    assert _topic_to_filename("post-pause-briefing") == "post-pause-briefing"


# ---------------------------------------------------------------------------
# Tests: _accuracy_rate
# ---------------------------------------------------------------------------

def test_accuracy_rate_all_accepted():
    responses = [
        QuestionResponse(_Q1, _P1, "manifest-based", ANSWER_ACCEPTED),
        QuestionResponse(_Q2, _P2, "pure function", ANSWER_ACCEPTED),
    ]
    assert _accuracy_rate(responses) == pytest.approx(1.0)


def test_accuracy_rate_none_accepted():
    responses = [
        QuestionResponse(_Q1, _P1, "manual", ANSWER_MODIFIED),
    ]
    assert _accuracy_rate(responses) == pytest.approx(0.0)


def test_accuracy_rate_no_answers():
    responses = [
        QuestionResponse(_Q1, _P1, "", ANSWER_NONE),
    ]
    assert _accuracy_rate(responses) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Tests: build_responses
# ---------------------------------------------------------------------------

def test_build_responses_returns_correct_count():
    pset = _make_pset(_P1, _P2)
    answers = {"Q1": "manifest-based", "Q2": "class-based"}
    responses = build_responses([_Q1, _Q2], pset, answers)
    assert len(responses) == 2


def test_build_responses_accepted():
    pset = _make_pset(_P1)
    responses = build_responses([_Q1], pset, {"Q1": "manifest-based"})
    assert responses[0].answer_type == ANSWER_ACCEPTED


def test_build_responses_missing_answer_is_none():
    pset = _make_pset(_P1)
    responses = build_responses([_Q1], pset, {})
    assert responses[0].answer_type == ANSWER_NONE


def test_build_responses_missing_prediction_uses_placeholder():
    pset = _make_pset()  # empty predictions
    responses = build_responses([_Q1], pset, {"Q1": "manifest-based"})
    assert responses[0].prediction is not None
    assert responses[0].answer_type in (ANSWER_ACCEPTED, ANSWER_FREE_TEXT, ANSWER_MODIFIED)


# ---------------------------------------------------------------------------
# Tests: render_design_doc
# ---------------------------------------------------------------------------

def test_render_design_doc_is_markdown():
    responses = [QuestionResponse(_Q1, _P1, "manifest-based", ANSWER_ACCEPTED)]
    doc = render_design_doc("test topic", responses, _NOW_TS)
    assert "# Design:" in doc


def test_render_design_doc_contains_topic():
    responses = []
    doc = render_design_doc("dependency management", responses, _NOW_TS)
    assert "dependency management" in doc


def test_render_design_doc_has_summary_section():
    responses = []
    doc = render_design_doc("topic", responses, _NOW_TS)
    assert "## Summary" in doc


def test_render_design_doc_has_decisions_section():
    responses = []
    doc = render_design_doc("topic", responses, _NOW_TS)
    assert "## Decisions Table" in doc


def test_render_design_doc_has_details_section():
    responses = [QuestionResponse(_Q1, _P1, "manifest-based", ANSWER_ACCEPTED)]
    doc = render_design_doc("topic", responses, _NOW_TS)
    assert "## Decision Details" in doc


def test_render_design_doc_contains_answer():
    responses = [QuestionResponse(_Q1, _P1, "manifest-based", ANSWER_ACCEPTED)]
    doc = render_design_doc("topic", responses, _NOW_TS)
    assert "manifest-based" in doc


# ---------------------------------------------------------------------------
# Tests: synthesize
# ---------------------------------------------------------------------------

def test_synthesize_returns_output():
    pset = _make_pset(_P1, _P2)
    result = synthesize("test topic", [_Q1, _Q2], pset, {"Q1": "manifest-based", "Q2": "pure function"})
    assert isinstance(result, SynthesisOutput)


def test_synthesize_topic_stored():
    pset = _make_pset()
    result = synthesize("my topic", [], pset, {})
    assert result.topic == "my topic"


def test_synthesize_questions_total():
    pset = _make_pset(_P1, _P2)
    result = synthesize("t", [_Q1, _Q2], pset, {"Q1": "manifest-based"})
    assert result.questions_total == 2


def test_synthesize_questions_answered():
    pset = _make_pset(_P1, _P2)
    result = synthesize("t", [_Q1, _Q2], pset, {"Q1": "manifest-based"})
    assert result.questions_answered == 1


def test_synthesize_accuracy_rate_all_accepted():
    pset = _make_pset(_P1, _P2)
    result = synthesize("t", [_Q1, _Q2], pset, {
        "Q1": "manifest-based",
        "Q2": "pure function",
    })
    assert result.accuracy_rate == pytest.approx(1.0)


def test_synthesize_accuracy_rate_partial():
    pset = _make_pset(_P1, _P2)
    result = synthesize("t", [_Q1, _Q2], pset, {
        "Q1": "manifest-based",  # accepted
        "Q2": "class-based",     # modified
    })
    assert 0.0 < result.accuracy_rate < 1.0


def test_synthesize_content_non_empty():
    pset = _make_pset()
    result = synthesize("my topic", [], pset, {})
    assert len(result.content) > 0


def test_synthesize_custom_timestamp():
    pset = _make_pset()
    result = synthesize("t", [], pset, {}, now_ts="2026-05-27T12:00:00+00:00")
    assert result.generated_at == "2026-05-27T12:00:00+00:00"


def test_synthesize_design_path_contains_topic():
    pset = _make_pset()
    result = synthesize("dependency management", [], pset, {})
    assert "dependency" in result.design_path
    assert result.design_path.startswith("design/")


def test_synthesize_empty_questions():
    pset = _make_pset()
    result = synthesize("topic", [], pset, {})
    assert result.questions_total == 0
    assert result.questions_answered == 0


def test_synthesize_all_accepted():
    pset = _make_pset(_P1)
    result = synthesize("t", [_Q1], pset, {"Q1": "manifest-based"})
    assert result.questions_accepted == 1
    assert result.accuracy_rate == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Tests: write_design_doc
# ---------------------------------------------------------------------------

def test_write_design_doc_creates_file(tmp_path):
    pset = _make_pset()
    output = synthesize("my topic", [], pset, {}, arch_root=str(tmp_path))
    path = write_design_doc(output, arch_root=str(tmp_path))
    assert path.exists()


def test_write_design_doc_correct_path(tmp_path):
    pset = _make_pset()
    output = synthesize("my topic", [], pset, {}, arch_root=str(tmp_path))
    path = write_design_doc(output, arch_root=str(tmp_path))
    assert "design" in str(path)
    assert path.suffix == ".md"


def test_write_design_doc_returns_path(tmp_path):
    pset = _make_pset()
    output = synthesize("t", [], pset, {}, arch_root=str(tmp_path))
    path = write_design_doc(output, arch_root=str(tmp_path))
    assert isinstance(path, Path)
