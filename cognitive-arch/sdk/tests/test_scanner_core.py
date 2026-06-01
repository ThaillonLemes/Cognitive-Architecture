# sdk/tests/test_scanner_core.py
# PURPOSE: Validate scanner core: CLI, L0+L1 scan, ProjectProfile, multi-client.
# BLOCK:   block-166

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


# ---------------------------------------------------------------------------
# Fixture builder
# ---------------------------------------------------------------------------

def _make_repo(tmp_dir: str) -> Path:
    """Create a minimal TypeScript/React fixture repo."""
    repo = Path(tmp_dir) / "fixture-repo"
    repo.mkdir()
    (repo / "package.json").write_text(
        '{"name":"fixture","dependencies":{"next":"14.0.0","react":"18.0.0"},'
        '"devDependencies":{"typescript":"5.0.0"}}',
        encoding="utf-8",
    )
    (repo / ".gitignore").write_text("node_modules/\ndist/\n.next/\n", encoding="utf-8")
    src = repo / "src"
    src.mkdir()
    (src / "index.ts").write_text("export default function app() {}\n", encoding="utf-8")
    models = src / "models"
    models.mkdir()
    (models / "User.ts").write_text("export class User { id: string; name: string; }\n", encoding="utf-8")
    (models / "Order.ts").write_text("export class Order { id: string; total: number; }\n", encoding="utf-8")
    return repo


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_cli_help():
    from codebase_scanner import build_parser
    p = build_parser()
    assert p is not None
    # Should have --target-repo, --level, --client, --no-html flags
    actions = {a.dest for a in p._actions}
    assert "target_repo" in actions
    assert "level" in actions
    assert "client" in actions
    assert "no_html" in actions


# ---------------------------------------------------------------------------
# L0 + L1 scan
# ---------------------------------------------------------------------------

def test_scan_l0_creates_profile():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp)
        arch = Path(tmp) / "arch"
        (arch / "governance").mkdir(parents=True)
        (arch / "sdk").mkdir()
        (arch / "STATE.md").write_text("# STATE\n\np:30 status:active\n", encoding="utf-8")
        (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")

        from codebase_scanner import run_scan
        result = run_scan(repo, "L0", arch, "fixture", no_html=True)

        profile_path = Path(result["profile_path"])
        assert profile_path.exists()

        text = profile_path.read_text(encoding="utf-8")
        assert "L0" in text
        assert "L1" in text


def test_l0_detects_typescript():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp)
        arch = Path(tmp) / "arch"
        (arch / "governance").mkdir(parents=True)
        (arch / "sdk").mkdir()
        (arch / "STATE.md").write_text("# STATE\n\np:30 status:active\n", encoding="utf-8")
        (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")

        from codebase_scanner import scan_l0
        result = scan_l0(repo)
        assert result["stack"].get("lang") in ("TypeScript", "JavaScript", "TypeScript/React")


def test_profile_no_code_snippets():
    """Profile must never contain actual client code."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp)
        # Add code content that should NOT appear in profile
        (repo / "src" / "secret_logic.ts").write_text(
            "export function secretAlgorithm(x: number) { return x * 42; }\n",
            encoding="utf-8",
        )
        arch = Path(tmp) / "arch"
        (arch / "governance").mkdir(parents=True)
        (arch / "sdk").mkdir()
        (arch / "STATE.md").write_text("# STATE\n\np:30 status:active\n", encoding="utf-8")
        (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")

        from codebase_scanner import run_scan
        run_scan(repo, "L0", arch, "fixture", no_html=True)

        profile = arch / "governance" / "project-profile-fixture.md"
        text = profile.read_text(encoding="utf-8")
        # Should NOT contain function bodies or raw code
        assert "return x * 42" not in text
        assert "secretAlgorithm" not in text  # function name ok to exclude


# ---------------------------------------------------------------------------
# ProjectProfile
# ---------------------------------------------------------------------------

def test_project_profile_set_get_section():
    with tempfile.TemporaryDirectory() as tmp:
        arch = Path(tmp)
        (arch / "governance").mkdir()
        from scanner_profile import ProjectProfile
        p = ProjectProfile(arch, "testclient")
        p.set_section("L0", ["tipo: web", "stack: Next.js"])
        p.save()

        p2 = ProjectProfile(arch, "testclient")
        section = p2.get_section("L0")
        assert "tipo: web" in section
        assert "Next.js" in section


def test_project_profile_multi_client():
    with tempfile.TemporaryDirectory() as tmp:
        arch = Path(tmp)
        (arch / "governance").mkdir()
        from scanner_profile import ProjectProfile

        pa = ProjectProfile(arch, "clientA")
        pa.set_section("L0", ["tipo: api"])
        pa.save()

        pb = ProjectProfile(arch, "clientB")
        pb.set_section("L0", ["tipo: web"])
        pb.save()

        clients = ProjectProfile.list_clients(arch)
        assert "clientA" in clients
        assert "clientB" in clients

        # Ensure no cross-contamination
        pa2 = ProjectProfile(arch, "clientA")
        assert "api" in pa2.get_section("L0")
        assert "web" not in pa2.get_section("L0")


def test_no_html_flag():
    """--no-html must suppress HTML generation."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp)
        arch = Path(tmp) / "arch"
        (arch / "governance").mkdir(parents=True)
        (arch / "sdk").mkdir()
        (arch / "STATE.md").write_text("# STATE\n\np:30 status:active\n", encoding="utf-8")
        (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")

        from codebase_scanner import run_scan
        result = run_scan(repo, "L0", arch, "fixture", no_html=True)

        # No HTML should have been created
        html_files = list((arch / "governance").glob("scanner-output-*.html"))
        assert len(html_files) == 0
        assert "html_path" not in result


if __name__ == "__main__":
    test_cli_help()
    test_scan_l0_creates_profile()
    test_l0_detects_typescript()
    test_profile_no_code_snippets()
    test_project_profile_set_get_section()
    test_project_profile_multi_client()
    test_no_html_flag()
    print("All block-166 tests passed.")
