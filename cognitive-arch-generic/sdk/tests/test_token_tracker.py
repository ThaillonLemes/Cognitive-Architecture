# PURPOSE: Tests for sdk/token_tracker.py — token record parsing and report generation
# INPUTS:  tmp_path, synthetic retro files
# OUTPUTS: pass/fail assertions on TokenRecord, TokenTracker, report output
# DEPS:    pytest, pathlib, token_tracker module
# SEE:     sdk/token_tracker.py, phases/phase-18.md block-113

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from token_tracker import TokenRecord, TokenTracker, _extract_int, _extract_field


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_retro(tmp_path: Path, name: str, content: str) -> Path:
    blocks = tmp_path / "blocks"
    blocks.mkdir(exist_ok=True)
    p = blocks / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# _extract_int tests
# ---------------------------------------------------------------------------

class TestExtractInt:
    def test_numeric_returns_int(self):
        assert _extract_int("tok_actual: 1500\n", r"^tok_actual:\s*(.+)") == 1500

    def test_null_returns_none(self):
        assert _extract_int("tok_actual: null\n", r"^tok_actual:\s*(.+)") is None

    def test_tilde_returns_none(self):
        assert _extract_int("tok_actual: ~\n", r"^tok_actual:\s*(.+)") is None

    def test_empty_returns_none(self):
        assert _extract_int("tok_actual: \n", r"^tok_actual:\s*(.+)") is None

    def test_missing_field_returns_none(self):
        assert _extract_int("other_field: 100\n", r"^tok_actual:\s*(.+)") is None

    def test_non_numeric_returns_none(self):
        assert _extract_int("tok_actual: abc\n", r"^tok_actual:\s*(.+)") is None


# ---------------------------------------------------------------------------
# TokenRecord.from_retro tests
# ---------------------------------------------------------------------------

class TestTokenRecordFromRetro:
    def test_full_record_parsed(self, tmp_path):
        p = _write_retro(tmp_path, "block-100-test.md",
            "---\nid: block-100\nphase: phase-10\ntok_estimated: 2000\ntok_actual: 1800\ncreated_at: 2026-05-10\n---\n")
        rec = TokenRecord.from_retro(p)
        assert rec is not None
        assert rec.block_id == "block-100"
        assert rec.phase == "phase-10"
        assert rec.tok_estimated == 2000
        assert rec.tok_actual == 1800
        assert rec.delta == -200
        assert rec.missing is False

    def test_missing_tok_actual_sets_missing_true(self, tmp_path):
        p = _write_retro(tmp_path, "block-101-test.md",
            "---\nid: block-101\nphase: phase-10\ntok_estimated: 1000\ncreated_at: 2026-05-10\n---\n")
        rec = TokenRecord.from_retro(p)
        assert rec is not None
        assert rec.tok_actual is None
        assert rec.delta is None
        assert rec.missing is True

    def test_null_tok_actual_sets_missing_true(self, tmp_path):
        p = _write_retro(tmp_path, "block-102-test.md",
            "---\nid: block-102\nphase: phase-10\ntok_actual: null\ncreated_at: 2026-05-10\n---\n")
        rec = TokenRecord.from_retro(p)
        assert rec is not None
        assert rec.missing is True

    def test_tok_dash_actual_variant(self, tmp_path):
        p = _write_retro(tmp_path, "block-103-test.md",
            "---\nid: block-103\nphase: phase-11\ntok-actual: 500\ncreated_at: 2026-05-11\n---\n")
        rec = TokenRecord.from_retro(p)
        assert rec is not None
        assert rec.tok_actual == 500
        assert rec.missing is False

    def test_tokens_actual_variant(self, tmp_path):
        p = _write_retro(tmp_path, "block-104-test.md",
            "---\nid: block-104\nphase: phase-11\ntokens_actual: 900\ncreated_at: 2026-05-11\n---\n")
        rec = TokenRecord.from_retro(p)
        assert rec is not None
        assert rec.tok_actual == 900

    def test_id_derived_from_filename_when_missing(self, tmp_path):
        p = _write_retro(tmp_path, "block-105-someblock.md",
            "---\nphase: phase-12\ntok_actual: 300\ncreated_at: 2026-05-12\n---\n")
        rec = TokenRecord.from_retro(p)
        assert rec is not None
        assert rec.block_id == "block-105"

    def test_malformed_file_no_crash(self, tmp_path):
        p = _write_retro(tmp_path, "block-106-bad.md", "not yaml at all just text")
        rec = TokenRecord.from_retro(p)
        # Should return a record with mostly None fields, not crash
        assert rec is not None


# ---------------------------------------------------------------------------
# TokenTracker tests
# ---------------------------------------------------------------------------

class TestTokenTracker:
    def test_load_scans_retros(self, tmp_path):
        _write_retro(tmp_path, "block-200-a.md",
            "---\nid: block-200\nphase: phase-20\ntok_estimated: 1000\ntok_actual: 900\ncreated_at: 2026-05-20\n---\n")
        _write_retro(tmp_path, "block-201-b.md",
            "---\nid: block-201\nphase: phase-20\ntok_estimated: 500\ncreated_at: 2026-05-20\n---\n")
        tracker = TokenTracker(tmp_path).load()
        assert len(tracker.records) == 2

    def test_block_log_excluded(self, tmp_path):
        (tmp_path / "blocks").mkdir(exist_ok=True)
        (tmp_path / "blocks" / "BLOCK_LOG.md").write_text("block-200 done - 2026-05-20\n", encoding="utf-8")
        tracker = TokenTracker(tmp_path).load()
        assert all("LOG" not in r.block_id.upper() for r in tracker.records)

    def test_report_contains_header(self, tmp_path):
        _write_retro(tmp_path, "block-210-x.md",
            "---\nid: block-210\nphase: phase-21\ntok_actual: 1200\ncreated_at: 2026-05-21\n---\n")
        tracker = TokenTracker(tmp_path).load()
        report = tracker.report()
        assert "# Token Report" in report
        assert "Per-Block Summary" in report
        assert "Per-Phase Summary" in report

    def test_report_marks_missing(self, tmp_path):
        _write_retro(tmp_path, "block-220-y.md",
            "---\nid: block-220\nphase: phase-22\ntok_estimated: 1000\ncreated_at: 2026-05-22\n---\n")
        tracker = TokenTracker(tmp_path).load()
        report = tracker.report()
        assert "null" in report or "missing" in report.lower()

    def test_write_report_creates_file(self, tmp_path):
        _write_retro(tmp_path, "block-230-z.md",
            "---\nid: block-230\nphase: phase-22\ntok_actual: 400\ncreated_at: 2026-05-22\n---\n")
        tracker = TokenTracker(tmp_path).load()
        out = tracker.write_report(tmp_path / "governance")
        assert out.exists()
        assert "Token Report" in out.read_text(encoding="utf-8")

    def test_empty_blocks_dir(self, tmp_path):
        (tmp_path / "blocks").mkdir()
        tracker = TokenTracker(tmp_path).load()
        assert tracker.records == []
        report = tracker.report()
        assert "0" in report

    def test_no_blocks_dir(self, tmp_path):
        tracker = TokenTracker(tmp_path).load()
        assert tracker.records == []
