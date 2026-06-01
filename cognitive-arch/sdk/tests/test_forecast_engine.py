# sdk/tests/test_forecast_engine.py
# PURPOSE: Validate forecast engine: HTML generated, confidence band, delivery estimate,
#          parallelism recommendation, meeting adjustment.
# BLOCK:   block-174

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


def _make_arch(tmp: str, blocks_with_hours: list[float] | None = None) -> Path:
    arch = Path(tmp) / "arch"
    gov = arch / "governance"
    gov.mkdir(parents=True)
    (arch / "manifests").mkdir()
    (arch / "blocks").mkdir()
    (arch / "sdk").mkdir()
    (arch / "STATE.md").write_text("# STATE\n\np:32 status:active\n", encoding="utf-8")
    (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")

    log_lines = []
    for i, hours in enumerate(blocks_with_hours or []):
        bid = f"block-{900+i}"
        log_lines.append(f"{bid} done - 2026-06-01")
        (arch / "manifests" / f"{bid}-test.md").write_text(
            f"---\nid: {bid}\nsize: S\nactual_duration_hours: {hours}\n---\n",
            encoding="utf-8",
        )
    (arch / "blocks" / "BLOCK_LOG.md").write_text("\n".join(log_lines), encoding="utf-8")
    return arch


# ---------------------------------------------------------------------------
# Velocity and confidence
# ---------------------------------------------------------------------------

def test_html_generated():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp, [2.0, 1.5, 3.0, 2.5, 1.8])
        from forecast_engine import generate_forecast_html
        path = generate_forecast_html(arch, "acme")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "Forecast" in text


def test_confidence_medium_with_5_blocks():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp, [2.0, 1.5, 3.0, 2.5, 1.8])
        from forecast_engine import _load_velocity_history, _confidence_band
        history = _load_velocity_history(arch)
        assert len(history) == 5
        assert _confidence_band(len(history)) == "MÉDIO"


def test_confidence_low_with_2_blocks():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp, [2.0, 3.0])
        from forecast_engine import _load_velocity_history, _confidence_band
        history = _load_velocity_history(arch)
        assert _confidence_band(len(history)) == "BAIXO"


def test_confidence_high_with_11_blocks():
    with tempfile.TemporaryDirectory() as tmp:
        hours = [2.0] * 11
        arch = _make_arch(tmp, hours)
        from forecast_engine import _load_velocity_history, _confidence_band
        history = _load_velocity_history(arch)
        assert _confidence_band(len(history)) == "ALTO"


def test_no_history_no_crash():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp, [])
        from forecast_engine import generate_forecast_html
        path = generate_forecast_html(arch, "empty")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "insuficiente" in text.lower() or "BAIXO" in text


# ---------------------------------------------------------------------------
# Delivery estimate
# ---------------------------------------------------------------------------

def test_delivery_estimate_with_open_tickets():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp, [2.0] * 8)  # avg 2h/ticket → 3 tickets/day
        from forecast_engine import generate_forecast_html
        path = generate_forecast_html(arch, "acme", open_tickets=6)
        text = path.read_text(encoding="utf-8")
        # Should show delivery estimate
        assert "dias úteis" in text or "Estimativa" in text


# ---------------------------------------------------------------------------
# Parallelism
# ---------------------------------------------------------------------------

def test_parallelism_recommended_with_5_clean_blocks():
    with tempfile.TemporaryDirectory() as tmp:
        # 5 blocks with > 30min each (avg > 0.5h)
        arch = _make_arch(tmp, [2.0, 1.5, 3.0, 2.5, 1.8])
        from forecast_engine import _load_velocity_history, _parallelism_recommendation
        history = _load_velocity_history(arch)
        rec = _parallelism_recommendation(history)
        assert "2 tickets" in rec or "paralelo" in rec


def test_parallelism_not_recommended_with_loopbacks():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp, [2.0] * 5)
        from forecast_engine import _parallelism_recommendation, _load_velocity_history
        history = _load_velocity_history(arch)
        rec = _parallelism_recommendation(history, loop_back_count=2)
        assert "1 ticket" in rec


# ---------------------------------------------------------------------------
# phase_forecast not broken
# ---------------------------------------------------------------------------

def test_phase_forecast_still_runs():
    """Verify phase_forecast.py was not broken by block-174 changes."""
    from phase_forecast import Forecast
    assert Forecast is not None


if __name__ == "__main__":
    test_html_generated()
    test_confidence_medium_with_5_blocks()
    test_confidence_low_with_2_blocks()
    test_confidence_high_with_11_blocks()
    test_no_history_no_crash()
    test_delivery_estimate_with_open_tickets()
    test_parallelism_recommended_with_5_clean_blocks()
    test_parallelism_not_recommended_with_loopbacks()
    test_phase_forecast_still_runs()
    print("All block-174 tests passed.")
