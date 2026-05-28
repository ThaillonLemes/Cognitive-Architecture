# PURPOSE: Shared pytest fixtures for Governor v2 SDK test suite
# INPUTS:  pytest session / function scope
# OUTPUTS: arch_root path, tmp_arch isolated temp directory, sample manifest
# DEPS:    pytest, pathlib, shutil, tempfile
# SEE:     phases/phase-7.md, sdk/governor.py (ARCH_ROOT definition)

import sys
import shutil
import tempfile
from pathlib import Path

import pytest

# Ensure sdk/ is importable from test files
_SDK_DIR = Path(__file__).resolve().parent.parent   # cognitive-arch/sdk/
_ARCH_ROOT = _SDK_DIR.parent                         # cognitive-arch/

if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def arch_root() -> Path:
    """The real cognitive-arch root directory (read-only in tests)."""
    return _ARCH_ROOT


@pytest.fixture
def tmp_arch(tmp_path: Path) -> Path:
    """
    An isolated temporary copy of the minimal arch state files.
    Modifying this directory does NOT affect the real cognitive-arch.
    """
    # Copy essential state files
    for fname in ["STATE.md", "NEXT.md", "board.md"]:
        src = _ARCH_ROOT / fname
        if src.exists():
            shutil.copy(src, tmp_path / fname)

    # Create blocks/ with BLOCK_LOG
    (tmp_path / "blocks").mkdir(exist_ok=True)
    block_log_src = _ARCH_ROOT / "blocks" / "BLOCK_LOG.md"
    if block_log_src.exists():
        shutil.copy(block_log_src, tmp_path / "blocks" / "BLOCK_LOG.md")

    return tmp_path


@pytest.fixture
def sample_manifest_path(tmp_path: Path) -> Path:
    """A minimal valid Tier S manifest written to a temp file."""
    manifest = tmp_path / "manifests"
    manifest.mkdir(exist_ok=True)
    m = manifest / "block-999-sample.md"
    m.write_text(
        "---\n"
        "id: block-999\n"
        "tier: S\n"
        "kind: doc-only\n"
        "phase: phase-7\n"
        "status: planned\n"
        "files:\n"
        "  read:\n"
        "    - STATE.md\n"
        "  modify: []\n"
        "  create: []\n"
        "gates:\n"
        "  - name: files-updated\n"
        "    type: file-changed\n"
        "    paths: [STATE.md]\n"
        "created_at: 2026-05-22\n"
        "---\n\n"
        "# Block 999 — Sample\n\n"
        "## 1. Purpose\n\nSample block for testing.\n",
        encoding="utf-8",
    )
    return m


@pytest.fixture
def sample_manifest_rel(sample_manifest_path: Path, tmp_path: Path) -> str:
    """Relative path string for sample_manifest_path within tmp_path."""
    return str(sample_manifest_path.relative_to(tmp_path))
