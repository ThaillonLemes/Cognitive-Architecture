# sdk/tests/test_ticket_intake.py
# PURPOSE: Validate ticket_intake.py: manifest generation, kind, required fields.
# BLOCK:   block-165

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


def _make_root(tmp: str, blocks: list[str] | None = None) -> Path:
    root = Path(tmp)
    (root / "STATE.md").write_text(
        "# STATE — AI-only\n\np:29 status:active phase:phase-29\n", encoding="utf-8"
    )
    (root / "NEXT.md").write_text("# NEXT — AI-only\n\nnext_action:-\n", encoding="utf-8")
    (root / "blocks").mkdir()
    log_content = "\n".join(f"{b} done - 2026-06-01" for b in (blocks or []))
    (root / "blocks" / "BLOCK_LOG.md").write_text(log_content, encoding="utf-8")
    (root / "manifests").mkdir()
    return root


def test_generate_manifest_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_root(tmp)
        from ticket_intake import generate_manifest
        out = generate_manifest("implementar refresh de JWT", "visagio", root)
        assert out.exists()
        text = out.read_text(encoding="utf-8")
        assert "kind: intake" in text
        assert "client_id: visagio" in text
        assert "size: XS" in text


def test_intake_never_modifies_client_code():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_root(tmp)
        from ticket_intake import generate_manifest
        out = generate_manifest("adicionar validação de e-mail", "acme", root)
        text = out.read_text(encoding="utf-8")
        # modify section should be empty
        assert "modify: []" in text


def test_acceptance_criteria_extracted():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_root(tmp)
        from ticket_intake import generate_manifest
        ticket = "implementar refresh de JWT. AC: o token deve expirar em 15 minutos."
        out = generate_manifest(ticket, "visagio", root)
        text = out.read_text(encoding="utf-8")
        assert "acceptance_criteria" in text


def test_block_id_does_not_collide():
    with tempfile.TemporaryDirectory() as tmp:
        # Pre-populate BLOCK_LOG with blocks 1–161
        existing = [f"block-{i}" for i in range(1, 162)]
        root = _make_root(tmp, blocks=existing)
        from ticket_intake import generate_manifest
        out = generate_manifest("ticket qualquer", "visagio", root)
        text = out.read_text(encoding="utf-8")
        # block id should be >= 162
        m = re.search(r"^id: block-(\d+)", text, re.MULTILINE)
        assert m and int(m.group(1)) >= 162


def test_acceptance_criteria_needs_review_flag():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_root(tmp)
        from ticket_intake import generate_manifest
        out = generate_manifest("fix crash on login", "acme", root)
        text = out.read_text(encoding="utf-8")
        # Without explicit AC, should have NEEDS_REVIEW
        assert "NEEDS_REVIEW" in text


def test_cli_smoke():
    """CLI must run without crash and create a manifest."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_root(tmp)
        import io, contextlib
        from ticket_intake import main
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ret = main(["--ticket", "adicionar paginação", "--client", "visagio",
                        "--arch-root", str(root)])
        assert ret == 0
        assert "Created" in buf.getvalue()
        manifests = list((root / "manifests").glob("block-*-*.md"))
        assert len(manifests) == 1


if __name__ == "__main__":
    test_generate_manifest_creates_file()
    test_intake_never_modifies_client_code()
    test_acceptance_criteria_extracted()
    test_block_id_does_not_collide()
    test_acceptance_criteria_needs_review_flag()
    test_cli_smoke()
    print("All block-165 tests passed.")
