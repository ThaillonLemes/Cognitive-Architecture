# cognitive-arch / sdk/tests/test_briefing_generator.py
# purpose: Unit tests for sdk/briefing_generator.py
# stdlib-only; no external dependencies

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from briefing_generator import (
    PostPauseBriefing,
    should_brief,
    generate_briefing,
    render_markdown,
    render_html,
    DEFAULT_PAUSE_THRESHOLD_HOURS,
    MAX_BRIEFING_LINES,
    _parse_block_log_since,
    _parse_kv,
)
from master_scheduler import URGENCY_CRITICAL, URGENCY_OVERDUE

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)


def _ts(dt: datetime) -> str:
    return dt.isoformat()


def _24h_ago() -> str:
    return _ts(_NOW - timedelta(hours=24.1))


def _recent() -> str:
    return _ts(_NOW - timedelta(hours=6))


_SAMPLE_STATE = (
    "p:15 status:active phase:15 last_block:block-101 last_block_status:done "
    "next:block-103 governor_mode:manual"
)
_SAMPLE_NEXT = (
    "status:active next_action:start-block-103 phase:phase-16 "
    "manifest:manifests/block-103-briefing-generator.md"
)
_SAMPLE_LOG = """
# BLOCK_LOG
block-098 done - 2026-05-27
block-099 done - 2026-05-27
block-100 done - 2026-05-27
block-101 done - 2026-05-27
block-102 done - 2026-05-27
"""


# ---------------------------------------------------------------------------
# Tests: should_brief
# ---------------------------------------------------------------------------

def test_should_brief_below_threshold():
    assert should_brief(_recent(), threshold_hours=24, now_dt=_NOW) is False


def test_should_brief_above_threshold():
    assert should_brief(_24h_ago(), threshold_hours=24, now_dt=_NOW) is True


def test_should_brief_exactly_at_threshold_is_false():
    exactly = _ts(_NOW - timedelta(hours=24))
    assert should_brief(exactly, threshold_hours=24, now_dt=_NOW) is False


def test_should_brief_long_pause():
    week_ago = _ts(_NOW - timedelta(days=7))
    assert should_brief(week_ago, threshold_hours=24, now_dt=_NOW) is True


def test_should_brief_invalid_timestamp():
    assert should_brief("not-a-date", threshold_hours=24, now_dt=_NOW) is False


# ---------------------------------------------------------------------------
# Tests: _parse_block_log_since
# ---------------------------------------------------------------------------

def test_parse_log_since_returns_correct_blocks():
    blocks = _parse_block_log_since(_SAMPLE_LOG, since_date="2026-05-27")
    assert "block-098" in blocks
    assert "block-099" in blocks


def test_parse_log_since_excludes_old_blocks():
    log = "block-050 done - 2026-05-22\nblock-098 done - 2026-05-27\n"
    blocks = _parse_block_log_since(log, since_date="2026-05-27")
    assert "block-050" not in blocks
    assert "block-098" in blocks


def test_parse_log_since_ignores_comments():
    log = "# header comment\nblock-001 done - 2026-05-27\n"
    blocks = _parse_block_log_since(log, since_date="2026-05-27")
    assert "block-001" in blocks


def test_parse_kv_extracts_phase():
    state = _parse_kv(_SAMPLE_STATE)
    assert state.get("phase") == "15"


def test_parse_kv_extracts_next_action():
    nxt = _parse_kv(_SAMPLE_NEXT)
    assert nxt.get("next_action") == "start-block-103"


# ---------------------------------------------------------------------------
# Tests: generate_briefing
# ---------------------------------------------------------------------------

def test_generate_returns_none_when_recent():
    result = generate_briefing(
        last_active_ts=_recent(),
        now_ts=_ts(_NOW),
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        log_content=_SAMPLE_LOG,
        stale_tools=[],
    )
    assert result is None


def test_generate_returns_briefing_when_overdue():
    result = generate_briefing(
        last_active_ts=_24h_ago(),
        now_ts=_ts(_NOW),
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        log_content=_SAMPLE_LOG,
        stale_tools=[],
    )
    assert result is not None
    assert isinstance(result, PostPauseBriefing)


