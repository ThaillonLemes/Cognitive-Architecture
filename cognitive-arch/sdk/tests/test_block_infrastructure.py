# sdk/tests/test_block_infrastructure.py
# PURPOSE: Validate dual-mode block infrastructure (block-164):
#          size+importance in manifests, wip_stage progression for corporate,
#          paused status, and CorporateGates.
# BLOCK:   block-164

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


# ---------------------------------------------------------------------------
# block_start: reads size+importance
# ---------------------------------------------------------------------------

def test_block_start_reads_v2_manifest():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "STATE.md").write_text("# STATE — AI-only\n\np:29 status:active\n", encoding="utf-8")
        (root / "NEXT.md").write_text("# NEXT — AI-only\n\nnext_action:block-999\n", encoding="utf-8")
        (root / "board.md").write_text(
            "agent:implementer b:- group:- status:idle lock:ready deps:- ts:2026-06-01\n",
            encoding="utf-8",
        )
        (root / "blocks").mkdir()
        (root / "blocks" / "BLOCK_LOG.md").write_text("", encoding="utf-8")
        (root / "manifests").mkdir()
        manifest = root / "manifests" / "block-999-test.md"
        manifest.write_text(
            "---\nid: block-999\nsize: S\nimportance: normal\nkind: implementation\n"
            "phase: phase-99\nstatus: pending\ndependencies: []\n"
            "files:\n  read: []\n  modify: []\n  create: []\ngates: []\n---\n# Test\n",
            encoding="utf-8",
        )

        from block_start import _read_manifest
        data = _read_manifest(manifest)
        assert data.get("size") == "S"
        assert data.get("importance") == "normal"
        assert data.get("kind") == "implementation"


# ---------------------------------------------------------------------------
# block_close: wip_stage_reached for corporate tickets
# ---------------------------------------------------------------------------

def _make_temp_arch(tmp: str) -> Path:
    root = Path(tmp)
    (root / "STATE.md").write_text("# STATE — AI-only\n\np:99 status:active\n", encoding="utf-8")
    (root / "NEXT.md").write_text("# NEXT — AI-only\n\nnext_action:-\n", encoding="utf-8")
    (root / "board.md").write_text(
        "agent:implementer b:999 group:- status:wip lock:in-progress deps:- ts:2026-06-01\n",
        encoding="utf-8",
    )
    (root / "blocks").mkdir()
    (root / "blocks" / "BLOCK_LOG.md").write_text("", encoding="utf-8")
    (root / "manifests").mkdir()
    (root / "phases").mkdir()
    (root / "phases" / "phase-99.md").write_text(
        "---\nid: phase-99\nmode: corporate\n---\n# Test\n", encoding="utf-8"
    )
    (root / "manifests" / "block-999-ticket.md").write_text(
        "---\nid: block-999\nsize: S\nimportance: normal\nkind: ticket\n"
        "phase: phase-99\nstatus: wip\nclient_id: acme\ndependencies: []\n"
        "files:\n  read: []\n  modify: []\n  create: []\ngates: []\n---\n",
        encoding="utf-8",
    )
    return root


def test_close_corporate_ticket_blocks_without_teaching():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_temp_arch(tmp)
        # Retro WITHOUT wip_stage_reached: teaching
        (root / "blocks" / "block-999-ticket.md").write_text(
            "---\nid: block-999\nstatus: done\nwip_stage_reached: quality\n"
            "tok_actual: 100\nactual_duration_hours: 1.0\n---\n",
            encoding="utf-8",
        )

        from block_close import close_block
        result = close_block(root, "block-999", force=False)
        assert result.get("halted") is True or result.get("wip_stage_check") == "failed"


def test_close_corporate_ticket_passes_with_teaching():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_temp_arch(tmp)
        (root / "blocks" / "block-999-ticket.md").write_text(
            "---\nid: block-999\nstatus: done\nwip_stage_reached: teaching\n"
            "tok_actual: 100\nactual_duration_hours: 1.0\n---\n",
            encoding="utf-8",
        )

        from block_close import close_block
        result = close_block(root, "block-999", force=False)
        assert result.get("halted") is not True


def test_close_mmorpg_block_skips_wip_check():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_temp_arch(tmp)
        # Change phase mode to mmorpg
        (root / "phases" / "phase-99.md").write_text(
            "---\nid: phase-99\nmode: mmorpg\n---\n# Test\n", encoding="utf-8"
        )
        (root / "blocks" / "block-999-ticket.md").write_text(
            "---\nid: block-999\nstatus: done\nwip_stage_reached: implementing\n"
            "tok_actual: 100\nactual_duration_hours: 1.0\n---\n",
            encoding="utf-8",
        )

        from block_close import close_block
        result = close_block(root, "block-999", force=False)
        assert result.get("halted") is not True


# ---------------------------------------------------------------------------
# pause_block
# ---------------------------------------------------------------------------

def test_pause_block():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "STATE.md").write_text("# STATE — AI-only\n\np:29 status:active\n", encoding="utf-8")
        (root / "NEXT.md").write_text("# NEXT — AI-only\n\nnext_action:block-999\n", encoding="utf-8")
        (root / "manifests").mkdir()
        (root / "manifests" / "block-999-t.md").write_text(
            "---\nid: block-999\nsize: S\nimportance: normal\nkind: ticket\n"
            "paused_reason: ~\nstatus: wip\n---\n",
            encoding="utf-8",
        )

        from block_close import pause_block
        from state_manager import read_state
        pause_block(root, "block-999", reason="reuniao-inesperada")

        state = read_state(root)
        assert state.get("wip_stage") == "paused"


# ---------------------------------------------------------------------------
# CorporateGates
# ---------------------------------------------------------------------------

def test_corporate_gates_no_checker():
    from gates import CorporateGates
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "manifests").mkdir()
        cg = CorporateGates(root)
        results = cg.check_all("block-999", client_id="acme")
        assert len(results) == 3
        names = {r.name for r in results}
        assert {"functionality-check", "consistency-check", "teach-ready"} == names
        # Without checker present, consistency should warn but pass
        for r in results:
            if r.name == "consistency-check":
                assert r.ok is True  # passes gracefully


def test_gate_files_updated():
    from gates import gate_files_updated
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        block_id = "block-999"
        (root / "STATE.md").write_text(f"# STATE\n\nstatus:active last_block:{block_id}\n", encoding="utf-8")
        (root / "NEXT.md").write_text(f"# NEXT\n\nnext_action:{block_id}\n", encoding="utf-8")
        (root / "blocks").mkdir()
        (root / "blocks" / "BLOCK_LOG.md").write_text(f"{block_id} done - 2026-06-01\n", encoding="utf-8")
        result = gate_files_updated(root, block_id)
        assert result.ok is True


if __name__ == "__main__":
    test_block_start_reads_v2_manifest()
    test_close_corporate_ticket_blocks_without_teaching()
    test_close_corporate_ticket_passes_with_teaching()
    test_close_mmorpg_block_skips_wip_check()
    test_pause_block()
    test_corporate_gates_no_checker()
    test_gate_files_updated()
    print("All block-164 tests passed.")
