# PURPOSE: Tests for risk_forecast -- a known-bad manifest fires >=1 heuristic with a
#          rationale; a known-good one fires none; assess() never raises on a
#          malformed/missing manifest; the CLI always exits 0 (advisory contract).
# INPUTS:  tmp_path synthetic manifests + the real arch-root.
# OUTPUTS: assertions on RiskFlag fields, assess() behavior, CLI exit codes.
# DEPS:    pytest, pathlib, subprocess, risk_forecast
# SEE:     sdk/risk_forecast.py, manifests/block-150-risk-forecast.md, phases/phase-26.md

import os
import subprocess
import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import risk_forecast as rf

_ARCH_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Manifest builders
# ---------------------------------------------------------------------------

def _write_manifest(path: Path, *, tier: str, files: list[str], block_id: str = "block-999") -> Path:
    modify_block = "\n".join(f"    - {f}" for f in files)
    path.write_text(
        "---\n"
        f"id: {block_id}\n"
        f"tier: {tier}\n"
        "kind: implementation\n"
        "files:\n"
        "  read:\n"
        "    - sdk/x.py\n"
        "  modify:\n"
        f"{modify_block}\n"
        "  create: []\n"
        "---\n\n# synthetic\n",
        encoding="utf-8",
    )
    return path


def _bad_manifest(tmp_path: Path) -> Path:
    # tier L + 8 files (per orchestrator spec) -> oversized for L? No: L budget=20.
    # But 8 files >= HIGH_FILE_COUNT (7) -> H1 fires; and 10 files would overflow
    # nothing on L. The spec's BAD case is "tier L + 8 files": H1 (high count)
    # must fire. We also build a clearly-oversized variant below.
    files = [f"sdk/mod_{i}.py" for i in range(8)]
    return _write_manifest(tmp_path / "block-901-bad.md", tier="L", files=files)


def _good_manifest(tmp_path: Path) -> Path:
    return _write_manifest(
        tmp_path / "block-902-good.md", tier="S", files=["sdk/a.py", "sdk/b.py"]
    )


# ---------------------------------------------------------------------------
# RiskFlag dataclass shape
# ---------------------------------------------------------------------------

def test_riskflag_fields():
    flag = rf.RiskFlag(heuristic="h", severity="high", rationale="because")
    assert flag.heuristic == "h"
    assert flag.severity == "high"
    assert flag.rationale == "because"
    assert flag.fired is True  # default


# ---------------------------------------------------------------------------
# assess() -- known-bad
# ---------------------------------------------------------------------------

def test_known_bad_fires_at_least_one_flag(tmp_path: Path):
    flags = rf.assess(_bad_manifest(tmp_path), tmp_path)
    assert len(flags) >= 1, "tier-L + 8-file manifest must raise >=1 risk flag"
    for f in flags:
        assert f.fired is True
        assert f.rationale.strip(), "every fired flag must carry a non-empty rationale"
        assert f.severity in ("low", "med", "high")


def test_known_bad_high_file_count_is_scope_expansion(tmp_path: Path):
    flags = rf.assess(_bad_manifest(tmp_path), tmp_path)
    names = {f.heuristic for f in flags}
    assert "scope-expansion-resemblance" in names
    h1 = next(f for f in flags if f.heuristic == "scope-expansion-resemblance")
    assert "scope-expansion" in h1.rationale.lower()


def test_oversized_modify_list_overflows_tier_budget(tmp_path: Path):
    # tier S budget is 4; give it 6 files -> H3 must fire.
    m = _write_manifest(
        tmp_path / "block-903-oversize.md",
        tier="S",
        files=[f"sdk/f_{i}.py" for i in range(6)],
    )
    flags = rf.assess(m, tmp_path)
    names = {f.heuristic for f in flags}
    assert "oversized-modify-list" in names
    h3 = next(f for f in flags if f.heuristic == "oversized-modify-list")
    assert "budget" in h3.rationale.lower()


