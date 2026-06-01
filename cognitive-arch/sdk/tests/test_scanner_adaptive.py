# sdk/tests/test_scanner_adaptive.py
# PURPOSE: Validate adaptive mode, ticket inference, and profile management.
# BLOCK:   block-169

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


def _make_repo(tmp: str, n_files: int = 10, dirs: list[str] | None = None) -> Path:
    repo = Path(tmp) / "repo"
    repo.mkdir()
    src = repo / "src"
    src.mkdir()
    for i in range(n_files):
        (src / f"file{i}.ts").write_text(f"export const f{i} = {i};\n", encoding="utf-8")
    for d in (dirs or []):
        (src / d).mkdir(exist_ok=True)
        (src / d / "index.ts").write_text(f"// {d}\n", encoding="utf-8")
    (repo / "package.json").write_text('{"dependencies":{"react":"18"}}', encoding="utf-8")
    return repo


def _make_arch(tmp: str) -> Path:
    arch = Path(tmp) / "arch"
    (arch / "governance").mkdir(parents=True)
    (arch / "sdk").mkdir()
    (arch / "STATE.md").write_text("# STATE\n\np:30 status:active\n", encoding="utf-8")
    (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")
    return arch


# ---------------------------------------------------------------------------
# Adaptive preflight
# ---------------------------------------------------------------------------

def test_small_repo_no_prompt():
    """Repos below threshold must not prompt."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, n_files=5)
        from scanner_adaptive import adaptive_preflight
        result = adaptive_preflight(repo, "L0", interactive=False)
        assert result is True


def test_large_repo_non_interactive_proceeds():
    """Large repos in non-interactive mode proceed automatically."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, n_files=5)
        # Add many files to exceed threshold
        for i in range(300):
            (repo / "src" / f"extra{i}.ts").write_text(f"const x{i} = {i};", encoding="utf-8")

        from scanner_adaptive import adaptive_preflight
        result = adaptive_preflight(repo, "L0", interactive=False)
        assert result is True


# ---------------------------------------------------------------------------
# Ticket inference
# ---------------------------------------------------------------------------

def test_infer_area_jwt():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, dirs=["auth", "user"])
        from scanner_adaptive import infer_area_from_ticket
        area = infer_area_from_ticket("fix JWT refresh bug", repo)
        assert area is not None
        assert "auth" in str(area).lower()


def test_infer_area_payment():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, dirs=["payment", "billing"])
        from scanner_adaptive import infer_area_from_ticket
        area = infer_area_from_ticket("implementar checkout com Stripe", repo)
        assert area is not None
        assert "payment" in str(area).lower() or "billing" in str(area).lower()


def test_infer_area_unknown():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp)
        from scanner_adaptive import infer_area_from_ticket
        area = infer_area_from_ticket("lorem ipsum dolor sit amet", repo)
        # Should return None for unrecognized ticket text
        assert area is None


# ---------------------------------------------------------------------------
# Profile management
# ---------------------------------------------------------------------------

def test_profile_manager_detects_stale():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        from scanner_adaptive import ProfileManager
        pm = ProfileManager(arch)
        # No profile → stale
        assert pm.is_stale("newclient", "L0") is True


def test_profile_manager_list_stale_all_missing():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        from scanner_adaptive import ProfileManager
        pm = ProfileManager(arch)
        stale = pm.list_stale("newclient")
        assert set(stale) == {"L0", "L1", "L2", "L3", "L4"}


def test_refresh_level_updates_section():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp)
        arch = _make_arch(tmp)
        from scanner_adaptive import ProfileManager
        pm = ProfileManager(arch)
        pm.refresh_level("fixture", "L0", repo, no_html=True)

        from scanner_profile import ProjectProfile
        p = ProjectProfile(arch, "fixture")
        assert p.has_section("L0")


if __name__ == "__main__":
    test_small_repo_no_prompt()
    test_large_repo_non_interactive_proceeds()
    test_infer_area_jwt()
    test_infer_area_payment()
    test_infer_area_unknown()
    test_profile_manager_detects_stale()
    test_profile_manager_list_stale_all_missing()
    test_refresh_level_updates_section()
    print("All block-169 tests passed.")
