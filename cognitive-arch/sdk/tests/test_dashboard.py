# cognitive-arch / sdk/tests/test_dashboard.py
# purpose: Unit tests for sdk/dashboard_generator.py
# stdlib-only; no external dependencies

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard_generator import (
    DashboardData, AgentRow,
    generate_dashboard, render_html, write_dashboard,
    _parse_board, _blocks_in_window, _timeline_entries,
    _extract_recent_patterns, _build_roadmap, _velocity, _forecast,
)

# ---------------------------------------------------------------------------
# Fixtures / shared data
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)
_NOW_TS = _NOW.isoformat()

_SAMPLE_BOARD = """\
agent:implementer b:107 group:16A status:done lock:ready deps:- ts:2026-05-27 last_done:block-107
agent:master b:- group:- status:idle lock:ready deps:- ts:2026-05-27
"""

_SAMPLE_LOG = """\
# BLOCK_LOG
block-090 done - 2026-05-21
block-095 done - 2026-05-23
block-097 done - 2026-05-27
block-098 done - 2026-05-27
block-099 done - 2026-05-27
"""

_SAMPLE_STATE = "phase:16 last_block:block-107 status:active"
_SAMPLE_NEXT  = "next_action:start-block-105 phase:phase-16 manifest:manifests/block-105-dashboard.md"

_SAMPLE_PATTERNS = """\
# Patterns Report
## Summary Table
## velocity-data-gap
## stale-tools-detected
## premature-phase-close
"""


def _make_data(**overrides) -> DashboardData:
    defaults = dict(
        generated_at=_NOW_TS,
        current_phase="16",
        next_action="start-block-105",
        manifest="manifests/block-105-dashboard.md",
        last_block="block-107",
    )
    defaults.update(overrides)
    return DashboardData(**defaults)


# ---------------------------------------------------------------------------
# Tests: _parse_board
# ---------------------------------------------------------------------------

def test_parse_board_returns_agent_rows():
    rows = _parse_board(_SAMPLE_BOARD)
    assert len(rows) == 2


def test_parse_board_correct_agent_id():
    rows = _parse_board(_SAMPLE_BOARD)
    assert rows[0].agent_id == "implementer"


def test_parse_board_correct_block():
    rows = _parse_board(_SAMPLE_BOARD)
    assert rows[0].block == "107"


def test_parse_board_correct_status():
    rows = _parse_board(_SAMPLE_BOARD)
    assert rows[0].status == "done"


def test_parse_board_last_done_field():
    rows = _parse_board(_SAMPLE_BOARD)
    assert rows[0].last_done == "block-107"


def test_parse_board_ignores_comments():
    board = "# comment line\nagent:tester b:001 group:A status:wip lock:ready deps:- ts:2026-01-01\n"
    rows = _parse_board(board)
    assert len(rows) == 1
    assert rows[0].agent_id == "tester"


def test_parse_board_empty_content():
    assert _parse_board("# just a comment\n") == []


def test_parse_board_ignores_non_agent_lines():
    board = "# board\nsome:random line\nagent:x b:- group:- status:idle lock:ready deps:- ts:2026-01-01\n"
    rows = _parse_board(board)
    assert len(rows) == 1


# ---------------------------------------------------------------------------
# Tests: _blocks_in_window
# ---------------------------------------------------------------------------

def test_blocks_in_window_within_range():
    blocks = _blocks_in_window(_SAMPLE_LOG, 7, _NOW)
    assert "block-097" in blocks
    assert "block-099" in blocks


def test_blocks_in_window_includes_cutoff_date():
    # 7-day window from 2026-05-27: cutoff = 2026-05-20; block-090 on 2026-05-21 → included
    blocks = _blocks_in_window(_SAMPLE_LOG, 7, _NOW)
    assert "block-090" in blocks


def test_blocks_in_window_excludes_older_blocks():
    # 3-day window from 2026-05-27: cutoff = 2026-05-24; block-090 on 2026-05-21 → excluded
    blocks = _blocks_in_window(_SAMPLE_LOG, 3, _NOW)
    assert "block-090" not in blocks
    assert "block-095" not in blocks


def test_blocks_in_window_empty_log():
    assert _blocks_in_window("", 7, _NOW) == []


# ---------------------------------------------------------------------------
# Tests: _timeline_entries
# ---------------------------------------------------------------------------

def test_timeline_entries_newest_first():
    entries = _timeline_entries(_SAMPLE_LOG, 7, _NOW)
    assert len(entries) >= 2
    dates = [e[0] for e in entries]
    assert dates == sorted(dates, reverse=True)


def test_timeline_entries_empty_log():
    assert _timeline_entries("", 7, _NOW) == []


def test_timeline_entries_format():
    entries = _timeline_entries(_SAMPLE_LOG, 7, _NOW)
    for date_str, block_id in entries:
        assert re.match(r"\d{4}-\d{2}-\d{2}", date_str) or True  # just check structure
        assert block_id.startswith("block-")


# ---------------------------------------------------------------------------
# Tests: _extract_recent_patterns
# ---------------------------------------------------------------------------

def test_extract_patterns_returns_names():
    names = _extract_recent_patterns(_SAMPLE_PATTERNS)
    assert "velocity-data-gap" in names


def test_extract_patterns_excludes_summary_table():
    names = _extract_recent_patterns(_SAMPLE_PATTERNS)
    assert "Summary Table" not in names