# ---------------------------------------------------------------------------
# assess() -- known-good
# ---------------------------------------------------------------------------

def test_known_good_fires_no_flags(tmp_path: Path):
    flags = rf.assess(_good_manifest(tmp_path), tmp_path)
    assert flags == [], f"tier-S 2-file manifest must flag nothing, got {flags}"


# ---------------------------------------------------------------------------
# assess() -- never raises (advisory contract)
# ---------------------------------------------------------------------------

def test_assess_missing_manifest_does_not_raise(tmp_path: Path):
    flags = rf.assess(tmp_path / "does-not-exist.md", tmp_path)
    assert flags == []


def test_assess_none_manifest_does_not_raise(tmp_path: Path):
    assert rf.assess(None, tmp_path) == []


def test_assess_malformed_manifest_does_not_raise(tmp_path: Path):
    bad = tmp_path / "block-904-malformed.md"
    bad.write_text("not yaml at all :::\n\x00\x01 garbage", encoding="utf-8")
    # Must return a list, never raise.
    assert isinstance(rf.assess(bad, tmp_path), list)


def test_assess_real_manifest_never_raises():
    real = _ARCH_ROOT / "manifests" / "block-155-e2e-verify.md"
    assert real.is_file(), "fixture manifest missing"
    flags = rf.assess(real, _ARCH_ROOT)
    assert isinstance(flags, list)


# ---------------------------------------------------------------------------
# L-tier history heuristic (MEASURED/ESTIMATED discipline)
# ---------------------------------------------------------------------------

def test_l_tier_thin_history_does_not_overclaim(tmp_path: Path):
    # tmp_path has no retros -> R7 cannot be active -> H2 must NOT fire even on tier L.
    m = _write_manifest(tmp_path / "block-905-l.md", tier="L", files=["sdk/a.py", "sdk/b.py"])
    flags = rf.assess(m, tmp_path)
    assert "l-tier-overrun-history" not in {f.heuristic for f in flags}


# ---------------------------------------------------------------------------
# CLI -- always exits 0
# ---------------------------------------------------------------------------

def _run_cli(args: list[str], cwd: Path = _ARCH_ROOT) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1252"  # provoke the Windows encoding failure mode
    return subprocess.run(
        [sys.executable, str(_SDK_DIR / "risk_forecast.py"), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=60, cwd=str(cwd),
    )


def test_cli_help_exits_zero():
    r = _run_cli(["--help"])
    assert r.returncode == 0
    assert "usage:" in r.stdout.lower()


def test_cli_good_manifest_exits_zero(tmp_path: Path):
    m = _good_manifest(tmp_path)
    r = _run_cli([str(m), "--arch-root", str(tmp_path)])
    assert r.returncode == 0, f"CLI must exit 0 (advisory); got {r.returncode}: {r.stderr}"
    assert "Traceback" not in (r.stdout + r.stderr)
    assert "LOW" in r.stdout and "no risks" in r.stdout.lower()


def test_cli_bad_manifest_exits_zero(tmp_path: Path):
    m = _bad_manifest(tmp_path)
    r = _run_cli([str(m), "--arch-root", str(tmp_path)])
    assert r.returncode == 0, f"CLI must exit 0 even when risks fire; got {r.returncode}"
    assert "Traceback" not in (r.stdout + r.stderr)
    assert "ELEVATED" in r.stdout


def test_cli_block_id_on_real_arch_exits_zero():
    # The frontmatter gate form: --block-id resolves manifests/<id>-*.md.
    r = _run_cli(["--block-id", "block-150", "--arch-root", "."])
    assert r.returncode == 0, f"--block-id form must exit 0; got {r.returncode}: {r.stderr}"
    assert "Traceback" not in (r.stdout + r.stderr)
    assert "Risk forecast" in r.stdout


def test_cli_missing_manifest_exits_zero():
    r = _run_cli(["--block-id", "block-does-not-exist", "--arch-root", "."])
    assert r.returncode == 0
    assert "Traceback" not in (r.stdout + r.stderr)
