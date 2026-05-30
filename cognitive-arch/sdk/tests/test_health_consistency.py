# PURPOSE: The block-149 regression — prove the two health instruments can never
#          diverge again. On the real arch-root, the score from audit (to_dict /
#          score()), the score rendered by health_report, and health_model.compute()
#          are the SAME number; the 32-vs-100 / 30-vs-0 contradiction is dead. Also
#          pins the meaningfulness rules: accepted drift (governance/known-drift.md)
#          costs 0, the score is a sensible value in (0,100], and a missing
#          known-drift.md degrades to "no exclusion" without crashing.
# INPUTS:  the real arch-root + synthetic roots (tmp_path) + monkeypatch
# OUTPUTS: assertions on audit.run_audit / health_report.generate_report / health_model
# DEPS:    pytest, pathlib, re, io, contextlib, audit, health_report, health_model
# SEE:     sdk/health_model.py, sdk/audit.py, sdk/health_report.py,
#          manifests/block-149-reconcile-health.md, governance/known-drift.md

import contextlib
import io
import re
import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import audit
import health_model
import health_report

_ARCH_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers — pull each instrument's headline score the way a user would see it
# ---------------------------------------------------------------------------

def _audit_score(arch_root: Path) -> int:
    """audit's reported score (run it quietly; read the canonical score())."""
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        result = audit.run_audit(arch_root, as_json=True)
    # to_dict()['score'] and score() must agree — both are the canonical number.
    assert result.to_dict()["score"] == result.score()
    return result.score()


_REPORT_SCORE_RE = re.compile(r"Score:\s*(\d+)/100", re.MULTILINE)


def _health_report_score(arch_root: Path) -> int:
    """The score health_report actually renders in its Audit Score section."""
    section = health_report._section_audit(arch_root)
    m = _REPORT_SCORE_RE.search(section)
    assert m, f"no 'Score: N/100' in rendered audit section:\n{section}"
    return int(m.group(1))


def _full_report_score(arch_root: Path) -> int:
    """Parse the score out of the FULL rendered report (what the user reads)."""
    report = health_report.generate_report(arch_root)
    # Section 1 is the audit score; take the first Score: N/100 in the document.
    m = _REPORT_SCORE_RE.search(report)
    assert m, "no 'Score: N/100' in the full health report"
    return int(m.group(1))


# ---------------------------------------------------------------------------
# THE regression: audit == health_report == health_model on the real root
# ---------------------------------------------------------------------------

def test_all_three_instruments_report_the_same_score():
    model_score = health_model.compute(_ARCH_ROOT).score
    audit_score = _audit_score(_ARCH_ROOT)
    report_score = _health_report_score(_ARCH_ROOT)

    assert audit_score == model_score, (
        f"audit ({audit_score}) != health_model ({model_score}) — the scorers diverged"
    )
    assert report_score == model_score, (
        f"health_report ({report_score}) != health_model ({model_score}) — the scorers diverged"
    )
    # transitively: audit == health_report, the exact 32-vs-100 contradiction killed.
    assert audit_score == report_score


def test_full_rendered_report_matches_model():
    """Belt-and-suspenders: the number in the whole generated document agrees too."""
    assert _full_report_score(_ARCH_ROOT) == health_model.compute(_ARCH_ROOT).score


def test_audit_to_dict_score_is_the_model_score():
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        result = audit.run_audit(_ARCH_ROOT, as_json=True)
    assert result.to_dict()["score"] == health_model.compute(_ARCH_ROOT).score


# ---------------------------------------------------------------------------
# Meaningfulness: the real-root score is non-zero, in (0, 100]
# ---------------------------------------------------------------------------

def test_real_root_score_is_meaningful_not_floored_at_zero():
    score = health_model.compute(_ARCH_ROOT).score
    assert 0 < score <= 100, f"expected a meaningful (0,100] score, got {score}"


def test_real_root_score_is_explained_by_top_drags():
    """score == 100 - sum(top-cost factors); the headline is fully accounted for."""
    health = health_model.compute(_ARCH_ROOT)
    # Every point deducted is attributable to a factor (the load-bearing invariant).
    assert health.score == max(0, 100 - sum(f.cost for f in health.factors))
    # And a non-100 score has at least one drag explaining it.
    if health.score < 100:
        assert health.top_drags(99), "score < 100 but no drag explains it"


# ---------------------------------------------------------------------------
# Accepted-drift exclusion: a known-drift block adds NO cost
# ---------------------------------------------------------------------------

def test_known_drift_blocks_are_parsed_from_real_ledger():
    accepted = health_model.accepted_drift_blocks(_ARCH_ROOT)
    # known-drift.md documents INV2 blocks 061..085 and INV3 blocks 108..111.
    for n in ("061", "085", "108", "111"):
        assert n in accepted, f"expected accepted-drift block {n} to be parsed"
    # A block NOT in the ledger must not be excused.
    assert "999" not in accepted


def test_accepted_drift_warning_costs_zero(tmp_path):
    """A warn whose block is accepted moves to a 0-cost factor; an un-accepted one drags."""
    accepted = {"061"}
    # Two invariant warns: one accepted (block-061), one real (block-999).
    counted, excused = health_model._split_accepted(
        [
            "block-061 is 'done' in BLOCK_LOG but has no retro",
            "block-999 is 'done' in BLOCK_LOG but has no retro",
        ],
        accepted,
    )
    assert len(excused) == 1 and "061" in excused[0]
    assert len(counted) == 1 and "999" in counted[0]


