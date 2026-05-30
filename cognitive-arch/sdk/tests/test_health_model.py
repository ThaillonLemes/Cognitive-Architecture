# PURPOSE: Tests for the canonical health model — pins the load-bearing invariant
#          (score == max(0, 100 - sum(factor.cost))), top_drags ranking, real-root
#          compute shape, and the defensive-import contract (a failing/erroring
#          invariant_check yields a 0-cost factor, never a crash).
# INPUTS:  the real arch-root + synthetic factor lists + monkeypatch on imports
# OUTPUTS: assertions on HealthScore / Factor / compute() / main()
# DEPS:    pytest, pathlib, subprocess, health_model
# SEE:     sdk/health_model.py, manifests/block-148-health-model.md, phases/phase-26.md

import builtins
import os
import subprocess
import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import health_model
from health_model import Factor, HealthScore, compute

_ARCH_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Load-bearing invariant: score == max(0, 100 - sum(costs))
# ---------------------------------------------------------------------------

def test_score_equals_100_minus_sum_of_costs():
    hs = HealthScore(factors=[
        Factor("a", 15, "d", "f"),
        Factor("b", 2, "d", "f"),
        Factor("c", 0, "d", "f"),
    ])
    assert hs.total_cost == 17
    assert hs.score == max(0, 100 - 17) == 83


def test_score_is_clamped_at_zero_never_negative():
    hs = HealthScore(factors=[Factor("huge", 250, "d", "f")])
    assert hs.score == 0  # max(0, 100-250), not -150


def test_empty_score_is_100():
    assert HealthScore(factors=[]).score == 100


def test_invariant_holds_for_real_root():
    hs = compute(_ARCH_ROOT)
    assert hs.score == max(0, 100 - sum(f.cost for f in hs.factors))


# ---------------------------------------------------------------------------
# top_drags(n): the n highest-cost factors, sorted descending
# ---------------------------------------------------------------------------

def test_top_drags_returns_n_highest_cost_sorted_desc():
    hs = HealthScore(factors=[
        Factor("low", 2, "d", "f"),
        Factor("high", 30, "d", "f"),
        Factor("mid", 10, "d", "f"),
        Factor("zero", 0, "d", "f"),
    ])
    drags = hs.top_drags(2)
    assert [f.key for f in drags] == ["high", "mid"]
    assert [f.cost for f in drags] == [30, 10]


def test_top_drags_excludes_zero_cost_factors():
    hs = HealthScore(factors=[Factor("z1", 0, "d", "f"), Factor("z2", 0, "d", "f")])
    assert hs.top_drags(3) == []


def test_top_drags_default_n_is_3():
    hs = HealthScore(factors=[Factor(f"k{i}", i + 1, "d", "f") for i in range(10)])
    assert len(hs.top_drags()) == 3
    # highest costs are 10, 9, 8
    assert [f.cost for f in hs.top_drags()] == [10, 9, 8]


def test_top_drags_each_carries_nonempty_fix():
    hs = compute(_ARCH_ROOT)
    for f in hs.top_drags(5):
        assert f.fix.strip(), f"factor {f.key} has an empty fix"


def test_top_drags_handles_n_larger_than_factor_count():
    hs = HealthScore(factors=[Factor("only", 5, "d", "f")])
    assert len(hs.top_drags(99)) == 1


# ---------------------------------------------------------------------------
# compute() on the real arch-root: well-formed HealthScore
# ---------------------------------------------------------------------------

def test_compute_real_root_returns_healthscore_with_factors():
    hs = compute(_ARCH_ROOT)
    assert isinstance(hs, HealthScore)
    assert hs.factors, "expected a non-empty factor breakdown"
    assert 0 <= hs.score <= 100


def test_compute_accepts_str_path():
    hs = compute(str(_ARCH_ROOT))
    assert isinstance(hs, HealthScore)
    assert 0 <= hs.score <= 100


def test_compute_includes_namespaced_factor_keys():
    keys = {f.key for f in compute(_ARCH_ROOT).factors}
    # audit + invariant + hot categories must all be represented (namespaced).
    assert any(k.startswith("audit.") for k in keys)
    assert any(k.startswith("invariant.") for k in keys)
    assert any(k.startswith("hot.") for k in keys)


# ---------------------------------------------------------------------------
# Synthetic arch-roots: clean -> 100; injected signals cost the expected points
# ---------------------------------------------------------------------------

def _make_clean_root(tmp_path: Path) -> Path:
    """A minimal arch-root that audit passes (all HOT files, small, valid)."""
    for f in audit_hot_files():
        (tmp_path / f).write_text("# ok\nkey: value\n", encoding="utf-8")
    (tmp_path / "blocks").mkdir()
    (tmp_path / "blocks" / "BLOCK_LOG.md").write_text("# log\n", encoding="utf-8")
    return tmp_path


def audit_hot_files() -> list[str]:
    import audit
    return list(audit.HOT_FILES)