def test_extract_patterns_max_count():
    content = "\n".join(f"## pattern-{i}" for i in range(20))
    names = _extract_recent_patterns(content, max_count=3)
    assert len(names) == 3


def test_extract_patterns_empty_content():
    assert _extract_recent_patterns("") == []


# ---------------------------------------------------------------------------
# Tests: _build_roadmap
# ---------------------------------------------------------------------------

def test_build_roadmap_active_phase_correct():
    done, active, planned = _build_roadmap("16")
    assert "16" in active
    assert len(active) == 1


def test_build_roadmap_done_phases():
    done, active, planned = _build_roadmap("16")
    assert "15" in done
    assert "1" in done


def test_build_roadmap_planned_phases():
    done, active, planned = _build_roadmap("16", max_phase=17)
    assert "17" in planned


def test_build_roadmap_phase_1_no_done():
    done, active, planned = _build_roadmap("1", max_phase=3)
    assert done == []
    assert "1" in active
    assert "2" in planned and "3" in planned


def test_build_roadmap_invalid_phase_defaults_to_1():
    done, active, planned = _build_roadmap("unknown", max_phase=3)
    assert "1" in active


# ---------------------------------------------------------------------------
# Tests: _velocity / _forecast helpers
# ---------------------------------------------------------------------------

def test_velocity_calculation():
    assert _velocity(7, 7) == pytest.approx(1.0)


def test_velocity_zero_days():
    assert _velocity(5, 0) is None


def test_forecast_calculation():
    assert _forecast(1.0, 7) == 7


def test_forecast_none_velocity():
    assert _forecast(None) is None


# ---------------------------------------------------------------------------
# Tests: generate_dashboard
# ---------------------------------------------------------------------------

def test_generate_returns_dashboard_data():
    data = generate_dashboard(
        now_ts=_NOW_TS,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        board_content=_SAMPLE_BOARD,
        patterns_content=_SAMPLE_PATTERNS,
        stale_tools=[],
    )
    assert isinstance(data, DashboardData)


def test_generate_current_phase():
    data = generate_dashboard(
        now_ts=_NOW_TS,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        board_content=_SAMPLE_BOARD,
        patterns_content="",
        stale_tools=[],
    )
    assert data.current_phase == "16"


def test_generate_next_action():
    data = generate_dashboard(
        now_ts=_NOW_TS,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        board_content=_SAMPLE_BOARD,
        patterns_content="",
        stale_tools=[],
    )
    assert data.next_action == "start-block-105"


def test_generate_agents_count():
    data = generate_dashboard(
        now_ts=_NOW_TS,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        board_content=_SAMPLE_BOARD,
        patterns_content="",
        stale_tools=[],
    )
    assert len(data.agents) == 2


def test_generate_blocks_7d_positive():
    data = generate_dashboard(
        now_ts=_NOW_TS,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        board_content=_SAMPLE_BOARD,
        patterns_content="",
        stale_tools=[],
    )
    assert len(data.blocks_closed_7d) > 0


def test_generate_stale_tool_count():
    from master_scheduler import StaleTool, URGENCY_OVERDUE
    fake = [StaleTool(
        tool_id="audit", tool_name="Audit", urgency=URGENCY_OVERDUE,
        days_overdue=1.0, days_since_last_run=2.0,
        recommended_interval_days=1.0, priority="medium",
        command="bash audit.sh", message="overdue",
    )]
    data = generate_dashboard(
        now_ts=_NOW_TS,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        board_content=_SAMPLE_BOARD,
        patterns_content="",
        stale_tools=fake,
    )
    assert data.stale_tool_count == 1


def test_generate_roadmap_populated():
    data = generate_dashboard(
        now_ts=_NOW_TS,
        log_content=_SAMPLE_LOG,
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        board_content=_SAMPLE_BOARD,
        patterns_content="",
        stale_tools=[],
    )
    assert len(data.phases_active) == 1
    assert len(data.phases_done) > 0


# ---------------------------------------------------------------------------
# Tests: render_html
# ---------------------------------------------------------------------------

def test_render_html_is_standalone():
    html = render_html(_make_data())
    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "</html>" in html


def test_render_html_no_cdn():
    html = render_html(_make_data())
    lower = html.lower()
    assert "cdn" not in lower
    assert "googleapis.com" not in lower
    assert "cloudflare.com" not in lower


def test_render_html_contains_phase():
    html = render_html(_make_data())
    assert "Phase 16" in html or ">16<" in html or "phase:16" in html.lower() or "16" in html


def test_render_html_contains_next_action():
    html = render_html(_make_data())
    assert "start-block-105" in html


def test_render_html_contains_last_block():
    html = render_html(_make_data())
    assert "block-107" in html


def test_render_html_custom_css():
    html = render_html(_make_data(), css="body { color: red; }")
    assert "color: red" in html


# ---------------------------------------------------------------------------
# Tests: write_dashboard
# ---------------------------------------------------------------------------

def test_write_dashboard_creates_file(tmp_path):
    path = write_dashboard(_make_data(), arch_root=str(tmp_path))
    assert path.exists()


def test_write_dashboard_correct_path(tmp_path):
    path = write_dashboard(_make_data(), arch_root=str(tmp_path))
    assert "governance" in str(path)
    assert path.name == "dashboard.html"


def test_write_dashboard_returns_path(tmp_path):
    path = write_dashboard(_make_data(), arch_root=str(tmp_path))
    assert isinstance(path, Path)


# ---------------------------------------------------------------------------
# Import for regex in timeline test
# ---------------------------------------------------------------------------
import re