def test_excluding_drift_changes_the_score(monkeypatch, tmp_path):
    """With the SAME violations, excusing the accepted ones yields a higher score."""
    import invariant_check

    class _V:
        def __init__(self, msg):
            self.severity = "warn"
            self.message = msg

    # 3 warns: blocks 061 & 062 are accepted; block-999 is real.
    violations = [_V("block-061 no retro"), _V("block-062 no retro"), _V("block-999 no retro")]
    monkeypatch.setattr(invariant_check, "run_all", lambda root: violations)

    with_exclusion = health_model._invariant_factors(tmp_path, accepted={"061", "062"})
    without_exclusion = health_model._invariant_factors(tmp_path, accepted=set())

    cost_with = sum(f.cost for f in with_exclusion)
    cost_without = sum(f.cost for f in without_exclusion)
    # Excusing 2 of 3 warns must cost strictly less (2 * unit less, here 4 pts).
    assert cost_with < cost_without
    assert cost_with == 1 * health_model.COST_INVARIANT_WARN
    assert cost_without == 3 * health_model.COST_INVARIANT_WARN
    # The excused two surface as a 0-cost transparency factor.
    assert any(f.key == "invariant.accepted" and f.cost == 0 for f in with_exclusion)


# ---------------------------------------------------------------------------
# Defensiveness: missing known-drift.md => no exclusion, never a crash
# ---------------------------------------------------------------------------

def test_missing_known_drift_file_yields_empty_set_no_crash(tmp_path):
    # tmp_path has no governance/known-drift.md at all.
    assert health_model.accepted_drift_blocks(tmp_path) == set()


def test_compute_does_not_crash_without_known_drift(tmp_path):
    # A bare root (no known-drift.md, minimal files) must still produce a score.
    health = health_model.compute(tmp_path)
    assert 0 <= health.score <= 100


def test_known_drift_parser_handles_id_and_numeric_ranges(tmp_path):
    gov = tmp_path / "governance"
    gov.mkdir()
    (gov / "known-drift.md").write_text(
        "blocks 061 through 063 are accepted.\n"
        "also block-100 … block-102 inclusive.\n"
        "and a lone block-200.\n",
        encoding="utf-8",
    )
    accepted = health_model.accepted_drift_blocks(tmp_path)
    for n in ("061", "062", "063", "100", "101", "102", "200"):
        assert n in accepted, f"{n} should be accepted"
    assert "064" not in accepted


def test_metadata_block_mentions_are_not_excused(tmp_path):
    """A block named only in metadata/prose (not an '## INV' acceptance) is NOT excused.

    Guards the real-ledger case: 'Recorded by: block-147' and 'After block-147 ...'
    must not make block-147 an accepted-drift block.
    """
    gov = tmp_path / "governance"
    gov.mkdir()
    (gov / "known-drift.md").write_text(
        "# Recorded by: block-147 (capstone)\n\n"
        "## Purpose\n\n"
        "After block-147 the root has 0 CRITICAL.\n\n"
        "## INV2 — done blocks without a retro (block-061 … block-063)\n\n"
        "blocks 061 through 063 are accepted history.\n",
        encoding="utf-8",
    )
    accepted = health_model.accepted_drift_blocks(tmp_path)
    assert {"061", "062", "063"} <= accepted
    assert "147" not in accepted, "block-147 is metadata, not accepted drift"


# ---------------------------------------------------------------------------
# Per-category light-warn cap: a pile of minor warns can't alone zero the score
# ---------------------------------------------------------------------------

def test_warn_category_cap_prevents_zeroing(monkeypatch, tmp_path):
    import invariant_check

    class _V:
        def __init__(self, msg):
            self.severity = "warn"
            self.message = msg

    # 100 un-accepted warns would be 200 pts uncapped — far past 100.
    violations = [_V(f"unrelated warn {i}") for i in range(100)]
    monkeypatch.setattr(invariant_check, "run_all", lambda root: violations)

    factors = health_model._invariant_factors(tmp_path, accepted=set())
    warn = next(f for f in factors if f.key == "invariant.warn")
    assert warn.cost == health_model.WARN_CATEGORY_CAP
    # One light category alone cannot exceed the cap (so it can't solo-zero a root).
    assert warn.cost <= 100


def test_audit_score_fallback_is_visible(tmp_path, monkeypatch):
    """When health_model.compute fails, audit.score() must emit a visible warning."""
    import sys
    sys.path.insert(0, str(Path("cognitive-arch/sdk").resolve()))

    # Force health_model.compute to raise so the fallback path is exercised.
    def _boom(root):
        raise RuntimeError("simulated compute failure for fallback test")

    monkeypatch.setattr(health_model, "compute", _boom)

    from audit import AuditResult
    r = AuditResult(arch_root=tmp_path)
    # score() should not raise and should add a warning
    import io, contextlib
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        score = r.score()
    assert isinstance(score, int)
    # A warning should have been added (the fallback must be visible)
    assert any("health_model" in w.lower() or "legacy" in w.lower() for w in r.warnings), (
        f"Expected a visible fallback warning, got warnings: {r.warnings}"
    )
