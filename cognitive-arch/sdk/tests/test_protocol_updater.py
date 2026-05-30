# PURPOSE: Tests for sdk/protocol_updater.py — proposal generation from patterns
# INPUTS:  tmp_path, synthetic patterns.md content
# OUTPUTS: assertions on proposal file creation and index updates
# DEPS:    pytest, pathlib, protocol_updater module
# SEE:     sdk/protocol_updater.py, templates/proposal.md, phases/phase-20.md block-122

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from protocol_updater import ProtocolUpdater, _parse_patterns_md, _make_proposal_id, _already_proposed


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_patterns(tmp_path: Path, content: str) -> None:
    gov = tmp_path / "governance"
    gov.mkdir(exist_ok=True)
    (gov / "patterns.md").write_text(content, encoding="utf-8")


_PATTERN_ABOVE_THRESHOLD = """# governance/patterns.md

## 🟡 WARN — duration-overrun-recurring

**Rule:** R2
**Description:** 4 of last 30 blocks had duration overruns.
**First detected:** block-010
**Last detected:** block-050
**Occurrences:** 4

**Evidence blocks:** `block-010`, `block-030`, `block-040`, `block-050`
"""

_PATTERN_BELOW_THRESHOLD = """# governance/patterns.md

## 🟡 WARN — gate-failures-recurring

**Rule:** R3
**Description:** 2 blocks had gate failures.
**Occurrences:** 2

**Evidence blocks:** `block-010`, `block-020`
"""

_TWO_PATTERNS = _PATTERN_ABOVE_THRESHOLD + """
## 🔴 CRITICAL — axiom-q4-repeated-violation

**Rule:** R1
**Description:** Axiom Q4 violated 5 times.
**First detected:** block-005
**Last detected:** block-055
**Occurrences:** 5

**Evidence blocks:** `block-005`, `block-015`, `block-025`, `block-035`, `block-055`
"""


# ---------------------------------------------------------------------------
# _parse_patterns_md tests
# ---------------------------------------------------------------------------

class TestParsePatternsmd:
    def test_parses_single_pattern(self):
        patterns = _parse_patterns_md(_PATTERN_ABOVE_THRESHOLD)
        assert len(patterns) == 1
        assert patterns[0]["name"] == "duration-overrun-recurring"
        assert patterns[0]["occurrences"] == 4
        assert patterns[0]["severity"] == "warn"
        assert "block-010" in patterns[0]["evidence"]

    def test_parses_two_patterns(self):
        patterns = _parse_patterns_md(_TWO_PATTERNS)
        assert len(patterns) == 2

    def test_empty_text_returns_empty(self):
        assert _parse_patterns_md("") == []

    def test_critical_severity_detected(self):
        patterns = _parse_patterns_md(_TWO_PATTERNS)
        names = {p["name"]: p["severity"] for p in patterns}
        assert names.get("axiom-q4-repeated-violation") == "critical"


# ---------------------------------------------------------------------------
# ProtocolUpdater.run tests
# ---------------------------------------------------------------------------

class TestProtocolUpdater:
    def test_creates_proposal_above_threshold(self, tmp_path):
        _write_patterns(tmp_path, _PATTERN_ABOVE_THRESHOLD)
        updater = ProtocolUpdater(tmp_path)
        created = updater.run()
        assert len(created) == 1
        assert created[0].exists()

    def test_no_proposal_below_threshold(self, tmp_path):
        _write_patterns(tmp_path, _PATTERN_BELOW_THRESHOLD)
        updater = ProtocolUpdater(tmp_path)
        created = updater.run()
        assert len(created) == 0

    def test_idempotent_no_duplicate(self, tmp_path):
        _write_patterns(tmp_path, _PATTERN_ABOVE_THRESHOLD)
        updater = ProtocolUpdater(tmp_path)
        first = updater.run()
        second = updater.run()
        assert len(first) == 1
        assert len(second) == 0  # duplicate skipped

    def test_two_patterns_two_proposals(self, tmp_path):
        _write_patterns(tmp_path, _TWO_PATTERNS)
        updater = ProtocolUpdater(tmp_path)
        created = updater.run()
        assert len(created) == 2

    def test_proposal_has_valid_fields(self, tmp_path):
        _write_patterns(tmp_path, _PATTERN_ABOVE_THRESHOLD)
        updater = ProtocolUpdater(tmp_path)
        created = updater.run()
        text = created[0].read_text(encoding="utf-8")
        assert "status: pending" in text
        assert "pattern_id:" in text
        assert "proposed_change:" in text
        assert "signal_count_d1: 4" in text

    def test_index_updated_on_create(self, tmp_path):
        _write_patterns(tmp_path, _PATTERN_ABOVE_THRESHOLD)
        updater = ProtocolUpdater(tmp_path)
        updater.run()
        index = tmp_path / "governance" / "proposals" / "index.md"
        assert index.exists()
        assert "duration-overrun-recurring" in index.read_text(encoding="utf-8")

    def test_dry_run_creates_no_files(self, tmp_path):
        _write_patterns(tmp_path, _PATTERN_ABOVE_THRESHOLD)
        updater = ProtocolUpdater(tmp_path)
        created = updater.run(dry_run=True)
        assert created == []
        # No proposal files should exist
        proposals_dir = tmp_path / "governance" / "proposals"
        if proposals_dir.exists():
            assert not list(proposals_dir.glob("*.md"))

    def test_missing_patterns_md_returns_empty(self, tmp_path):
        updater = ProtocolUpdater(tmp_path)
        created = updater.run()
        assert created == []

    def test_make_proposal_id_deterministic(self):
        id1 = _make_proposal_id("some-pattern", "2026-05-28")
        id2 = _make_proposal_id("some-pattern", "2026-05-28")
        assert id1 == id2

    def test_already_proposed_false_when_no_files(self, tmp_path):
        proposals_dir = tmp_path / "proposals"
        proposals_dir.mkdir()
        assert not _already_proposed(proposals_dir, "some-pattern")

    def test_already_proposed_true_when_file_exists(self, tmp_path):
        proposals_dir = tmp_path / "proposals"
        proposals_dir.mkdir()
        (proposals_dir / "2026-05-28-some-pattern.md").write_text("x", encoding="utf-8")
        assert _already_proposed(proposals_dir, "some-pattern")
