# PURPOSE: Tests for ADR index management and dashboard ADR widget — block-120
# INPUTS:  tmp_path, synthetic ADR files and index content
# OUTPUTS: assertions on index content and _render_adr_widget HTML output
# DEPS:    pytest, pathlib, adr_drafter, dashboard_generator modules
# SEE:     sdk/adr_drafter.py, sdk/dashboard_generator.py, phases/phase-19.md block-120

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from adr_drafter import AdrDrafter, _rebuild_index, _update_adr_index
from dashboard_generator import _render_adr_widget


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decision(title, significance="high"):
    return {
        "title": title,
        "significance": significance,
        "recommended_option": "Option A",
        "options_considered": ["Option A", "Option B"],
        "confidence_band": "high",
        "context": "ctx",
        "synthesis_source": "design/test.md",
    }

def _write_adr(adrs_dir: Path, name: str, title: str, status: str = "draft", date: str = "2026-05-28"):
    adrs_dir.mkdir(parents=True, exist_ok=True)
    (adrs_dir / name).write_text(
        f"---\ntitle: {title}\nstatus: {status}\ncreated_at: {date}\nauto_generated: true\n---\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Index management tests
# ---------------------------------------------------------------------------

class TestAdrIndex:
    def test_generate_updates_index(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        drafter.generate([_decision("New ADR Title")])
        index = tmp_path / "governance" / "adrs" / "index.md"
        assert index.exists()
        assert "New ADR Title" in index.read_text(encoding="utf-8")

    def test_index_append_only(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        drafter.generate([_decision("First ADR")])
        drafter.generate([_decision("Second ADR")])
        text = (tmp_path / "governance" / "adrs" / "index.md").read_text(encoding="utf-8")
        assert "First ADR" in text
        assert "Second ADR" in text

    def test_rebuild_counts_all_adrs(self, tmp_path):
        adrs_dir = tmp_path / "design" / "adrs"
        _write_adr(adrs_dir, "adr-a.md", "ADR Alpha")
        _write_adr(adrs_dir, "adr-b.md", "ADR Beta", status="accepted")
        count = _rebuild_index(tmp_path)
        assert count == 2

    def test_rebuild_includes_status(self, tmp_path):
        adrs_dir = tmp_path / "design" / "adrs"
        _write_adr(adrs_dir, "adr-c.md", "ADR Gamma", status="rejected")
        _rebuild_index(tmp_path)
        text = (tmp_path / "governance" / "adrs" / "index.md").read_text(encoding="utf-8")
        assert "rejected" in text

    def test_rebuild_empty_dir_produces_empty_index(self, tmp_path):
        (tmp_path / "design" / "adrs").mkdir(parents=True)
        count = _rebuild_index(tmp_path)
        assert count == 0
        assert (tmp_path / "governance" / "adrs" / "index.md").exists()

    def test_rebuild_missing_dir_returns_zero(self, tmp_path):
        count = _rebuild_index(tmp_path)
        assert count == 0


# ---------------------------------------------------------------------------
# Dashboard ADR widget tests
# ---------------------------------------------------------------------------

class TestRenderAdrWidget:
    def test_none_path_shows_not_found(self):
        html = _render_adr_widget(None)
        assert "not found" in html.lower() or "ADR index not found" in html

    def test_missing_file_shows_not_found(self, tmp_path):
        html = _render_adr_widget(tmp_path / "nonexistent.md")
        assert "not found" in html.lower()

    def test_empty_index_shows_no_adrs(self, tmp_path):
        index = tmp_path / "index.md"
        index.write_text("# ADR Index\n\n| Date | Title | Status |\n|---|---|---|\n", encoding="utf-8")
        html = _render_adr_widget(index)
        assert "No ADRs" in html

    def test_populated_index_shows_count(self, tmp_path):
        index = tmp_path / "index.md"
        index.write_text(
            "# ADR Index\n\n"
            "| Date | Title | Status |\n|---|---|---|\n"
            "| 2026-05-28 | [ADR A](design/adrs/a.md) | draft |\n"
            "| 2026-05-27 | [ADR B](design/adrs/b.md) | accepted |\n",
            encoding="utf-8",
        )
        html = _render_adr_widget(index)
        assert "2" in html  # total count
        assert "draft" in html
        assert "accepted" in html
        assert "2026-05-28" in html  # last date

    def test_widget_returns_html_card(self, tmp_path):
        index = tmp_path / "index.md"
        index.write_text(
            "| 2026-05-28 | [X](d/x.md) | draft |\n", encoding="utf-8")
        html = _render_adr_widget(index)
        assert "<div" in html
        assert "ADR" in html
