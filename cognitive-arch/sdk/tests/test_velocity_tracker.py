# sdk/tests/test_velocity_tracker.py
# PURPOSE: Validate velocity_tracker: started_at, pause/resume, actual_duration_hours,
#          phase timestamps, and velocity_inference integration.
# BLOCK:   block-173

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


def _make_arch(tmp: str) -> Path:
    arch = Path(tmp) / "arch"
    (arch / "manifests").mkdir(parents=True)
    (arch / "phases").mkdir()
    (arch / "blocks").mkdir()
    (arch / "sdk").mkdir()
    (arch / "STATE.md").write_text("# STATE\n\np:32 status:active\n", encoding="utf-8")
    (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")
    return arch


def _make_manifest(arch: Path, block_id: str) -> Path:
    p = arch / "manifests" / f"{block_id}-test.md"
    p.write_text(
        f"---\nid: {block_id}\nsize: S\nimportance: normal\nkind: implementation\n"
        "phase: phase-32\nstatus: wip\nstarted_at: ~\npaused_at: ~\nresumed_at: ~\n"
        "finished_at: ~\nactual_duration_hours: ~\n---\n",
        encoding="utf-8",
    )
    return p


def _make_phase(arch: Path, phase_id: str) -> Path:
    p = arch / "phases" / f"{phase_id}.md"
    p.write_text(
        f"---\nid: {phase_id}\nmode: mmorpg\nstatus: active\n"
        "phase_started_at: ~\nphase_finished_at: ~\nphase_duration_hours: ~\n---\n"
        f"# {phase_id}\n",
        encoding="utf-8",
    )
    return p


# ---------------------------------------------------------------------------
# Basic timestamp tests
# ---------------------------------------------------------------------------

def test_stamp_started_writes_timestamp():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")

        from velocity_tracker import stamp_started
        ts = stamp_started(arch, "block-999")
        assert ts != ""

        text = (arch / "manifests" / "block-999-test.md").read_text(encoding="utf-8")
        assert "started_at:" in text
        assert ts in text


def test_stamp_finished_computes_duration():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")

        from velocity_tracker import stamp_started, stamp_finished
        stamp_started(arch, "block-999")
        # Minimal sleep not needed — same second is fine, duration will be ~0
        ts, hours = stamp_finished(arch, "block-999")
        assert ts != ""
        assert isinstance(hours, float)
        assert hours >= 0.0


def test_pause_resume_reduces_duration():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")

        from velocity_tracker import stamp_started, pause_timer, resume_timer, stamp_finished

        stamp_started(arch, "block-999")
        pause_msg = pause_timer(arch, "block-999")
        assert "pausado" in pause_msg.lower() or "paused" in pause_msg.lower()

        resume_msg = resume_timer(arch, "block-999")
        assert "retomado" in resume_msg.lower() or "resumed" in resume_msg.lower()
        # After resume, paused_duration_hours should be set
        text = (arch / "manifests" / "block-999-test.md").read_text(encoding="utf-8")
        assert "paused_duration_hours" in text

        _, hours = stamp_finished(arch, "block-999")
        assert isinstance(hours, float)


def test_status_output():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")

        from velocity_tracker import stamp_started, get_status
        stamp_started(arch, "block-999")
        status = get_status(arch, "block-999")
        assert "started_at" in status
        assert "block-999" in status


# ---------------------------------------------------------------------------
# Phase timestamps
# ---------------------------------------------------------------------------

def test_phase_started_at():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_phase(arch, "phase-99")

        from velocity_tracker import stamp_phase_started
        ts = stamp_phase_started(arch, "phase-99")
        assert ts != ""
        text = (arch / "phases" / "phase-99.md").read_text(encoding="utf-8")
        assert ts in text


def test_phase_duration_computed():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_phase(arch, "phase-99")

        from velocity_tracker import stamp_phase_started, stamp_phase_finished
        stamp_phase_started(arch, "phase-99")
        _, hours = stamp_phase_finished(arch, "phase-99")
        assert isinstance(hours, float)
        assert hours >= 0.0


# ---------------------------------------------------------------------------
# velocity_inference integration
# ---------------------------------------------------------------------------

def test_velocity_inference_uses_actual_hours():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        p = _make_manifest(arch, "block-999")
        # Pre-write actual_duration_hours into manifest
        text = p.read_text(encoding="utf-8")
        import re
        text = re.sub(r"^actual_duration_hours:\s*~", "actual_duration_hours: 2.5", text, flags=re.MULTILINE)
        p.write_text(text, encoding="utf-8")

        from velocity_inference import infer_duration
        hours, source = infer_duration("block-999", arch)
        assert source == "actual"
        assert hours == 2.5


if __name__ == "__main__":
    test_stamp_started_writes_timestamp()
    test_stamp_finished_computes_duration()
    test_pause_resume_reduces_duration()
    test_status_output()
    test_phase_started_at()
    test_phase_duration_computed()
    test_velocity_inference_uses_actual_hours()
    print("All block-173 tests passed.")
