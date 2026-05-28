# sdk/tests/test_recommendation_engine.py
# PURPOSE: Unit tests for recommendation_engine.py mapping rules.
# DEPS:    pytest, sdk/recommendation_engine, sdk/pattern_schema

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from pattern_schema import Pattern
from recommendation_schema import Recommendation
from recommendation_engine import recommend, _rec_r1, _rec_r2, _rec_r3, _rec_r4, _rec_r5, _rec_r6, _rec_r7


def _pat(rule_id="R1", name="axiom-p3-repeated-violation", severity="warn",
         occurrences=3, evidence=None, first="block-001", last="block-003"):
    return Pattern(
        name=name, description="test pattern", severity=severity,
        evidence=evidence or [f"block-{i:03}" for i in range(occurrences)],
        first_detected=first, last_detected=last,
        occurrences=occurrences, rule_id=rule_id,
    )


# --- R1 ---

def test_r1_produces_recommendation():
    p = _pat(rule_id="R1", name="axiom-p3-repeated-violation")
    r = _rec_r1(p)
    assert r.rule_id == "R1"
    assert "P3" in r.title
    assert r.priority in ("high", "medium", "low")


def test_r1_high_priority_at_5_plus():
    p = _pat(rule_id="R1", occurrences=5)
    r = _rec_r1(p)
    assert r.priority == "high"


def test_r1_medium_priority_below_5():
    p = _pat(rule_id="R1", occurrences=3)
    r = _rec_r1(p)
    assert r.priority == "medium"


# --- R2 ---

def test_r2_produces_recommendation():
    p = _pat(rule_id="R2", name="duration-overrun-recurring")
    r = _rec_r2(p)
    assert r.rule_id == "R2"
    assert "estimate" in r.title.lower() or "duration" in r.title.lower()
    assert r.priority == "medium"


# --- R3 ---

def test_r3_is_high_priority():
    p = _pat(rule_id="R3", name="gate-failures-recurring")
    r = _rec_r3(p)
    assert r.priority == "high"


# --- R4 ---

def test_r4_references_q6():
    p = _pat(rule_id="R4", name="scope-expansion-recurring")
    r = _rec_r4(p)
    assert "Q6" in r.rationale or "Q6" in r.suggested_action


# --- R5 ---

def test_r5_is_high_priority():
    p = _pat(rule_id="R5", name="forced-pass-clustering", severity="critical")
    r = _rec_r5(p)
    assert r.priority == "high"


# --- R6 ---

def test_r6_is_low_priority():
    p = _pat(rule_id="R6", name="velocity-data-gap", severity="info")
    r = _rec_r6(p)
    assert r.priority == "low"


# --- R7 ---

def test_r7_medium_priority():
    p = _pat(rule_id="R7", name="l-tier-systematic-overrun", occurrences=2)
    r = _rec_r7(p)
    assert r.priority == "medium"


# --- recommend() integration ---

def test_recommend_populates_pattern_recommendation():
    p = _pat(rule_id="R1", name="axiom-p3-repeated-violation")
    recommend([p])
    assert p.recommendation != ""


def test_recommend_sorts_by_priority():
    patterns = [
        _pat(rule_id="R6", name="velocity-data-gap", severity="info"),
        _pat(rule_id="R5", name="forced-pass-clustering", severity="critical"),
        _pat(rule_id="R2", name="duration-overrun-recurring"),
    ]
    recs = recommend(patterns)
    assert recs[0].priority == "high"
    assert recs[-1].priority == "low"


def test_recommend_unknown_rule_skipped():
    p = _pat(rule_id="R99", name="unknown-pattern")
    recs = recommend([p])
    assert recs == []


def test_recommend_empty_input():
    assert recommend([]) == []


def test_priority_rank():
    r = Recommendation("x", "t", "rat", "high", "action", "R1")
    assert r.priority_rank == 0
    r.priority = "low"
    assert r.priority_rank == 2
