# cognitive-arch / sdk/tests/test_master_scheduler.py
# purpose: Unit tests for sdk/master_scheduler.py
# stdlib-only; no external dependencies

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools_registry import ToolEntry
from master_scheduler import (
    StaleTool,
    check_schedule,
    format_report,
    _classify_urgency,
    _days_since,
    URGENCY_CRITICAL,
    URGENCY_VERY_OVERDUE,
    URGENCY_OVERDUE,
    _NEVER_RUN_DAYS,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)


def _entry(
    id="audit",
    trigger_type="time",
    priority="high",
    interval=1.0,
    last_run="never",
) -> ToolEntry:
    return ToolEntry(
        id=id, name=id, command=f"run {id}", description="test",
        recommended_interval_days=interval,
        trigger_type=trigger_type,
        priority=priority,
        last_run=last_run,
    )


# ---------------------------------------------------------------------------
# Tests: _days_since
# ---------------------------------------------------------------------------

def test_days_since_never():
    now = _now()
    assert _days_since("never", now) == _NEVER_RUN_DAYS


def test_days_since_one_day_ago():
    now = _now()
    one_day_ago = (now - timedelta(days=1)).isoformat()
    days = _days_since(one_day_ago, now)
    assert abs(days - 1.0) < 0.01


def test_days_since_naive_timestamp_treated_as_utc():
    now = _now()
    naive_ts = "2026-05-26T12:00:00"  # naive — treated as UTC
    days = _days_since(naive_ts, now)
    assert abs(days - 1.0) < 0.01


# ---------------------------------------------------------------------------
# Tests: _classify_urgency
# ---------------------------------------------------------------------------

def test_classify_not_stale():
    assert _classify_urgency(0.5, interval=1.0, priority="high") is None


def test_classify_overdue():
    assert _classify_urgency(1.5, interval=1.0, priority="medium") == URGENCY_OVERDUE


def test_classify_very_overdue():
    assert _classify_urgency(2.5, interval=1.0, priority="medium") == URGENCY_VERY_OVERDUE


def test_classify_critical_high_priority():
    assert _classify_urgency(3.5, interval=1.0, priority="high") == URGENCY_CRITICAL


def test_classify_not_critical_medium_priority():
    # 3.5× past interval but priority=medium → very_overdue (not critical)
    assert _classify_urgency(3.5, interval=1.0, priority="medium") == URGENCY_VERY_OVERDUE


# ---------------------------------------------------------------------------
# Tests: check_schedule
# ---------------------------------------------------------------------------

def test_no_stale_tools():
    now = _now()
    recent = (now - timedelta(hours=6)).isoformat()
    entries = [_entry(id="audit", interval=1.0, last_run=recent)]
    stale = check_schedule(now_dt=now, registry=entries)
    assert stale == []


def test_event_tool_excluded():
    now = _now()
    entries = [_entry(id="dep-check", trigger_type="event", last_run="never")]
    stale = check_schedule(now_dt=now, registry=entries)
    assert stale == []


def test_never_run_high_priority_is_critical():
    now = _now()
    entries = [_entry(id="audit", priority="high", interval=1.0, last_run="never")]
    stale = check_schedule(now_dt=now, registry=entries)
    assert len(stale) == 1
    assert stale[0].urgency == URGENCY_CRITICAL


def test_never_run_medium_priority_is_very_overdue():
    now = _now()
    entries = [_entry(id="pattern-mining", priority="medium", interval=7.0, last_run="never")]
    stale = check_schedule(now_dt=now, registry=entries)
    assert len(stale) == 1
    assert stale[0].urgency == URGENCY_VERY_OVERDUE


def test_overdue_tool_in_result():
    now = _now()
    # 1.5 days ago with 1-day interval → days_since=1.5 > 1 but < 2 → "overdue"
    one_and_half_days_ago = (now - timedelta(hours=36)).isoformat()
    entries = [_entry(id="audit", interval=1.0, last_run=one_and_half_days_ago, priority="medium")]
    stale = check_schedule(now_dt=now, registry=entries)
    assert len(stale) == 1
    assert stale[0].urgency == URGENCY_OVERDUE


def test_very_overdue_tool_in_result():
    now = _now()
    # 2.5 days ago with 1-day interval → days_since=2.5 > 2 → "very_overdue"
    two_and_half_days_ago = (now - timedelta(hours=60)).isoformat()
    entries = [_entry(id="audit", interval=1.0, last_run=two_and_half_days_ago, priority="medium")]
    stale = check_schedule(now_dt=now, registry=entries)
    assert len(stale) == 1
    assert stale[0].urgency == URGENCY_VERY_OVERDUE


def test_stale_tools_sorted_critical_first():
    now = _now()
    critical_ts = (now - timedelta(days=4)).isoformat()
    overdue_ts = (now - timedelta(days=1.5)).isoformat()
    entries = [
        _entry(id="tool-b", priority="medium", interval=1.0, last_run=overdue_ts),
        _entry(id="tool-a", priority="high", interval=1.0, last_run=critical_ts),
    ]
    stale = check_schedule(now_dt=now, registry=entries)
    assert stale[0].urgency == URGENCY_CRITICAL
    assert stale[0].tool_id == "tool-a"


def test_stale_tools_contains_expected_fields():
    now = _now()
    entries = [_entry(id="audit", interval=1.0, last_run="never")]
    stale = check_schedule(now_dt=now, registry=entries)
    s = stale[0]
    assert s.tool_id == "audit"
    assert s.recommended_interval_days == 1.0
    assert s.days_since_last_run == _NEVER_RUN_DAYS
    assert "CRITICAL" in s.message or "OVERDUE" in s.message or "VERY" in s.message


def test_mixed_tools_event_excluded():
    now = _now()
    entries = [
        _entry(id="audit", trigger_type="time", last_run="never", priority="high"),
        _entry(id="dep", trigger_type="event", last_run="never"),
    ]
    stale = check_schedule(now_dt=now, registry=entries)
    ids = [s.tool_id for s in stale]
    assert "dep" not in ids
    assert "audit" in ids


# ---------------------------------------------------------------------------
# Tests: format_report
# ---------------------------------------------------------------------------

def test_format_report_no_stale():
    assert "current" in format_report([]).lower() or "✅" in format_report([])


def test_format_report_shows_critical_emoji():
    stale = [StaleTool(
        tool_id="audit", tool_name="Audit", urgency=URGENCY_CRITICAL,
        days_overdue=3.0, days_since_last_run=4.0,
        recommended_interval_days=1.0, priority="high",
        command="bash audit.sh", message="[CRITICAL] audit",
    )]
    report = format_report(stale)
    assert "🔴" in report
    assert "audit" in report
