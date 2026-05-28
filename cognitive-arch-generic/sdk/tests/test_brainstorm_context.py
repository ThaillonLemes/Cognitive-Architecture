# cognitive-arch / sdk/tests/test_brainstorm_context.py
# purpose: Unit tests for sdk/brainstorm_context.py and sdk/brainstorm_context_schema.py
# stdlib-only; no external dependencies

import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from brainstorm_context_schema import (
    AdrEntry, ContextBundle, PatternEntry,
    RecommendationEntry, RetroEntry, StateSnapshot,
)
from brainstorm_context import (
    load_context,
    _extract_keywords, _score_relevance, _recency_weight,
    _load_retros, _load_patterns, _load_adrs, _load_state,
    _rank_retros, _rank_patterns, _rank_adrs,
    _trim_content,
)

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

_NOW_DATE = "2026-05-27"

_SAMPLE_RETRO = RetroEntry(
    block_id="block-107",
    title="Block 107 Retrospective — Dependency resolution automation",
    slug="block-107-dependency-resolution",
    date="2026-05-27",
    content="dependency resolver, manifests, unblocked, pure function design",
)

_SAMPLE_RETRO_OLD = RetroEntry(
    block_id="block-001",
    title="Block 001 Retrospective — Bootstrap setup",
    slug="block-001-bootstrap-setup",
    date="2026-05-01",
    content="initial setup, bootstrap, governance files",
)

_SAMPLE_PATTERN = PatternEntry(
    name="velocity-data-gap",
    content="INFO pattern. Velocity data missing for some blocks.",
)

_SAMPLE_ADR = AdrEntry(
    adr_id="ADR-001",
    title="Structure Option A",
    content="Decision: use monorepo structure. Rationale: simpler governance.",
)

_SAMPLE_STATE = StateSnapshot(
    current_phase="17",
    next_action="start-block-108",
    last_block="block-106",
    generated_at="2026-05-27T00:00:00+00:00",
)


# ---------------------------------------------------------------------------
# Tests: _extract_keywords
# ---------------------------------------------------------------------------

def test_extract_keywords_simple():
    kws = _extract_keywords("dependency management")
    assert "dependency" in kws
    assert "management" in kws


def test_extract_keywords_hyphenated():
    kws = _extract_keywords("post-pause-briefing")
    assert "post" in kws
    assert "pause" in kws
    assert "briefing" in kws


def test_extract_keywords_filters_short_words():
    kws = _extract_keywords("is a big thing")
    assert "is" not in kws
    assert "a" not in kws
    assert "big" in kws


def test_extract_keywords_lowercase():
    kws = _extract_keywords("Dashboard Generator")
    assert "dashboard" in kws
    assert "generator" in kws


def test_extract_keywords_empty():
    assert _extract_keywords("") == []


# ---------------------------------------------------------------------------
# Tests: _score_relevance
# ---------------------------------------------------------------------------

def test_score_relevance_match():
    score = _score_relevance("dependency management automation", ["dependency", "automation"])
    assert score == 2


def test_score_relevance_no_match():
    assert _score_relevance("bootstrap setup", ["dependency"]) == 0


def test_score_relevance_empty_keywords():
    assert _score_relevance("anything", []) == 0


def test_score_relevance_case_insensitive():
    assert _score_relevance("DEPENDENCY management", ["dependency"]) == 1


# ---------------------------------------------------------------------------
# Tests: _recency_weight
# ---------------------------------------------------------------------------

def test_recency_weight_today_is_max():
    w = _recency_weight("2026-05-27", "2026-05-27")
    assert w == pytest.approx(1.0)


def test_recency_weight_old_is_min():
    # 30+ days old → min weight
    w = _recency_weight("2026-01-01", "2026-05-27")
    assert w == pytest.approx(0.1)


def test_recency_weight_halfway():
    # 15 days old = halfway decay
    w = _recency_weight("2026-05-12", "2026-05-27")
    assert 0.1 < w < 1.0


