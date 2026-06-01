# sdk/tests/test_scanner_deep.py
# PURPOSE: Validate deep scan levels L2, L3, L4 and proof-of-reasoning.
# BLOCK:   block-167

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


def _make_repo(tmp: str, style: str = "fsd") -> Path:
    """Create fixture repo with known architecture patterns."""
    repo = Path(tmp) / "repo"
    repo.mkdir()
    src = repo / "src"
    src.mkdir()

    if style == "fsd":
        for d in ("features", "entities", "shared", "widgets"):
            (src / d).mkdir()
            (src / d / "index.ts").write_text(
                f'import {{ something }} from "./utils";\nexport const {d}Module = true;\n',
                encoding="utf-8",
            )
    elif style == "mvc":
        for d in ("models", "views", "controllers"):
            (src / d).mkdir()
            (src / d / "index.py").write_text(
                f"class {d.capitalize()}Base:\n    pass\n", encoding="utf-8"
            )

    (repo / "package.json").write_text(
        '{"name":"test","dependencies":{"react":"18.0.0"},"devDependencies":{"typescript":"5.0.0"}}',
        encoding="utf-8",
    )
    return repo


def _make_arch(tmp: str) -> Path:
    arch = Path(tmp) / "arch"
    (arch / "governance").mkdir(parents=True)
    (arch / "sdk").mkdir()
    (arch / "STATE.md").write_text("# STATE\n\np:30 status:active\n", encoding="utf-8")
    (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")
    return arch


# ---------------------------------------------------------------------------
# L2 tests
# ---------------------------------------------------------------------------

def test_l2_detects_fsd():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, "fsd")
        arch = _make_arch(tmp)
        from scanner_deep import scan_deep
        result = scan_deep(repo, "L2", arch, "fixture")
        assert "Feature-Sliced" in result.get("architecture", "")


def test_l2_includes_proof():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, "fsd")
        arch = _make_arch(tmp)
        from scanner_deep import scan_deep
        result = scan_deep(repo, "L2", arch, "fixture")
        assert "L2" in result.get("proofs", {})
        assert len(result["proofs"]["L2"]) > 0


def test_l2_profile_has_section():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, "mvc")
        arch = _make_arch(tmp)
        from scanner_deep import scan_deep
        from scanner_profile import ProjectProfile
        scan_deep(repo, "L2", arch, "fixture")
        p = ProjectProfile(arch, "fixture")
        assert p.has_section("L2")
        section = p.get_section("L2")
        assert "padrão" in section


# ---------------------------------------------------------------------------
# L3 tests
# ---------------------------------------------------------------------------

def test_l3_detects_naming():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, "fsd")
        arch = _make_arch(tmp)
        from scanner_deep import scan_deep
        result = scan_deep(repo, "L3", arch, "fixture")
        assert "naming" in result
        assert isinstance(result["naming"], dict)


def test_l3_profile_has_section():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, "fsd")
        arch = _make_arch(tmp)
        from scanner_deep import scan_deep
        from scanner_profile import ProjectProfile
        scan_deep(repo, "L3", arch, "fixture")
        p = ProjectProfile(arch, "fixture")
        assert p.has_section("L3")


# ---------------------------------------------------------------------------
# L4 tests
# ---------------------------------------------------------------------------

def test_l4_profile_has_section():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, "fsd")
        arch = _make_arch(tmp)
        from scanner_deep import scan_deep
        from scanner_profile import ProjectProfile
        scan_deep(repo, "L2+L3+L4", arch, "fixture")
        p = ProjectProfile(arch, "fixture")
        assert p.has_section("L4")
        section = p.get_section("L4")
        assert "vigente" in section


def test_l4_does_not_store_code():
    """L4 result must not contain actual code snippets."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, "fsd")
        # Add some code that should not appear in profile
        (repo / "src" / "features" / "auth.ts").write_text(
            "export function login(pw: string) { return hash(pw) * 99; }\n",
            encoding="utf-8",
        )
        arch = _make_arch(tmp)
        from scanner_deep import scan_deep
        from scanner_profile import ProjectProfile
        scan_deep(repo, "L4", arch, "fixture")
        p = ProjectProfile(arch, "fixture")
        text = p.get_section("L4")
        assert "hash(pw)" not in text
        assert "return hash" not in text


def test_l4_coexistence_no_absolute_paths():
    """L4 vigente/legado must contain only repo-internal dir names (no drive letters or user paths)."""
    import os
    import re
    import time

    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp, "fsd")
        arch = _make_arch(tmp)

        # Create a "legacy" subdir and stamp it 1 year in the past so the
        # recency split puts it firmly in the "old" bucket.
        legacy_dir = repo / "src" / "legacy_module"
        legacy_dir.mkdir()
        legacy_file = legacy_dir / "old.py"
        legacy_file.write_text("x = 1\n", encoding="utf-8")
        old_time = time.time() - 86400 * 365
        os.utime(legacy_file, (old_time, old_time))

        from scanner_deep import scan_deep
        result = scan_deep(repo, "L4", arch, "fixture")

        coex = result["l4_coexistence"]
        for key in ("vigente", "legado"):
            val = coex[key]
            # Must not contain Windows drive letters (e.g. "C:/" or "C:\")
            assert not re.search(r"[A-Za-z]:[/\\]", val), \
                f"{key} contains drive letter: {val!r}"
            # Must not contain OS-level user-path components
            assert "Users" not in val, f"{key} contains 'Users': {val!r}"
            # Each individual segment must be a short name with no path separators
            for segment in val.split(", "):
                name = segment.rstrip("/")
                if name in ("padrão atual (homogêneo)", "nenhum legado detectado"):
                    continue
                assert len(name) < 50, f"{key} segment too long: {name!r}"
                assert "\\" not in name and "/" not in name, \
                    f"{key} segment contains path separator: {name!r}"


if __name__ == "__main__":
    test_l2_detects_fsd()
    test_l2_includes_proof()
    test_l2_profile_has_section()
    test_l3_detects_naming()
    test_l3_profile_has_section()
    test_l4_profile_has_section()
    test_l4_does_not_store_code()
    print("All block-167 tests passed.")
