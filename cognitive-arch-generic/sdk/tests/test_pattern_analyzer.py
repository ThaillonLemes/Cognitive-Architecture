# sdk/tests/test_pattern_analyzer.py
# PURPOSE: Unit tests for pattern_analyzer.py detection rules.
# DEPS:    pytest, sdk/pattern_analyzer, sdk/retro_signal_schema

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from retro_signal_schema import RetroSignal
from pattern_analyzer import (
    analyze, THRESHOLD,
    _rule_axiom_violation, _rule_duration_overrun, _rule_gate_failures,
    _rule_scope_expansion, _rule_forced_pass, _rule_missing_duration,
    _rule_tier_l_overrun,
)


def _sig(block_id="block-001", tier="M", kind="implementation", phase="phase-1",
         actual_h=2.0, est_days=1.0, duration_source="manual",
         axioms_violated=None, scope_expansion=False,
         gate_failures=0, gates_total=4, gates_passed=4,
         forced_pass=False, duration_actual_h=None):
    return RetroSignal(
        block_id=block_id, tier=tier, kind=kind, phase=phase,
        duration_actual_h=duration_actual_h if duration_actual_h is not None else actual_h,
        duration_estimated_days=est_days,
        duration_source=duration_source,
        axioms_violated=axioms_violated or [],
        scope_expansion=scope_expansion,
        gate_failures=gate_failures,
        gates_total=gates_total,
        gates_passed_count=gates_passed,
        forced_pass=forced_pass,
    )


# --- R1: axiom violation ---

def test_r1_fires_at_threshold():
    signals = [_sig(f"block-{i:03}", axioms_violated=["P3"]) for i in range(THRESHOLD)]
    patterns = _rule_axiom_violation(signals)
    assert any(p.rule_id == "R1" and "p3" in p.name for p in patterns)  # name is lowercase


def test_r1_below_threshold_no_pattern():
    signals = [_sig(f"block-{i:03}", axioms_violated=["Q6"]) for i in range(THRESHOLD - 1)]
    patterns = _rule_axiom_violation(signals)
    assert not patterns


def test_r1_multiple_axioms():
    signals = (
        [_sig(f"block-{i:03}", axioms_violated=["P1", "Q4"]) for i in range(THRESHOLD)]
    )
    patterns = _rule_axiom_violation(signals)
    names = [p.name for p in patterns]
    assert any("p1" in n for n in names)
    assert any("q4" in n for n in names)


# --- R2: duration overrun ---

def test_r2_fires_on_overrun():
    # actual=16h, est=1day=8h → ratio=2.0 → over_estimate
    signals = [_sig(f"block-{i:03}", actual_h=16.0, est_days=1.0) for i in range(THRESHOLD)]
    patterns = _rule_duration_overrun(signals)
    assert any(p.rule_id == "R2" for p in patterns)


def test_r2_no_fire_on_normal():
    signals = [_sig(f"block-{i:03}", actual_h=4.0, est_days=1.0) for i in range(THRESHOLD)]
    patterns = _rule_duration_overrun(signals)
    assert not patterns


# --- R3: gate failures ---

def test_r3_fires_on_failures():
    signals = [_sig(f"block-{i:03}", gate_failures=1, gates_total=4, gates_passed=3)
               for i in range(THRESHOLD)]
    patterns = _rule_gate_failures(signals)
    assert any(p.rule_id == "R3" for p in patterns)


def test_r3_no_fire_no_failures():
    signals = [_sig(f"block-{i:03}", gate_failures=0) for i in range(THRESHOLD)]
    patterns = _rule_gate_failures(signals)
    assert not patterns


# --- R4: scope expansion ---

def test_r4_fires_on_expansion():
    signals = [_sig(f"block-{i:03}", scope_expansion=True) for i in range(THRESHOLD)]
    patterns = _rule_scope_expansion(signals)
    assert any(p.rule_id == "R4" for p in patterns)


# --- R5: forced pass ---

def test_r5_fires_critical():
    signals = [_sig(f"block-{i:03}", forced_pass=True) for i in range(THRESHOLD)]
    patterns = _rule_forced_pass(signals)
    assert any(p.rule_id == "R5" and p.severity == "critical" for p in patterns)


# --- R6: missing duration ---

def test_r6_fires_on_missing():
    signals = [_sig(f"block-{i:03}", duration_actual_h=None, actual_h=None) for i in range(THRESHOLD)]
    for s in signals:
        s.duration_actual_h = None
    patterns = _rule_missing_duration(signals)
    assert any(p.rule_id == "R6" for p in patterns)


# --- R7: L-tier overrun ---

def test_r7_fires_on_l_overruns():
    signals = [_sig(f"block-{i:03}", tier="L", actual_h=16.0, est_days=1.0) for i in range(2)]
    patterns = _rule_tier_l_overrun(signals)
    assert any(p.rule_id == "R7" for p in patterns)


def test_r7_no_fire_below_threshold():
    signals = [_sig("block-001", tier="L", actual_h=16.0, est_days=1.0)]
    patterns = _rule_tier_l_overrun(signals)
    assert not patterns


# --- Integration: analyze() ---

def test_analyze_returns_list():
    patterns = analyze([_sig("block-001")])
    assert isinstance(patterns, list)


def test_analyze_rule_failure_does_not_crash():
    """Passing an empty list should not raise."""
    patterns = analyze([])
    assert isinstance(patterns, list)
