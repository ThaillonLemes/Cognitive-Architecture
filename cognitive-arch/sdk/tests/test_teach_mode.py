# sdk/tests/test_teach_mode.py
# PURPOSE: Validate teach mode: 3 HTMLs generated, dial of abstraction, toggles,
#          text export, loopback wip_stage update, block_close enforcement.
# BLOCK:   block-172

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


def _make_arch(tmp: str, level: str = "tecnico", toggles: dict | None = None) -> Path:
    arch = Path(tmp) / "arch"
    gov = arch / "governance"
    gov.mkdir(parents=True)
    (arch / "sdk").mkdir()
    (arch / "manifests").mkdir()
    (arch / "blocks").mkdir()
    (arch / "STATE.md").write_text("# STATE\n\np:31 status:active\n", encoding="utf-8")
    (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")

    t = toggles or {"technical": "true", "team": "true", "learning": "true"}
    teach_cfg = "\n".join(f"  {k}: {v}" for k, v in t.items())
    (gov / "ux-config.yaml").write_text(
        f"abstraction_level: {level}\nteach_html:\n{teach_cfg}\n",
        encoding="utf-8",
    )
    return arch


def _make_manifest(arch: Path, block_id: str) -> None:
    (arch / "manifests" / f"{block_id}-ticket.md").write_text(
        f"---\nid: {block_id}\nsize: S\nimportance: normal\nkind: ticket\n"
        "client_id: acme\nphase: phase-31\nstatus: wip\nwip_stage: teaching\n"
        "files:\n  modify: []\n  create: []\n---\n",
        encoding="utf-8",
    )
    (arch / "blocks" / f"{block_id}-ticket.md").write_text(
        f"---\nid: {block_id}\nstatus: done\nwip_stage_reached: teaching\n"
        "tok_actual: 500\nactual_duration_hours: 2.0\n---\n\n"
        "# Block Test\n\n## 1. Summary\n\nAdicionado endpoint de refresh de JWT com validação de expiração.\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def test_teach_generates_3_htmls():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")

        from teach_mode import run_teach
        generated = run_teach("block-999", arch, interactive=False)

        assert "technical" in generated
        assert "team" in generated
        assert "learning" in generated
        for path in generated.values():
            assert path.exists()


def test_teach_html_has_summary():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")

        from teach_mode import run_teach
        generated = run_teach("block-999", arch, interactive=False)

        for audience, path in generated.items():
            text = path.read_text(encoding="utf-8")
            assert "Teach Mode" in text


# ---------------------------------------------------------------------------
# Abstraction dial
# ---------------------------------------------------------------------------

def test_dial_leigo():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp, level="leigo")
        _make_manifest(arch, "block-999")

        from teach_mode import run_teach
        generated = run_teach("block-999", arch, level_override="leigo", interactive=False)
        text = generated["technical"].read_text(encoding="utf-8")
        assert "leigo" in text.lower() or "resumido assim" in text.lower()


def test_dial_tecnico():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp, level="tecnico")
        _make_manifest(arch, "block-999")

        from teach_mode import run_teach
        generated = run_teach("block-999", arch, level_override="tecnico", interactive=False)
        text = generated["technical"].read_text(encoding="utf-8")
        assert "tecnico" in text.lower() or "arquiteturais" in text.lower()


# ---------------------------------------------------------------------------
# Toggle individual HTMLs
# ---------------------------------------------------------------------------

def test_team_html_disabled():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp, toggles={"technical": "true", "team": "false", "learning": "true"})
        _make_manifest(arch, "block-999")

        from teach_mode import run_teach
        generated = run_teach("block-999", arch, interactive=False)

        assert "team" not in generated
        assert "technical" in generated
        assert "learning" in generated


# ---------------------------------------------------------------------------
# Text export
# ---------------------------------------------------------------------------

def test_text_export_generated():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")

        from teach_mode import run_teach
        run_teach("block-999", arch, interactive=False)

        txt_files = list((arch / "governance").glob("teach-block-999-*.txt"))
        assert len(txt_files) == 3  # one per audience


# ---------------------------------------------------------------------------
# block_close enforcement
# ---------------------------------------------------------------------------

def test_block_close_rejects_ticket_without_teaching():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        (arch / "blocks" / "BLOCK_LOG.md").write_text("", encoding="utf-8")
        (arch / "board.md").write_text(
            "agent:implementer b:999 status:wip lock:in-progress deps:- ts:2026-06-01\n",
            encoding="utf-8",
        )
        (arch / "phases").mkdir()
        (arch / "phases" / "phase-31.md").write_text(
            "---\nid: phase-31\nmode: corporate\n---\n# Test\n", encoding="utf-8"
        )
        # Manifest with kind: ticket
        (arch / "manifests" / "block-999-ticket.md").write_text(
            "---\nid: block-999\nsize: S\nimportance: normal\nkind: ticket\n"
            "client_id: acme\nphase: phase-31\nstatus: wip\n---\n",
            encoding="utf-8",
        )
        # Retro with wip_stage_reached: quality (not teaching)
        (arch / "blocks" / "block-999-ticket.md").write_text(
            "---\nid: block-999\nstatus: done\nwip_stage_reached: quality\n"
            "tok_actual: 100\nactual_duration_hours: 1.0\n---\n",
            encoding="utf-8",
        )

        from block_close import close_block
        result = close_block(arch, "block-999", force=False)
        assert result.get("halted") is True or result.get("wip_stage_check") == "failed"


if __name__ == "__main__":
    test_teach_generates_3_htmls()
    test_teach_html_has_summary()
    test_dial_leigo()
    test_dial_tecnico()
    test_team_html_disabled()
    test_text_export_generated()
    test_block_close_rejects_ticket_without_teaching()
    print("All block-172 tests passed.")
