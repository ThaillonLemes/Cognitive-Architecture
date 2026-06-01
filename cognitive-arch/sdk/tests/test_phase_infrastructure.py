# sdk/tests/test_phase_infrastructure.py
# PURPOSE: Validate dual-mode phase infrastructure (block-163):
#          mode/type/client_id in phase docs, PilotState in state_manager,
#          workday type without doc, session_start mode display.
# BLOCK:   block-163

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # cognitive-arch/
sys.path.insert(0, str(ROOT / "sdk"))


# ---------------------------------------------------------------------------
# state_manager.PilotState
# ---------------------------------------------------------------------------

def test_pilot_state_read_write():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "STATE.md").write_text(
            "# STATE — AI-only\n\np:29 status:active phase:phase-29 mode:corporate "
            "current_client:visagio tickets_open:3 last_scan_at:2026-06-01\n",
            encoding="utf-8",
        )
        (root / "NEXT.md").write_text("# NEXT — AI-only\n\nnext_action:block-162\n", encoding="utf-8")

        from state_manager import PilotState
        ps = PilotState(root)
        assert ps.current_client == "visagio"
        assert ps.tickets_open == 3
        assert ps.last_scan_at == "2026-06-01"


def test_pilot_state_save():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "STATE.md").write_text("# STATE — AI-only\n\np:29 status:active\n", encoding="utf-8")
        (root / "NEXT.md").write_text("# NEXT — AI-only\n\nnext_action:-\n", encoding="utf-8")

        from state_manager import PilotState, read_state
        ps = PilotState(root)
        ps.set_client("acme")
        ps.tickets_open = 5
        ps.add_gap("src/auth")
        ps.save()

        state = read_state(root)
        assert state["current_client"] == "acme"
        assert state["tickets_open"] == "5"
        assert "src/auth" in state["knowledge_gaps"]


# ---------------------------------------------------------------------------
# phase_manager dual-mode read
# ---------------------------------------------------------------------------

def test_phase_meta_reads_mode():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        phases_dir = root / "phases"
        phases_dir.mkdir()
        (phases_dir / "phase-99.md").write_text(
            "---\nid: phase-99\nmode: corporate\ntype: feature\nclient_id: visagio\n"
            "status: planned\nblocks_count: 2\n---\n# Phase 99\n",
            encoding="utf-8",
        )

        from phase_manager import _read_phase_meta
        meta = _read_phase_meta(root, "phase-99")
        assert meta["mode"] == "corporate"
        assert meta["type"] == "feature"
        assert meta["client_id"] == "visagio"


def test_phase_manager_start_corporate_smoke():
    """phase_manager.start_phase with mode=corporate must update STATE without crash."""
    import io
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "STATE.md").write_text("# STATE — AI-only\n\np:28 status:complete\n", encoding="utf-8")
        (root / "NEXT.md").write_text("# NEXT — AI-only\n\nnext_action:-\n", encoding="utf-8")
        (root / "board.md").write_text(
            "# board\nagent:implementer b:- group:- status:idle lock:ready deps:- ts:2026-06-01\n",
            encoding="utf-8",
        )

        phases_dir = root / "phases"
        phases_dir.mkdir()
        (phases_dir / "phase-99.md").write_text(
            "---\nid: phase-99\nmode: corporate\ntype: feature\nclient_id: acme\n"
            "status: planned\nblocks_count: 1\n---\n\n# Phase 99 — Test\n\n"
            "## 2. Tickets / Block Index\n\n| block-999 | Test | planned | manifests/block-999.md |\n",
            encoding="utf-8",
        )

        from phase_manager import start_phase
        from state_manager import read_state

        captured = io.StringIO()
        orig = sys.stdout
        sys.stdout = captured
        try:
            start_phase(root, "phase-99")
        finally:
            sys.stdout = orig

        state = read_state(root)
        assert state.get("mode") == "corporate"
        assert state.get("current_client") == "acme"


# ---------------------------------------------------------------------------
# session_start mode reading
# ---------------------------------------------------------------------------

def test_session_start_reads_mode():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "STATE.md").write_text(
            "# STATE — AI-only\n\np:29 status:active mode:corporate "
            "current_client:visagio tickets_open:2 last_scan_at:2026-06-01\n",
            encoding="utf-8",
        )
        from session_start import _read_state
        state = _read_state(root)
        assert state.get("mode") == "corporate"
        assert state.get("current_client") == "visagio"
        assert state.get("tickets_open") == "2"


if __name__ == "__main__":
    test_pilot_state_read_write()
    test_pilot_state_save()
    test_phase_meta_reads_mode()
    test_phase_manager_start_corporate_smoke()
    test_session_start_reads_mode()
    print("All block-163 tests passed.")