def test_audit_warn_factor_cost_scales_with_count(monkeypatch, tmp_path):
    # Force a known audit result so the cost math is deterministic.
    import audit

    class _FakeResult:
        errors = ["e1", "e2"]
        warnings = ["w1", "w2", "w3"]

    # health_model now calls run_audit(root, as_json=True) (skips audit's score
    # block to avoid re-entering compute()), so the stub accepts extra kwargs.
    monkeypatch.setattr(audit, "run_audit", lambda root, *a, **kw: _FakeResult())
    # Also neutralise invariants + hot so only audit factors carry cost.
    monkeypatch.setattr(health_model, "_invariant_factors", lambda root: [])
    monkeypatch.setattr(health_model, "_hot_boot_factor",
                        lambda root: Factor("hot.boot_over_budget", 0, "ok", "f"))

    hs = compute(tmp_path)
    by_key = {f.key: f for f in hs.factors}
    assert by_key["audit.errors"].cost == 2 * health_model.COST_AUDIT_ERROR
    assert by_key["audit.warnings"].cost == 3 * health_model.COST_AUDIT_WARN
    expected = 2 * health_model.COST_AUDIT_ERROR + 3 * health_model.COST_AUDIT_WARN
    assert hs.score == max(0, 100 - expected)


def test_clean_signals_yield_score_100(monkeypatch, tmp_path):
    import audit

    class _CleanResult:
        errors: list[str] = []
        warnings: list[str] = []

    monkeypatch.setattr(audit, "run_audit", lambda root, *a, **kw: _CleanResult())
    monkeypatch.setattr(health_model, "_invariant_factors", lambda root: [])
    monkeypatch.setattr(health_model, "_hot_boot_factor",
                        lambda root: Factor("hot.boot_over_budget", 0, "ok", "f"))
    hs = compute(tmp_path)
    assert hs.score == 100
    assert hs.top_drags() == []


# ---------------------------------------------------------------------------
# HOT-boot-over-budget factor
# ---------------------------------------------------------------------------

def test_hot_boot_over_budget_costs_points(tmp_path):
    # Write a HOT file far over the 4000-token (16000-char) budget.
    (tmp_path / "PROTOCOLS.md").write_text("x" * 80000, encoding="utf-8")
    f = health_model._hot_boot_factor(tmp_path)
    assert f.cost == health_model.COST_HOT_OVER_BUDGET
    assert "over" in f.detail


def test_hot_boot_within_budget_is_zero_cost(tmp_path):
    (tmp_path / "STATE.md").write_text("small\n", encoding="utf-8")
    f = health_model._hot_boot_factor(tmp_path)
    assert f.cost == 0


# ---------------------------------------------------------------------------
# Defensive import: a missing/erroring invariant_check -> 0-cost factor, no crash
# ---------------------------------------------------------------------------

def test_invariant_import_failure_yields_zero_cost_factor(monkeypatch):
    real_import = builtins.__import__

    def _boom(name, *args, **kwargs):
        if name == "invariant_check":
            raise ImportError("simulated: invariant_check absent")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _boom)
    factors = health_model._invariant_factors(_ARCH_ROOT)
    assert len(factors) == 1
    assert factors[0].key == "invariant.unavailable"
    assert factors[0].cost == 0
    assert factors[0].fix.strip()


def test_compute_survives_invariant_import_failure(monkeypatch):
    real_import = builtins.__import__

    def _boom(name, *args, **kwargs):
        if name == "invariant_check":
            raise ImportError("simulated absence")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _boom)
    hs = compute(_ARCH_ROOT)  # must not raise
    assert 0 <= hs.score <= 100
    assert any(f.key == "invariant.unavailable" for f in hs.factors)


def test_invariant_engine_error_yields_zero_cost_factor(monkeypatch):
    import invariant_check

    def _raise(root):
        raise RuntimeError("simulated engine crash")

    monkeypatch.setattr(invariant_check, "run_all", _raise)
    factors = health_model._invariant_factors(_ARCH_ROOT)
    assert len(factors) == 1
    assert factors[0].key == "invariant.unavailable"
    assert factors[0].cost == 0


# ---------------------------------------------------------------------------
# CLI smoke
# ---------------------------------------------------------------------------

def _run_cli(args: list[str]) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1252"  # provoke any UTF-8 crash on Windows pipes
    return subprocess.run(
        [sys.executable, str(_SDK_DIR / "health_model.py"), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=60, cwd=str(_ARCH_ROOT),
    )


def test_cli_help_exits_zero():
    r = _run_cli(["--help"])
    assert r.returncode == 0, r.stderr
    assert "usage:" in r.stdout.lower()
    assert "Traceback" not in (r.stdout + r.stderr)


def test_cli_prints_score_and_top_drags():
    r = _run_cli(["--arch-root", "."])
    assert r.returncode == 0, r.stderr
    assert "Traceback" not in (r.stdout + r.stderr)
    assert "Health:" in r.stdout and "/100" in r.stdout
    assert "Top drags" in r.stdout
    # The score line must be within [0,100].
    import re
    m = re.search(r"Health:\s*(\d+)/100", r.stdout)
    assert m and 0 <= int(m.group(1)) <= 100
