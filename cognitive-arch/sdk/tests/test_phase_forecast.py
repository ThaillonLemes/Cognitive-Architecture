# PURPOSE: Tests for phase_forecast -- forecast() returns a Forecast with a MEASURED/
#          ESTIMATED label, NEVER raises on an empty/malformed arch, the CLI always
#          exits 0 with a dated estimate + label, and a synthetic arch with known
#          velocity yields the expected remaining-block math.
# INPUTS:  tmp_path synthetic arch-roots + the real arch-root.
# OUTPUTS: assertions on Forecast fields, defensive behavior, CLI exit codes, math.
# DEPS:    pytest, pathlib, subprocess, datetime, phase_forecast.
# SEE:     sdk/phase_forecast.py, manifests/block-151-phase-forecast.md, phases/phase-26.md,
#          sdk/velocity_inference.py (block-138 MEASURED/ESTIMATED discipline)

import math
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import phase_forecast as pf

_ARCH_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Synthetic arch builders
# ---------------------------------------------------------------------------

def _make_arch(
    tmp_path: Path,
    *,
    phase: int = 99,
    block_rows: int = 5,
    done_rows: int = 2,
    measured_blocks: int = 3,
    measured_tier: str = "S",
    measured_hours: float = 2.0,
) -> Path:
    """Build a minimal arch-root the forecaster can read end to end.

    - STATE.md sets the current phase (p:N).
    - phases/phase-N.md carries a block table with `block_rows` rows of which
      `done_rows` are marked `| done |` (these drive remaining = block_rows - done_rows).
    - BLOCK_LOG + retros add `measured_blocks` completed blocks of `measured_tier`
      each taking `measured_hours` (these drive the velocity mean + confidence).
    """
    (tmp_path / "phases").mkdir(parents=True, exist_ok=True)
    (tmp_path / "blocks").mkdir(parents=True, exist_ok=True)
    (tmp_path / "manifests").mkdir(parents=True, exist_ok=True)

    (tmp_path / "STATE.md").write_text(f"p:{phase} status:active\n", encoding="utf-8")

    # Phase file with a block index table: `done_rows` done, rest pending.
    rows = []
    for i in range(block_rows):
        status = "done" if i < done_rows else "pending"
        rows.append(f"| block-{700 + i:03d} | T{i} | M | {status} | manifests/x.md |")
    table = (
        "| Block | Title | Tier | Status | Manifest |\n"
        "|-------|-------|------|--------|----------|\n"
        + "\n".join(rows)
        + "\n"
    )
    (tmp_path / "phases" / f"phase-{phase}.md").write_text(
        f"---\nid: phase-{phase}\nstatus: active\n---\n\n# Phase {phase}\n\n{table}",
        encoding="utf-8",
    )

    # Completed blocks with measured durations -> velocity samples.
    log_lines = []
    for i in range(measured_blocks):
        bid = f"block-{800 + i:03d}"
        log_lines.append(f"{bid} done 2026-05-2{i % 9} | tier:{measured_tier}")
        retro = tmp_path / "blocks" / f"{bid}-test.md"
        retro.write_text(
            f"---\nid: {bid}\nstatus: done\ntier: {measured_tier}\n"
            f"actual_duration_hours: {measured_hours}\n---\n\n# retro\n",
            encoding="utf-8",
        )
    (tmp_path / "blocks" / "BLOCK_LOG.md").write_text(
        "# BLOCK LOG\n\n" + "\n".join(log_lines) + "\n", encoding="utf-8"
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Forecast dataclass shape
# ---------------------------------------------------------------------------

def test_forecast_dataclass_fields():
    fc = pf.Forecast(remaining_blocks=3, est_days=2.0, confidence="MEASURED",
                     completion_estimate="2026-01-01")
    assert fc.remaining_blocks == 3
    assert fc.est_days == 2.0
    assert fc.confidence == "MEASURED"
    assert fc.completion_estimate == "2026-01-01"


# ---------------------------------------------------------------------------
# forecast() returns a labelled Forecast
# ---------------------------------------------------------------------------

def test_forecast_returns_forecast_with_confidence_label():
    fc = pf.forecast(_ARCH_ROOT)
    assert isinstance(fc, pf.Forecast)
    assert fc.confidence in ("MEASURED", "ESTIMATED")
    assert isinstance(fc.remaining_blocks, int)
    assert isinstance(fc.completion_estimate, str) and fc.completion_estimate


def test_forecast_real_root_completion_is_dated_or_reason():
    fc = pf.forecast(_ARCH_ROOT)
    # On the real root there is an active phase with open blocks -> an ISO date.
    if fc.remaining_blocks > 0 and fc.completion_estimate not in ("unknown", "phase complete"):
        datetime.fromisoformat(fc.completion_estimate)  # raises if not a date


# ---------------------------------------------------------------------------
# Defensive: never raises on empty / malformed arch
# ---------------------------------------------------------------------------

def test_forecast_empty_arch_does_not_raise(tmp_path: Path):
    fc = pf.forecast(tmp_path)  # no STATE, no phases, no blocks
    assert isinstance(fc, pf.Forecast)
    assert fc.confidence in ("MEASURED", "ESTIMATED")
    assert fc.remaining_blocks == 0


def test_forecast_malformed_arch_does_not_raise(tmp_path: Path):
    (tmp_path / "STATE.md").write_text("not a real state :::\x00\x01", encoding="utf-8")
    (tmp_path / "phases").mkdir()
    (tmp_path / "phases" / "phase-99.md").write_text("\x00garbage not yaml", encoding="utf-8")
    fc = pf.forecast(tmp_path)
    assert isinstance(fc, pf.Forecast)


def test_forecast_none_arch_does_not_raise():
    # Path(None) raises internally -> must be caught and degrade.
    fc = pf.forecast(None)
    assert isinstance(fc, pf.Forecast)
    assert fc.confidence == "ESTIMATED"


def test_phase_block_counts_empty_arch_is_zero(tmp_path: Path):
    assert pf.phase_block_counts(tmp_path) == (0, 0)


def test_measured_velocity_empty_arch_uses_defaults(tmp_path: Path):
    means, counts = pf.measured_velocity(tmp_path)
    assert means == pf.VELOCITY_DEFAULTS
    assert counts == {"S": 0, "M": 0, "L": 0}


# ---------------------------------------------------------------------------
# Known-velocity synthetic arch: remaining-block math is exact
# ---------------------------------------------------------------------------

def test_synthetic_known_velocity_yields_expected_math(tmp_path: Path):
    # 5 block rows, 2 done -> remaining 3. Three S-tier blocks at 2.0h each ->
    # S mean 2.0 (3 samples => MEASURED). remaining_hours = 3 * 2.0 = 6.0;
    # est_days = ceil(6/4) = 2; completion = today(UTC) + 2 days.
    arch = _make_arch(tmp_path, block_rows=5, done_rows=2,
                      measured_blocks=3, measured_tier="S", measured_hours=2.0)
    fc = pf.forecast(arch)

    assert fc.remaining_blocks == 3
    assert fc.confidence == "MEASURED"
    expected_days = math.ceil((3 * 2.0) / pf.HOURS_PER_DAY)
    assert fc.est_days == float(expected_days)
    expected_date = (datetime.now(timezone.utc).date()
                     + timedelta(days=expected_days)).isoformat()
    assert fc.completion_estimate == expected_date


def test_synthetic_thin_history_is_estimated(tmp_path: Path):
    # Only 2 measured S samples (< MEASURED_MIN_SAMPLES=3) -> ESTIMATED, and the
    # per-block hours fall back to the S default, not the 2 thin samples' mean...
    # NOTE: with samples present the mean is still used for hours; the LABEL is
    # what must stay honest (ESTIMATED) when the sample count is thin.
    arch = _make_arch(tmp_path, block_rows=4, done_rows=1,
                      measured_blocks=2, measured_tier="S", measured_hours=2.0)
    fc = pf.forecast(arch)
    assert fc.remaining_blocks == 3
    assert fc.confidence == "ESTIMATED"


def test_synthetic_all_done_reports_phase_complete(tmp_path: Path):
    arch = _make_arch(tmp_path, block_rows=3, done_rows=3,
                      measured_blocks=3, measured_tier="S", measured_hours=1.0)
    fc = pf.forecast(arch)
    assert fc.remaining_blocks == 0
    assert fc.completion_estimate == "phase complete"
    assert fc.est_days == 0.0


def test_supplied_velocity_means_overrides_measurement(tmp_path: Path):
    # health_report passes its own means; forecast must use them for the hours.
    arch = _make_arch(tmp_path, block_rows=5, done_rows=0,
                      measured_blocks=3, measured_tier="S", measured_hours=2.0)
    # Force S=4.0h/block -> remaining 5 * 4.0 = 20h -> ceil(20/4)=5 days.
    fc = pf.forecast(arch, velocity_means={"S": 4.0, "M": 3.5, "L": 9.0})
    assert fc.remaining_blocks == 5
    expected_days = math.ceil((5 * 4.0) / pf.HOURS_PER_DAY)
    assert fc.est_days == float(expected_days)


# ---------------------------------------------------------------------------
# CLI -- always exits 0, prints a dated estimate + label, ASCII-safe
# ---------------------------------------------------------------------------

def _run_cli(args: list[str], cwd: Path = _ARCH_ROOT) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1252"  # provoke the Windows encoding failure mode
    return subprocess.run(
        [sys.executable, str(_SDK_DIR / "phase_forecast.py"), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=60, cwd=str(cwd),
    )


def test_cli_help_exits_zero():
    r = _run_cli(["--help"])
    assert r.returncode == 0
    assert "usage:" in r.stdout.lower()
    assert "Traceback" not in (r.stdout + r.stderr)


def test_cli_real_root_exits_zero_with_dated_label():
    r = _run_cli(["--arch-root", "."])
    assert r.returncode == 0, f"CLI must exit 0; got {r.returncode}: {r.stderr}"
    assert "Traceback" not in (r.stdout + r.stderr)
    assert "Completion:" in r.stdout
    # A MEASURED or ESTIMATED label must be present.
    assert ("MEASURED" in r.stdout) or ("ESTIMATED" in r.stdout)


def test_cli_synthetic_arch_exits_zero(tmp_path: Path):
    arch = _make_arch(tmp_path)
    r = _run_cli(["--arch-root", str(arch)], cwd=arch)
    assert r.returncode == 0, f"CLI must exit 0; got {r.returncode}: {r.stderr}"
    assert "Traceback" not in (r.stdout + r.stderr)
    assert "Remaining blocks: 3" in r.stdout


def test_cli_empty_arch_exits_zero(tmp_path: Path):
    r = _run_cli(["--arch-root", str(tmp_path)], cwd=tmp_path)
    assert r.returncode == 0
    assert "Traceback" not in (r.stdout + r.stderr)
