# PURPOSE: Smoke-test every sdk CLI as the user runs it (python sdk/foo.py) under cp1252.
#          Catches crash-on-run bugs that unit tests miss (e.g. UnicodeEncodeError on stdout).
# INPUTS:  sdk/*.py tools; a throwaway copy of cognitive-arch-generic as fixture
# OUTPUTS: pass/fail per tool; xfail for known crashers (velocity --help; block-138)
# DEPS:    pytest, subprocess, shutil
# SEE:     phases/phase-23.md block-135, sdk/recommendation_engine.py, sdk/velocity_inference.py

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_SDK = Path(__file__).resolve().parent.parent          # cognitive-arch/sdk
_ARCH = _SDK.parent                                     # cognitive-arch
_GENERIC = _ARCH.parent / "cognitive-arch-generic"     # sibling scaffold (fixture source)

_SKIP = {"__init__.py", "conftest.py"}

# No known crashers. block-136 fixed UTF-8 crashers; block-138 added argparse
# to velocity_inference and guarded the empty-manifest Path("") path.
_KNOWN_CRASHERS: set[str] = set()


def _tools() -> list[Path]:
    return sorted(
        p for p in _SDK.glob("*.py")
        if p.name not in _SKIP and not p.name.endswith("_schema.py")
    )


def _run(args: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a python command under cp1252 (the user's Windows console worst-case)."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1252"
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=timeout, cwd=str(cwd),
    )


def _params():
    out = []
    for p in _tools():
        marks = (
            [pytest.mark.xfail(reason="velocity --help reads '.'; block-138 fixes", strict=True)]
            if p.name in _KNOWN_CRASHERS else []
        )
        out.append(pytest.param(p, marks=marks, id=p.name))
    return out


# ---------------------------------------------------------------------------
# --help must never crash (catches import/encoding bugs in every tool)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool", _params())
def test_help_no_crash(tool: Path):
    r = _run([str(tool), "--help"], cwd=_ARCH)
    combined = r.stdout + r.stderr
    assert "Traceback" not in combined, f"{tool.name} --help crashed:\n{combined}"
    assert r.returncode == 0, f"{tool.name} --help exited {r.returncode}:\n{combined}"


# ---------------------------------------------------------------------------
# Curated real-runs of read-only generators against a throwaway fixture
# ---------------------------------------------------------------------------

_REAL_RUNS = [
    ("health_report.py", ["--arch-root", "{fix}"]),
    ("dashboard_generator.py", ["--arch-root", "{fix}"]),
    ("patterns_report.py", ["--arch-root", "{fix}"]),
    ("weekly_report.py", ["--arch-root", "{fix}"]),
    ("integrity_check.py", ["--verify", "--arch-root", "{fix}"]),
    ("audit.py", ["--arch-root", "{fix}"]),
]


@pytest.fixture(scope="module")
def fixture_arch(tmp_path_factory) -> Path:
    """A throwaway copy of the generic scaffold to run write-capable tools against."""
    if not _GENERIC.exists():
        pytest.skip("cognitive-arch-generic sibling not found")
    dest = tmp_path_factory.mktemp("arch_fix")
    target = dest / "arch"
    shutil.copytree(_GENERIC, target)
    return target


@pytest.mark.parametrize("name,args", _REAL_RUNS, ids=[n for n, _ in _REAL_RUNS])
def test_real_run_no_crash(name: str, args: list[str], fixture_arch: Path):
    tool = _SDK / name
    if not tool.exists():
        pytest.skip(f"{name} not present")
    resolved = [a.replace("{fix}", str(fixture_arch)) for a in args]
    r = _run([str(tool), *resolved], cwd=_ARCH)
    combined = r.stdout + r.stderr
    assert "Traceback" not in combined, f"{name} crashed on real run:\n{combined}"
