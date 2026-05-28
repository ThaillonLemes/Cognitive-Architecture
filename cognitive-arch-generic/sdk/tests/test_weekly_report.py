# cognitive-arch / sdk/tests/test_weekly_report.py
# purpose: Unit tests for sdk/weekly_report.py
# stdlib-only; no external dependencies

import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from weekly_report import (
    WeeklyReport,
    generate_weekly_report,
    render_html,
    write_report,
    _blocks_in_period,
    _extract_pattern_names,
    _velocity,
    _forecast,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)
_NOW_TS = _NOW.isoformat()

_SAMPLE_LOG = """
# BLOCK_LOG
block-090 done - 2026-05-21
block-095 done - 2026-05-23
block-096 done - 2026-05-23
block-097 done - 2026-05-27
block-098 done - 2026-05-27
block-099 done - 2026-05-27
"""

_SAMPLE_STATE = "phase:16 last_block:block-103 next:block-104 status:active"
_SAMPLE_NEXT = "next_action:start-block-104 phase:phase-16"
_SAMPLE_PATTERNS = """
# Patterns Report

## Summary Table
| # | pattern | severity |
|---|---------|---------|
| 1 | velocity-data-gap | info |

## velocity-data-gap

INFO pattern detected 85 times.
"""


# ---------------------------------------------------------------------------
# Tests: helpers
# ---------------------------------------------------------------------------

def test_blocks_in_period_correct():
    blocks = _blocks_in_period(_SAMPLE_LOG, "2026-05-27", "2026-05-27")
    assert "block-097" in blocks
    assert "block-098" in blocks
    assert "block-090" not in blocks


def test_blocks_in_period_inclusive_range():
    blocks = _blocks_in_period(_SAMPLE_LOG, "2026-05-23", "2026-05-27")
    assert "block-095" in blocks
    assert "block-097" in blocks
    assert "block-090" not in blocks


def test_extract_pattern_names():
    names = _extract_pattern_names(_SAMPLE_PATTERNS)
    assert any("velocity" in n.lower() for n in names)


def test_velocity_calculation():
    assert _velocity(7, 7) == pytest.approx(1.0)


def test_velocity_zero_days():
    assert _velocity(5, 0) is None


def test_forecast_calculation():
    assert _forecast(1.0, 7) == 7


def test_forecast_none_velocity():
    assert _forecast(None) is None


# ---------------------------------------------------------------------------
# Tests: generate_weekly_report
# ---------------------------------------------------------------------------

def test_generate_returns_weekly_report():
    report = generate_weekly_report(
        now_ts=_NOW_TS, days=7,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        patterns_content=_SAMPLE_PATTERNS,
        stale_tools=[],
    )
    assert isinstance(report, WeeklyReport)


def test_generate_period_dates():
    report = generate_weekly_report(
        now_ts=_NOW_TS, days=7,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        patterns_content="",
        stale_tools=[],
    )
    assert report.period_end == "2026-05-27"
    assert report.period_start == "2026-05-20"


def test_generate_blocks_closed_count():
    report = generate_weekly_report(
        now_ts=_NOW_TS, days=7,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        patterns_content="",
        stale_tools=[],
    )
    # BLOCK_LOG has blocks from 2026-05-21 onwards; window is 2026-05-20 to 2026-05-27
    assert len(report.blocks_closed) >= 3


def test_generate_velocity_positive():
    report = generate_weekly_report(
        now_ts=_NOW_TS, days=7,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        patterns_content="",
        stale_tools=[],
    )
    assert report.velocity_blocks_per_day is not None
    assert report.velocity_blocks_per_day > 0


def test_generate_current_phase():
    report = generate_weekly_report(
        now_ts=_NOW_TS, days=7,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        patterns_content="",
        stale_tools=[],
    )
    assert report.current_phase == "16"


def test_generate_next_action_from_next_md():
    report = generate_weekly_report(
        now_ts=_NOW_TS, days=7,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        patterns_content="",
        stale_tools=[],
    )
    assert report.next_action == "start-block-104"


def test_generate_stale_tools_counted():
    from tools_registry import ToolEntry
    from master_scheduler import StaleTool, URGENCY_CRITICAL, _NEVER_RUN_DAYS
    fake_stale = [StaleTool(
        tool_id="audit", tool_name="Audit", urgency=URGENCY_CRITICAL,
        days_overdue=3.0, days_since_last_run=_NEVER_RUN_DAYS,
        recommended_interval_days=1.0, priority="high",
        command="bash audit.sh", message="critical",
    )]
    report = generate_weekly_report(
        now_ts=_NOW_TS, days=7,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        patterns_content="",
        stale_tools=fake_stale,
    )
    assert report.stale_tool_count == 1
    assert "audit" in report.critical_tool_ids


def test_generate_forecast_positive():
    report = generate_weekly_report(
        now_ts=_NOW_TS, days=7,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        patterns_content="",
        stale_tools=[],
    )
    assert report.forecast_blocks_next_7d is not None
    assert report.forecast_blocks_next_7d >= 0


# ---------------------------------------------------------------------------
# Tests: render_html
# ---------------------------------------------------------------------------

def test_render_html_is_standalone():
    report = WeeklyReport(
        period_start="2026-05-20", period_end="2026-05-27",
        generated_at=_NOW_TS, current_phase="16", next_action="start-block-104",
    )
    html = render_html(report)
    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "</html>" in html


def test_render_html_no_cdn():
    report = WeeklyReport(
        period_start="2026-05-20", period_end="2026-05-27",
        generated_at=_NOW_TS, current_phase="16", next_action="start-block-104",
    )
    html = render_html(report)
    assert "cdn" not in html.lower()
    assert "googleapis" not in html.lower()
    assert "cloudflare" not in html.lower()


def test_render_html_contains_dates():
    report = WeeklyReport(
        period_start="2026-05-20", period_end="2026-05-27",
        generated_at=_NOW_TS, current_phase="16", next_action="start-block-104",
    )
    html = render_html(report)
    assert "2026-05-20" in html
    assert "2026-05-27" in html


def test_render_html_contains_next_action():
    report = WeeklyReport(
        period_start="2026-05-20", period_end="2026-05-27",
        generated_at=_NOW_TS, current_phase="16", next_action="start-block-104",
    )
    html = render_html(report)
    assert "start-block-104" in html


# ---------------------------------------------------------------------------
# Tests: write_report
# ---------------------------------------------------------------------------

def test_write_report_creates_file(tmp_path):
    report = WeeklyReport(
        period_start="2026-05-20", period_end="2026-05-27",
        generated_at=_NOW_TS, current_phase="16", next_action="x",
    )
    path = write_report(report, arch_root=str(tmp_path))
    assert path.exists()
    assert "weekly-2026-05-27" in path.name


def test_write_report_in_correct_dir(tmp_path):
    report = WeeklyReport(
        period_start="2026-05-20", period_end="2026-05-27",
        generated_at=_NOW_TS, current_phase="16", next_action="x",
    )
    path = write_report(report, arch_root=str(tmp_path))
    assert "governance" in str(path)
    assert "reports" in str(path)