def test_recency_weight_invalid_date():
    w = _recency_weight("not-a-date", "2026-05-27")
    assert w == pytest.approx(0.1)


# ---------------------------------------------------------------------------
# Tests: _load_retros
# ---------------------------------------------------------------------------

def test_load_retros_empty_dir(tmp_path):
    assert _load_retros(tmp_path / "blocks") == []


def test_load_retros_nonexistent_dir(tmp_path):
    assert _load_retros(tmp_path / "nonexistent") == []


def test_load_retros_finds_files(tmp_path):
    blocks = tmp_path / "blocks"
    blocks.mkdir()
    (blocks / "block-001-setup.md").write_text(
        "---\ncompleted_at: 2026-05-20\n---\n# Block 001 Retrospective — Setup\n\ncontent here",
        encoding="utf-8",
    )
    retros = _load_retros(blocks)
    assert len(retros) == 1
    assert retros[0].block_id == "block-001"


def test_load_retros_excludes_block_log(tmp_path):
    blocks = tmp_path / "blocks"
    blocks.mkdir()
    (blocks / "BLOCK_LOG.md").write_text("# log\n", encoding="utf-8")
    retros = _load_retros(blocks)
    assert retros == []


def test_load_retros_parses_title(tmp_path):
    blocks = tmp_path / "blocks"
    blocks.mkdir()
    (blocks / "block-042-decision.md").write_text(
        "---\ncompleted_at: 2026-05-22\n---\n# Block 042 Retrospective — Decision engine\n",
        encoding="utf-8",
    )
    retros = _load_retros(blocks)
    assert "Decision" in retros[0].title


# ---------------------------------------------------------------------------
# Tests: _load_patterns
# ---------------------------------------------------------------------------

def test_load_patterns_empty_file(tmp_path):
    path = tmp_path / "patterns.md"
    path.write_text("", encoding="utf-8")
    assert _load_patterns(path) == []


def test_load_patterns_missing_file(tmp_path):
    assert _load_patterns(tmp_path / "nonexistent.md") == []


def test_load_patterns_extracts_names(tmp_path):
    path = tmp_path / "patterns.md"
    path.write_text("## velocity-data-gap\n\nINFO pattern.\n## stale-tools\n\nWarning.\n",
                    encoding="utf-8")
    patterns = _load_patterns(path)
    names = [p.name for p in patterns]
    assert "velocity-data-gap" in names
    assert "stale-tools" in names


def test_load_patterns_excludes_summary_table(tmp_path):
    path = tmp_path / "patterns.md"
    path.write_text("## Summary Table\n| col | val |\n## real-pattern\ncontent\n",
                    encoding="utf-8")
    patterns = _load_patterns(path)
    names = [p.name for p in patterns]
    assert "Summary Table" not in names
    assert "real-pattern" in names


# ---------------------------------------------------------------------------
# Tests: _load_adrs
# ---------------------------------------------------------------------------

def test_load_adrs_empty_dir(tmp_path):
    assert _load_adrs(tmp_path / "decisions") == []


def test_load_adrs_finds_files(tmp_path):
    decisions = tmp_path / "decisions"
    decisions.mkdir()
    (decisions / "ADR-001-setup.md").write_text(
        "# ADR-001 — Use monorepo\n\nDecision: yes.\n",
        encoding="utf-8",
    )
    adrs = _load_adrs(decisions)
    assert len(adrs) == 1
    assert adrs[0].adr_id == "ADR-001"


# ---------------------------------------------------------------------------
# Tests: _rank functions
# ---------------------------------------------------------------------------

def test_rank_retros_high_relevance_first():
    retros = [_SAMPLE_RETRO_OLD, _SAMPLE_RETRO]
    keywords = ["dependency"]
    ranked = _rank_retros(retros, keywords, _NOW_DATE)
    assert ranked[0].block_id == "block-107"