def test_generate_pause_hours_correct():
    result = generate_briefing(
        last_active_ts=_ts(_NOW - timedelta(hours=48)),
        now_ts=_ts(_NOW),
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        log_content=_SAMPLE_LOG,
        stale_tools=[],
    )
    assert abs(result.pause_hours - 48.0) < 0.2


def test_generate_blocks_closed_since_populated():
    result = generate_briefing(
        last_active_ts=_24h_ago(),
        now_ts=_ts(_NOW),
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        log_content=_SAMPLE_LOG,
        stale_tools=[],
    )
    assert len(result.blocks_closed_since) > 0


def test_generate_next_action_from_next_md():
    result = generate_briefing(
        last_active_ts=_24h_ago(),
        now_ts=_ts(_NOW),
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        log_content=_SAMPLE_LOG,
        stale_tools=[],
    )
    assert result.next_action == "start-block-103"


def test_generate_critical_tools_extracted():
    from tools_registry import ToolEntry
    from master_scheduler import StaleTool, URGENCY_CRITICAL, _NEVER_RUN_DAYS

    fake_stale = [StaleTool(
        tool_id="audit", tool_name="Audit", urgency=URGENCY_CRITICAL,
        days_overdue=3.0, days_since_last_run=_NEVER_RUN_DAYS,
        recommended_interval_days=1.0, priority="high",
        command="bash audit.sh", message="[CRITICAL] audit",
    )]
    result = generate_briefing(
        last_active_ts=_24h_ago(),
        now_ts=_ts(_NOW),
        state_content=_SAMPLE_STATE,
        next_content=_SAMPLE_NEXT,
        log_content=_SAMPLE_LOG,
        stale_tools=fake_stale,
    )
    assert "audit" in result.critical_tools
    assert result.stale_tools_count == 1


# ---------------------------------------------------------------------------
# Tests: render_markdown
# ---------------------------------------------------------------------------

def test_render_markdown_within_line_cap():
    briefing = PostPauseBriefing(
        pause_hours=48.0, last_active_ts=_24h_ago(), generated_at=_ts(_NOW),
        current_phase="16", next_action="start-block-103", last_block="block-101",
        blocks_closed_since=["block-098", "block-099"],
        stale_tools_count=2, critical_tools=["audit"],
    )
    md = render_markdown(briefing)
    lines = [l for l in md.splitlines() if l.strip()]
    assert len(lines) <= MAX_BRIEFING_LINES


def test_render_markdown_contains_phase():
    briefing = PostPauseBriefing(
        pause_hours=24.5, last_active_ts=_24h_ago(), generated_at=_ts(_NOW),
        current_phase="16", next_action="start-block-103", last_block="block-101",
    )
    md = render_markdown(briefing)
    assert "16" in md


def test_render_markdown_contains_next_action():
    briefing = PostPauseBriefing(
        pause_hours=24.5, last_active_ts=_24h_ago(), generated_at=_ts(_NOW),
        current_phase="16", next_action="start-block-103", last_block="block-101",
    )
    md = render_markdown(briefing)
    assert "start-block-103" in md


def test_render_markdown_days_format_for_long_pause():
    briefing = PostPauseBriefing(
        pause_hours=72.0, last_active_ts=_ts(_NOW - timedelta(days=3)),
        generated_at=_ts(_NOW), current_phase="16",
        next_action="x", last_block="block-101",
    )
    md = render_markdown(briefing)
    assert "day" in md.lower()


# ---------------------------------------------------------------------------
# Tests: render_html
# ---------------------------------------------------------------------------

def test_render_html_is_html():
    briefing = PostPauseBriefing(
        pause_hours=24.5, last_active_ts=_24h_ago(), generated_at=_ts(_NOW),
        current_phase="16", next_action="start-block-103", last_block="block-101",
    )
    html = render_html(briefing)
    assert "<!DOCTYPE html>" in html
    assert "<html>" in html
    assert "</html>" in html


def test_render_html_contains_content():
    briefing = PostPauseBriefing(
        pause_hours=24.5, last_active_ts=_24h_ago(), generated_at=_ts(_NOW),
        current_phase="16", next_action="start-block-103", last_block="block-101",
    )
    html = render_html(briefing)
    assert "16" in html
