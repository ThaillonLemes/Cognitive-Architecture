# sdk/tests/test_pattern_analyzer_window.py
# PURPOSE: Tests for the optional window_size parameter on pattern_analyzer.analyze().
# DEPS:    pytest, sdk/pattern_analyzer, sdk/retro_signal_schema
# SEE:     blocks/block-139-close-loop.md (close-the-loop block)

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from retro_signal_schema import RetroSignal
from pattern_analyzer import _window, analyze, THRESHOLD, WINDOW_SIZE


def _sig(block_id: str, *, forced_pass: bool = False) -> RetroSignal:
    """Minimal RetroSignal — only the fields the windowing rules care about."""
    return RetroSignal(
        block_id=block_id,
        tier="M",
        kind="implementation",
        phase="phase-1",
        duration_actual_h=2.0,
        duration_estimated_days=1.0,
        duration_source="manual",
        axioms_violated=[],
        scope_expansion=False,
        gate_failures=0,
        gates_total=4,
        gates_passed_count=4,
        forced_pass=forced_pass,
    )


# ---------------------------------------------------------------------------
# _window — direct unit tests
# ---------------------------------------------------------------------------

class TestWindowHelper:
    def test_default_size_keeps_last_n(self):
        signals = [_sig(f"block-{i:03}") for i in range(100)]
        result = _window(signals)  # default = WINDOW_SIZE (30)
        assert len(result) == WINDOW_SIZE
        # Must be the *last* 30 signals
        assert result[0].block_id == f"block-{100 - WINDOW_SIZE:03}"
        assert result[-1].block_id == "block-099"

    def test_explicit_size_overrides_default(self):
        signals = [_sig(f"block-{i:03}") for i in range(20)]
        result = _window(signals, 5)
        assert len(result) == 5
        assert result[0].block_id == "block-015"
        assert result[-1].block_id == "block-019"

    def test_size_none_disables_windowing(self):
        signals = [_sig(f"block-{i:03}") for i in range(120)]
        result = _window(signals, None)
        assert result is signals  # same object — no copy
        assert len(result) == 120

    def test_size_larger_than_input_returns_all(self):
        signals = [_sig(f"block-{i:03}") for i in range(5)]
        result = _window(signals, 100)
        assert len(result) == 5


# ---------------------------------------------------------------------------
# analyze() — window_size parameter integration
# ---------------------------------------------------------------------------

class TestAnalyzeWindowSize:
    def test_default_windows_to_30(self):
        """Forced-pass in the oldest 90 blocks must NOT fire under default window."""
        old_forced = [_sig(f"block-{i:03}", forced_pass=True) for i in range(90)]
        recent_clean = [_sig(f"block-{i:03}") for i in range(90, 130)]
        signals = old_forced + recent_clean

        patterns = analyze(signals)  # default window=30 → forced_pass count = 0

        assert not any(p.rule_id == "R5" for p in patterns), (
            "R5 (forced-pass-clustering) must not fire when forced passes lie "
            "outside the default 30-block window"
        )

    def test_window_none_includes_full_history(self):
        """The same forced-pass signals MUST fire with window_size=None."""
        old_forced = [_sig(f"block-{i:03}", forced_pass=True) for i in range(90)]
        recent_clean = [_sig(f"block-{i:03}") for i in range(90, 130)]
        signals = old_forced + recent_clean

        patterns = analyze(signals, window_size=None)

        r5 = [p for p in patterns if p.rule_id == "R5"]
        assert r5, "R5 must fire when full history is mined"
        assert r5[0].occurrences == 90

    def test_explicit_small_window_caps_evidence(self):
        """window_size=5 must clip occurrences regardless of input size."""
        signals = [_sig(f"block-{i:03}", forced_pass=True) for i in range(50)]
        patterns = analyze(signals, window_size=5)
        r5 = [p for p in patterns if p.rule_id == "R5"]
        assert r5 and r5[0].occurrences == 5

    def test_empty_signals_window_none_no_crash(self):
        assert analyze([], window_size=None) == []

    def test_window_below_threshold_returns_empty(self):
        """window_size=1 with one forced_pass → below THRESHOLD → no pattern."""
        signals = [_sig(f"block-{i:03}", forced_pass=True) for i in range(THRESHOLD)]
        patterns = analyze(signals, window_size=1)
        assert not any(p.rule_id == "R5" for p in patterns)
