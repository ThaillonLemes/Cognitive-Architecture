# PURPOSE: Regression tests for velocity_inference — CLI must not crash on --help,
#          and Path("") must never be treated as a real manifest file.
# INPUTS:  the real arch-root + tmp_path for synthetic manifests
# OUTPUTS: assertions on argparse, _is_real_file guard, infer_duration fallback paths
# DEPS:    pytest, pathlib, subprocess, velocity_inference
# SEE:     sdk/velocity_inference.py, sdk/tests/test_cli_smoke.py, phases/phase-23.md block-138

import os
import subprocess
import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import velocity_inference

_ARCH_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# CLI safety
# ---------------------------------------------------------------------------

def _run_cli(args: list[str]) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1252"
    return subprocess.run(
        [sys.executable, str(_SDK_DIR / "velocity_inference.py"), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=30, cwd=str(_ARCH_ROOT),
    )


def test_help_exits_zero_no_traceback():
    r = _run_cli(["--help"])
    assert r.returncode == 0, f"--help exited {r.returncode}: {r.stderr}"
    assert "Traceback" not in (r.stdout + r.stderr)
    assert "usage:" in r.stdout.lower()


def test_unknown_block_does_not_crash():
    # Pre-fix this raised PermissionError on '.' (Path("").read_text()).
    r = _run_cli(["block-does-not-exist", "--arch-root", "."])
    assert r.returncode == 0, f"unknown block crashed: {r.stderr}"
    assert "Traceback" not in (r.stdout + r.stderr)
    # Falls back to tier-M default
    assert "estimated" in r.stdout


# ---------------------------------------------------------------------------
# _is_real_file guard
# ---------------------------------------------------------------------------

def test_is_real_file_rejects_empty_path():
    assert velocity_inference._is_real_file(Path("")) is False


def test_is_real_file_rejects_dot():
    assert velocity_inference._is_real_file(Path(".")) is False


def test_is_real_file_rejects_directory(tmp_path: Path):
    d = tmp_path / "subdir"
    d.mkdir()
    assert velocity_inference._is_real_file(d) is False


def test_is_real_file_accepts_existing_file(tmp_path: Path):
    f = tmp_path / "x.md"
    f.write_text("hi", encoding="utf-8")
    assert velocity_inference._is_real_file(f) is True


def test_is_real_file_none_returns_false():
    assert velocity_inference._is_real_file(None) is False


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------

def test_files_from_empty_path_returns_empty_list():
    # Pre-fix this called Path("").read_text() → PermissionError on Windows.
    assert velocity_inference._files_from_manifest(Path("")) == []


def test_tier_from_empty_path_defaults_to_M():
    assert velocity_inference._tier_from_manifest(Path("")) == "M"


def test_locate_manifest_returns_none_for_unknown_block(tmp_path: Path):
    # Tmp path has no manifests/ dir.
    assert velocity_inference._locate_manifest("block-001", tmp_path) is None


def test_locate_manifest_finds_real_block():
    p = velocity_inference._locate_manifest("block-137", _ARCH_ROOT)
    assert p is not None and p.name == "block-137-project-state.md"


def test_tier_from_real_manifest_reads_M():
    p = velocity_inference._locate_manifest("block-137", _ARCH_ROOT)
    assert velocity_inference._tier_from_manifest(p) == "M"


# ---------------------------------------------------------------------------
# infer_duration
# ---------------------------------------------------------------------------

def test_infer_duration_unknown_block_falls_back_to_estimated():
    hours, source = velocity_inference.infer_duration(
        "block-does-not-exist", _ARCH_ROOT
    )
    assert source == "estimated"
    assert hours == velocity_inference.TIER_ESTIMATES["M"]


def test_infer_duration_real_block_returns_value():
    hours, source = velocity_inference.infer_duration("block-137", _ARCH_ROOT)
    assert source in ("auto-inferred", "estimated")
    assert hours > 0
