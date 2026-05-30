# sdk/tests/test_patterns_report_loop.py
# PURPOSE: End-to-end test of the closed self-observation loop:
#          extract → analyze (full history) → recommend → render → propose.
# DEPS:    pytest, sdk/patterns_report, sdk/protocol_updater
# SEE:     blocks/block-139-close-loop.md, sdk/patterns_report.py::run_pipeline

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from patterns_report import run_pipeline


def _write_retro_and_manifest(
    arch: Path,
    block_id: str,
    *,
    forced_pass: bool,
    tier: str = "M",
) -> None:
    """Write minimal retro + manifest that retro_signals can parse."""
    blocks = arch / "blocks"
    manifests = arch / "manifests"
    blocks.mkdir(parents=True, exist_ok=True)
    manifests.mkdir(parents=True, exist_ok=True)

    manifest_text = (
        "---\n"
        f"id: {block_id}\n"
        f"tier: {tier}\n"
        "kind: implementation\n"
        "phase: phase-1\n"
        "status: pending\n"
        "estimated_duration_days: 1\n"
        "files:\n"
        "  read: []\n"
        "  modify: []\n"
        "  create: []\n"
        "gates: []\n"
        "created_at: 2026-05-01\n"
        "---\n\n"
        f"# {block_id}\n"
    )
    (manifests / f"{block_id}-loop-test.md").write_text(manifest_text, encoding="utf-8")

    body = (
        f"# {block_id} Retrospective — loop test\n\n"
        "## 1. What was built\n\nSynthetic block for the close-loop test.\n\n"
        "## 8. Files actually touched\n\nAs manifest.\n"
    )
    if forced_pass:
        body += "\n## 9. Notes\n\nNeeded a force-pass to land — flagged for review.\n"

    retro_text = (
        "---\n"
        f"id: {block_id}\n"
        f"tier: {tier}\n"
        "status: done\n"
        "actual_duration_hours: 2.0\n"
        "duration_source: estimated\n"
        "gates_passed: 4/4\n"
        "created_at: 2026-05-01\n"
        "---\n\n"
        + body
    )
    (blocks / f"{block_id}-loop-test.md").write_text(retro_text, encoding="utf-8")


@pytest.fixture
def synthetic_arch(tmp_path: Path) -> Path:
    """Arch root with five force-passed blocks — guaranteed to trip R5 (critical)."""
    arch = tmp_path / "arch"
    arch.mkdir()
    for i in range(5):
        _write_retro_and_manifest(arch, f"block-{i + 1:03}", forced_pass=True)
    # Also write one clean block — should not affect R5
    _write_retro_and_manifest(arch, "block-006", forced_pass=False)
    return arch


class TestRunPipelineEndToEnd:
    def test_renders_patterns_md_with_recommendation(self, synthetic_arch):
        run_pipeline(synthetic_arch, window_size=None, propose=False)

        patterns_md = synthetic_arch / "governance" / "patterns.md"
        assert patterns_md.exists(), "patterns_report must render governance/patterns.md"
        text = patterns_md.read_text(encoding="utf-8")

        assert "forced-pass-clustering" in text, (
            "R5 must fire on 5 force-passed blocks"
        )
        assert "**Recommendation:**" in text, (
            "patterns.md must carry a populated Recommendation line "
            "(was previously the placeholder 'No recommendation yet')"
        )
        assert "_No recommendation yet" not in text, (
            "Placeholder must be replaced once recommendation_engine runs"
        )

    def test_propose_creates_proposal_file(self, synthetic_arch):
        summary = run_pipeline(synthetic_arch, window_size=None, propose=True)

        assert summary["proposals_created"] >= 1, (
            "ProtocolUpdater must emit at least one proposal for a critical "
            "pattern that is above the D1=3 threshold"
        )

        proposals_dir = synthetic_arch / "governance" / "proposals"
        proposal_files = [p for p in proposals_dir.glob("*.md") if p.name != "index.md"]
        assert proposal_files, "at least one proposal file must land on disk"

        # The proposal should reference the R5 pattern
        all_text = "".join(p.read_text(encoding="utf-8") for p in proposal_files)
        assert "forced-pass-clustering" in all_text

    def test_propose_updates_index(self, synthetic_arch):
        run_pipeline(synthetic_arch, window_size=None, propose=True)
        index = synthetic_arch / "governance" / "proposals" / "index.md"
        assert index.exists()
        text = index.read_text(encoding="utf-8")
        assert "forced-pass-clustering" in text
        assert "pending" in text

    def test_pipeline_is_idempotent(self, synthetic_arch):
        first = run_pipeline(synthetic_arch, window_size=None, propose=True)
        second = run_pipeline(synthetic_arch, window_size=None, propose=True)
        assert first["proposals_created"] >= 1
        assert second["proposals_created"] == 0, (
            "Second run must not duplicate proposals — _already_proposed must dedup"
        )

    def test_no_propose_flag_skips_protocol_updater(self, synthetic_arch):
        summary = run_pipeline(synthetic_arch, window_size=None, propose=False)
        assert summary["proposals_created"] == 0
        proposals_dir = synthetic_arch / "governance" / "proposals"
        if proposals_dir.exists():
            files = [p for p in proposals_dir.glob("*.md") if p.name != "index.md"]
            assert not files

    def test_summary_shape(self, synthetic_arch):
        summary = run_pipeline(synthetic_arch, window_size=None, propose=True)
        assert summary["signals"] == 6
        assert summary["patterns"] >= 1
        assert summary["recommendations"] >= 1
        assert "report_path" in summary
