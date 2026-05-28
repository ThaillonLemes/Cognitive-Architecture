# PURPOSE: Tests for token signal extraction and budget_overrun pattern detection — block-116
# INPUTS:  tmp_path, synthetic retro files, mock TokenSignal objects
# OUTPUTS: assertions on extract_token_signals and detect_budget_overrun
# DEPS:    pytest, retro_signals, pattern_analyzer modules
# SEE:     sdk/retro_signals.py, sdk/pattern_analyzer.py, phases/phase-18.md block-116

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from retro_signals import extract_token_signals, TokenSignal
from pattern_analyzer import detect_budget_overrun


def _write_retro(tmp_path: Path, name: str, content: str) -> Path:
    blocks = tmp_path / "blocks"
    blocks.mkdir(exist_ok=True)
    p = blocks / name
    p.write_text(content, encoding="utf-8")
    return p


def _tok_signal(block_id, delta_pct):
    return SimpleNamespace(block_id=block_id, delta_pct=delta_pct)


# ---------------------------------------------------------------------------
# extract_token_signals tests
# ---------------------------------------------------------------------------

class TestExtractTokenSignals:
    def test_extracts_signal_with_both_fields(self, tmp_path):
        _write_retro(tmp_path, "block-100-test.md",
            "---\nid: block-100\nphase: phase-10\ntok_estimated: 2000\ntok_actual: 2400\ncreated_at: 2026-05-10\n---\n")
        signals = extract_token_signals(tmp_path)
        assert len(signals) == 1
        assert signals[0].block_id == "block-100"
        assert signals[0].tok_estimated == 2000
        assert signals[0].tok_actual == 2400
        assert signals[0].delta_pct == pytest.approx(20.0)

    def test_skips_block_without_tok_actual(self, tmp_path):
        _write_retro(tmp_path, "block-101-test.md",
            "---\nid: block-101\ntok_estimated: 1000\ncreated_at: 2026-05-10\n---\n")
        signals = extract_token_signals(tmp_path)
        assert len(signals) == 0

    def test_delta_pct_none_when_no_estimated(self, tmp_path):
        _write_retro(tmp_path, "block-102-test.md",
            "---\nid: block-102\ntok_actual: 800\ncreated_at: 2026-05-11\n---\n")
        signals = extract_token_signals(tmp_path)
        assert len(signals) == 1
        assert signals[0].delta_pct is None

    def test_excludes_block_log(self, tmp_path):
        (tmp_path / "blocks").mkdir(exist_ok=True)
        (tmp_path / "blocks" / "BLOCK_LOG.md").write_text("block-100 done - 2026-05-10\n")
        signals = extract_token_signals(tmp_path)
        assert len(signals) == 0

    def test_negative_delta_pct(self, tmp_path):
        _write_retro(tmp_path, "block-103-test.md",
            "---\nid: block-103\ntok_estimated: 3000\ntok_actual: 1500\ncreated_at: 2026-05-12\n---\n")
        signals = extract_token_signals(tmp_path)
        assert len(signals) == 1
        assert signals[0].delta_pct == pytest.approx(-50.0)

    def test_tok_dash_actual_variant(self, tmp_path):
        _write_retro(tmp_path, "block-104-test.md",
            "---\nid: block-104\ntok-actual: 500\ncreated_at: 2026-05-12\n---\n")
        signals = extract_token_signals(tmp_path)
        assert len(signals) == 1
        assert signals[0].tok_actual == 500


# ---------------------------------------------------------------------------
# detect_budget_overrun tests
# ---------------------------------------------------------------------------

class TestDetectBudgetOverrun:
    def test_fires_when_enough_overruns(self):
        signals = [_tok_signal(f"block-{i}", 25.0) for i in range(3)]
        patterns = detect_budget_overrun(signals, threshold_pct=20.0, d1_min=3)
        assert len(patterns) == 1
        assert patterns[0].name == "budget-overrun-recurring"
        assert patterns[0].rule_id == "R8"

    def test_does_not_fire_below_d1_min(self):
        signals = [_tok_signal(f"block-{i}", 25.0) for i in range(2)]
        patterns = detect_budget_overrun(signals, threshold_pct=20.0, d1_min=3)
        assert len(patterns) == 0

    def test_does_not_fire_when_within_threshold(self):
        signals = [_tok_signal(f"block-{i}", 15.0) for i in range(5)]
        patterns = detect_budget_overrun(signals, threshold_pct=20.0, d1_min=3)
        assert len(patterns) == 0

    def test_signals_with_none_delta_excluded(self):
        signals = [_tok_signal(f"block-{i}", None) for i in range(5)]
        patterns = detect_budget_overrun(signals)
        assert len(patterns) == 0

    def test_mixed_signals_only_overruns_counted(self):
        signals = [
            _tok_signal("block-001", 30.0),
            _tok_signal("block-002", 10.0),
            _tok_signal("block-003", 35.0),
            _tok_signal("block-004", 5.0),
            _tok_signal("block-005", 25.0),
        ]
        patterns = detect_budget_overrun(signals, threshold_pct=20.0, d1_min=3)
        assert len(patterns) == 1
        assert len(patterns[0].evidence) == 3
        assert "block-001" in patterns[0].evidence
        assert "block-003" in patterns[0].evidence
        assert "block-005" in patterns[0].evidence

    def test_custom_threshold(self):
        signals = [_tok_signal(f"block-{i}", 10.0) for i in range(5)]
        patterns = detect_budget_overrun(signals, threshold_pct=5.0, d1_min=3)
        assert len(patterns) == 1

    def test_empty_signals(self):
        assert detect_budget_overrun([]) == []