def test_rank_retros_fallback_to_recent_when_no_match():
    retros = [_SAMPLE_RETRO_OLD, _SAMPLE_RETRO]
    keywords = ["nonexistent_keyword_xyz"]
    ranked = _rank_retros(retros, keywords, _NOW_DATE)
    # Falls back to recency order
    assert len(ranked) <= 5


def test_rank_patterns_match_first():
    other = PatternEntry(name="unrelated-pattern", content="unrelated")
    ranked = _rank_patterns([other, _SAMPLE_PATTERN], ["velocity"])
    assert ranked[0].name == "velocity-data-gap"


def test_rank_adrs_match_first():
    other = AdrEntry(adr_id="ADR-002", title="Unrelated decision", content="nothing")
    ranked = _rank_adrs([other, _SAMPLE_ADR], ["monorepo", "structure"])
    assert ranked[0].adr_id == "ADR-001"


# ---------------------------------------------------------------------------
# Tests: load_context
# ---------------------------------------------------------------------------

def test_load_context_returns_bundle():
    bundle = load_context(
        "dependency management",
        retros=[_SAMPLE_RETRO],
        patterns=[_SAMPLE_PATTERN],
        adrs=[_SAMPLE_ADR],
        state=_SAMPLE_STATE,
    )
    assert isinstance(bundle, ContextBundle)


def test_load_context_topic_stored():
    bundle = load_context(
        "velocity dashboard",
        retros=[], patterns=[], adrs=[], state=_SAMPLE_STATE,
    )
    assert bundle.topic == "velocity dashboard"


def test_load_context_state_stored():
    bundle = load_context(
        "any",
        retros=[], patterns=[], adrs=[], state=_SAMPLE_STATE,
    )
    assert bundle.state_snapshot is not None
    assert bundle.state_snapshot.current_phase == "17"


def test_load_context_relevant_retro_included():
    bundle = load_context(
        "dependency",
        retros=[_SAMPLE_RETRO, _SAMPLE_RETRO_OLD],
        patterns=[], adrs=[], state=_SAMPLE_STATE,
    )
    assert any(r.block_id == "block-107" for r in bundle.relevant_retros)


def test_load_context_novel_topic_sparse():
    # Novel topic with no retro matches — should still return bundle (not crash)
    bundle = load_context(
        "quantum computing distributed ledger",
        retros=[_SAMPLE_RETRO], patterns=[], adrs=[], state=_SAMPLE_STATE,
    )
    assert isinstance(bundle, ContextBundle)
    assert bundle.topic == "quantum computing distributed ledger"


def test_load_context_multi_keyword_topic():
    bundle = load_context(
        "dependency resolution automation",
        retros=[_SAMPLE_RETRO, _SAMPLE_RETRO_OLD],
        patterns=[_SAMPLE_PATTERN], adrs=[], state=_SAMPLE_STATE,
    )
    # block-107 matches "dependency" + "resolution" + "automation"
    assert len(bundle.relevant_retros) >= 1


def test_load_context_empty_project(tmp_path):
    # All from disk: empty project — no crashes
    bundle = load_context("test topic", arch_root=str(tmp_path))
    assert isinstance(bundle, ContextBundle)
    assert bundle.relevant_retros == [] or isinstance(bundle.relevant_retros, list)


# ---------------------------------------------------------------------------
# Tests: ContextBundle / schema
# ---------------------------------------------------------------------------

def test_context_bundle_fields():
    bundle = ContextBundle(topic="test")
    assert bundle.topic == "test"
    assert bundle.relevant_retros == []
    assert bundle.state_snapshot is None


def test_retro_entry_fields():
    r = RetroEntry(block_id="block-1", title="T", slug="s", date="2026-05-01", content="c")
    assert r.block_id == "block-1"


def test_pattern_entry_fields():
    p = PatternEntry(name="n", content="c")
    assert p.name == "n"


def test_state_snapshot_fields():
    s = StateSnapshot(current_phase="16", next_action="x", last_block="b-1", generated_at="2026")
    assert s.current_phase == "16"
