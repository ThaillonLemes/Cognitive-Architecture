# PURPOSE: Tests for _render_proposals_widget() in dashboard_generator.py (block-124)
# INPUTS:  tmp_path, synthetic governance/proposals/index.md
# OUTPUTS: assertions on HTML output from the proposals widget
# DEPS:    pytest, pathlib, dashboard_generator module
# SEE:     sdk/dashboard_generator.py, manifests/block-124-dashboard-proposals.md

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from dashboard_generator import _render_proposals_widget


_HEADER = (
    "# Proposals Index — Governance\n\n"
    "| Date | ID | Pattern | Target File | Status |\n"
    "|------|----|---------|-------------|--------|\n"
)

_ROW_PENDING = "| 2026-05-28 | [2026-05-28-scope-expansion](governance/proposals/2026-05-28-scope-expansion.md) | scope-expansion-recurring | templates/manifest-medium.md | pending |\n"
_ROW_ACCEPTED = "| 2026-05-27 | [2026-05-27-duration-overrun](governance/proposals/2026-05-27-duration-overrun.md) | duration-overrun-recurring | protocols/block-complexity-estimator.md | accepted |\n"


def _write_index(tmp_path: Path, extra_rows: str = "") -> Path:
    index_path = tmp_path / "index.md"
    index_path.write_text(_HEADER + extra_rows, encoding="utf-8")
    return index_path


class TestRenderProposalsWidgetMissingIndex:
    def test_none_path_shows_fallback(self):
        html = _render_proposals_widget(None)
        assert "Proposals index not found" in html
        assert "protocol_updater.py" in html

    def test_nonexistent_path_shows_fallback(self, tmp_path):
        html = _render_proposals_widget(tmp_path / "nonexistent.md")
        assert "Proposals index not found" in html


class TestRenderProposalsWidgetEmpty:
    def test_empty_table_shows_quiet_message(self, tmp_path):
        index_path = _write_index(tmp_path)
        html = _render_proposals_widget(index_path)
        assert "learning loop is quiet" in html.lower() or "no proposals" in html.lower()

    def test_empty_table_still_has_heading(self, tmp_path):
        index_path = _write_index(tmp_path)
        html = _render_proposals_widget(index_path)
        assert "Learning Loop" in html


class TestRenderProposalsWidgetWithData:
    def test_single_pending_badge_shows_1(self, tmp_path):
        index_path = _write_index(tmp_path, _ROW_PENDING)
        html = _render_proposals_widget(index_path)
        assert "1 pending" in html

    def test_accepted_row_not_counted_as_pending(self, tmp_path):
        index_path = _write_index(tmp_path, _ROW_ACCEPTED)
        html = _render_proposals_widget(index_path)
        assert "0 pending" in html

    def test_mixed_pending_and_accepted(self, tmp_path):
        index_path = _write_index(tmp_path, _ROW_PENDING + _ROW_ACCEPTED)
        html = _render_proposals_widget(index_path)
        assert "1 pending" in html

    def test_three_pending_badge_shows_3(self, tmp_path):
        rows = _ROW_PENDING * 3
        index_path = _write_index(tmp_path, rows)
        html = _render_proposals_widget(index_path)
        assert "3 pending" in html

    def test_pattern_id_in_table(self, tmp_path):
        index_path = _write_index(tmp_path, _ROW_PENDING)
        html = _render_proposals_widget(index_path)
        assert "scope-expansion-recurring" in html

    def test_status_badge_pending_class(self, tmp_path):
        index_path = _write_index(tmp_path, _ROW_PENDING)
        html = _render_proposals_widget(index_path)
        assert "badge-warning" in html

    def test_status_badge_accepted_class(self, tmp_path):
        index_path = _write_index(tmp_path, _ROW_ACCEPTED)
        html = _render_proposals_widget(index_path)
        assert "badge-done" in html


class TestRenderProposalsWidgetLastFive:
    def test_six_rows_only_last_five_shown(self, tmp_path):
        rows = "".join(
            f"| 2026-05-{20+i:02d} | [2026-05-{20+i:02d}-p{i}](governance/proposals/x{i}.md) | pattern-{i} | protocols/x.md | pending |\n"
            for i in range(6)
        )
        index_path = _write_index(tmp_path, rows)
        html = _render_proposals_widget(index_path)
        # Last 5 should appear; first one (pattern-0) should not
        assert "pattern-5" in html
        assert "pattern-1" in html
        assert "pattern-0" not in html

    def test_five_or_fewer_all_shown(self, tmp_path):
        rows = "".join(
            f"| 2026-05-{20+i:02d} | [2026-05-{20+i:02d}-p{i}](governance/proposals/x{i}.md) | pattern-{i} | protocols/x.md | pending |\n"
            for i in range(3)
        )
        index_path = _write_index(tmp_path, rows)
        html = _render_proposals_widget(index_path)
        for i in range(3):
            assert f"pattern-{i}" in html


class TestRenderProposalsWidgetHtml:
    def test_returns_string(self, tmp_path):
        index_path = _write_index(tmp_path, _ROW_PENDING)
        html = _render_proposals_widget(index_path)
        assert isinstance(html, str)

    def test_contains_card_class(self, tmp_path):
        index_path = _write_index(tmp_path, _ROW_PENDING)
        html = _render_proposals_widget(index_path)
        assert 'class="card"' in html
