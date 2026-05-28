# PURPOSE: Tests for dashboard token widget (_render_token_widget) — block-115
# INPUTS:  synthetic TokenRecord-like objects
# OUTPUTS: assertions on HTML output of _render_token_widget
# DEPS:    pytest, dashboard_generator module
# SEE:     sdk/dashboard_generator.py, phases/phase-18.md block-115

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from dashboard_generator import _render_token_widget


def _rec(block_id, tok_actual, tok_estimated=None, date="2026-05-28"):
    return SimpleNamespace(
        block_id=block_id,
        tok_actual=tok_actual,
        tok_estimated=tok_estimated,
        date=date,
    )


class TestRenderTokenWidget:
    def test_none_records_shows_not_found(self):
        html = _render_token_widget(None)
        assert "Token report not found" in html
        assert "token_tracker" in html

    def test_empty_list_shows_insufficient_data(self):
        html = _render_token_widget([])
        assert "Insufficient data" in html

    def test_one_record_shows_insufficient_data(self):
        html = _render_token_widget([_rec("block-001", 500)])
        assert "Insufficient data" in html

    def test_two_records_shows_insufficient_data(self):
        html = _render_token_widget([_rec("block-001", 500), _rec("block-002", 600)])
        assert "Insufficient data" in html

    def test_three_records_shows_chart(self):
        records = [_rec(f"block-{i:03d}", 1000 + i * 100) for i in range(3)]
        html = _render_token_widget(records)
        assert "Token Usage" in html
        assert "block-000" in html
        assert "1,000" in html or "1000" in html

    def test_seven_records_shows_bar_chart(self):
        records = [_rec(f"block-{i:03d}", 1000 * (i + 1)) for i in range(7)]
        html = _render_token_widget(records)
        assert "Token Usage" in html
        assert "tok_actual" in html.lower() or "total" in html.lower()

    def test_budget_shown_when_provided(self):
        records = [_rec(f"block-{i:03d}", 5000) for i in range(5)]
        html = _render_token_widget(records, budget=30000)
        assert "Budget" in html
        assert "30,000" in html

    def test_budget_overrun_shows_red(self):
        records = [_rec(f"block-{i:03d}", 10000) for i in range(5)]
        html = _render_token_widget(records, budget=30000)
        assert "var(--red)" in html  # 50k > 30k budget

    def test_budget_within_shows_green(self):
        records = [_rec(f"block-{i:03d}", 1000) for i in range(3)]
        html = _render_token_widget(records, budget=100000)
        assert "var(--green)" in html

    def test_records_without_tok_actual_excluded(self):
        records = [
            _rec("block-001", None),
            _rec("block-002", None),
            _rec("block-003", None),
            _rec("block-004", 1000),
        ]
        html = _render_token_widget(records)
        assert "Insufficient data" in html  # only 1 tracked

    def test_avg_per_block_shown(self):
        records = [_rec(f"block-{i:03d}", 2000) for i in range(4)]
        html = _render_token_widget(records)
        assert "Avg/block" in html
        assert "2,000" in html
