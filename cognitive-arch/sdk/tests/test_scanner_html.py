# sdk/tests/test_scanner_html.py
# PURPOSE: Validate HTML dossier generation: sections present, Mermaid included,
#          no-html flag, ux-config toggle, cost footer.
# BLOCK:   block-168

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


def _make_arch(tmp: str) -> Path:
    arch = Path(tmp) / "arch"
    (arch / "governance").mkdir(parents=True)
    (arch / "sdk").mkdir()
    return arch


def _make_profile_and_result(arch: Path, client: str = "testclient") -> tuple:
    from scanner_profile import ProjectProfile
    p = ProjectProfile(arch, client)
    p.set_section("L0", ["tipo: web", "stack: Next.js · lang: TypeScript", "entidades: User, Order"])
    p.set_section("L1", ["linguagens: TypeScript (88%)", "arquivos: 120"])
    p.save()

    result = {
        "level": "L0",
        "client": client,
        "tokens_used": 1500,
        "usd_estimate": 0.0045,
        "l0": {
            "sys_type": "web-fullstack",
            "stack": {"framework": "Next.js 14", "lang": "TypeScript", "ci": "GitHub Actions"},
            "deps": ["next@14.0.0", "react@18.0.0", "zod@3.0.0"],
            "tree": ["src/", "  components/  [UI components]", "  pages/  [pages/routes]",
                     "  api/  [API handlers]"],
            "domain_entities": ["User", "Order", "Payment"],
            "domain_flows": [],
            "file_count": 120,
        },
        "l1": {
            "languages": {"TypeScript": 88.0, "CSS": 8.0},
            "entry_points": ["src/app/page.tsx"],
            "deps": ["next@14.0.0"],
            "file_count": 120,
        },
    }
    return p, result


def test_html_generates_file():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        p, result = _make_profile_and_result(arch)

        from scanner_html import generate_html
        html_path = generate_html(p, result, arch, "20260601-1000")
        assert html_path.exists()
        assert html_path.suffix == ".html"
        assert "testclient" in html_path.name


def test_html_has_required_sections():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        p, result = _make_profile_and_result(arch)

        from scanner_html import generate_html
        html_path = generate_html(p, result, arch, "20260601-1001")
        text = html_path.read_text(encoding="utf-8")

        # Required sections per design/scanner.md §3
        assert "Mapa Arquitetural" in text
        assert "Grafo de Depend" in text
        assert "Stack" in text or "stack" in text.lower()
        assert "tokens" in text.lower()


def test_html_contains_mermaid():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        p, result = _make_profile_and_result(arch)

        from scanner_html import generate_html
        html_path = generate_html(p, result, arch, "20260601-1002")
        text = html_path.read_text(encoding="utf-8")
        assert "mermaid" in text.lower()
        assert "graph" in text


def test_html_cost_footer():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        p, result = _make_profile_and_result(arch)

        from scanner_html import generate_html
        html_path = generate_html(p, result, arch, "20260601-1003")
        text = html_path.read_text(encoding="utf-8")
        assert "Tokens" in text or "tokens" in text.lower()
        assert "USD" in text or "usd" in text.lower()


def test_html_no_client_code():
    """HTML must not contain raw client code."""
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        p, result = _make_profile_and_result(arch)

        from scanner_html import generate_html
        html_path = generate_html(p, result, arch, "20260601-1004")
        text = html_path.read_text(encoding="utf-8")
        assert "return hash(pw)" not in text
        assert "secretAlgorithm" not in text


def test_html_no_html_flag_via_run_scan():
    """run_scan with no_html=True must not produce HTML."""
    import os
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        (repo / "package.json").write_text('{"dependencies":{"react":"18.0.0"}}', encoding="utf-8")
        arch = _make_arch(tmp)
        (arch / "STATE.md").write_text("# STATE\n\np:30 status:active\n", encoding="utf-8")
        (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")

        from codebase_scanner import run_scan
        run_scan(repo, "L0", arch, "fixture", no_html=True)

        html_files = list((arch / "governance").glob("scanner-output-*.html"))
        assert len(html_files) == 0


def test_html_ux_config_toggle():
    """scanner_html_output: false in ux-config must suppress HTML."""
    import os
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        (repo / "package.json").write_text('{"dependencies":{"react":"18.0.0"}}', encoding="utf-8")
        arch = _make_arch(tmp)
        (arch / "STATE.md").write_text("# STATE\n\np:30 status:active\n", encoding="utf-8")
        (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")
        # Write ux-config with html disabled
        (arch / "governance" / "ux-config.yaml").write_text(
            "scanner_html_output: false\n", encoding="utf-8"
        )

        from codebase_scanner import run_scan
        run_scan(repo, "L0", arch, "fixture2")

        html_files = list((arch / "governance").glob("scanner-output-*.html"))
        assert len(html_files) == 0


if __name__ == "__main__":
    test_html_generates_file()
    test_html_has_required_sections()
    test_html_contains_mermaid()
    test_html_cost_footer()
    test_html_no_client_code()
    test_html_no_html_flag_via_run_scan()
    test_html_ux_config_toggle()
    print("All block-168 tests passed.")
