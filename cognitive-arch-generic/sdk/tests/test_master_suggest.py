# cognitive-arch / sdk/tests/test_master_suggest.py
# purpose: Unit tests for sdk/master_suggest.py
# stdlib-only; no external dependencies

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools_registry import ToolEntry
from master_suggest import (
    Suggestion,
    suggest_at_session_start,
    suggest_inline,
    suggest_on_demand,
    render_suggestions,
    session_start_block,
    inline_block,
    _INLINE_MAX,
)
from master_scheduler import URGENCY_CRITICAL, URGENCY_VERY_OVERDUE, URGENCY_OVERDUE

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)


def _entry(
    id="audit",
    trigger_type="time",
    priority="high",
    interval=1.0,
    last_run="never",
) -> ToolEntry:
    return ToolEntry(
        id=id, name=f"{id}-name", command=f"run {id}", description="test",
        recommended_interval_days=interval,
        trigger_type=trigger_type,
        priority=priority,
        last_run=last_run,
    )


def _fresh(id="fresh", interval=1.0) -> ToolEntry:
    """Tool that ran 1 hour ago — not stale."""
    ts = (_NOW - timedelta(hours=1)).isoformat()
    return _entry(id=id, interval=interval, last_run=ts)


def _overdue(id="overdue-t", priority="medium", interval=1.0) -> ToolEntry:
    """Tool past recommended interval (1.5× overdue)."""
    ts = (_NOW - timedelta(hours=36)).isoformat()
    return _entry(id=id, priority=priority, interval=interval, last_run=ts)


def _very_overdue(id="very-t", priority="medium", interval=1.0) -> ToolEntry:
    """Tool past 2× interval."""
    ts = (_NOW - timedelta(hours=60)).isoformat()
    return _entry(id=id, priority=priority, interval=interval, last_run=ts)


def _critical(id="crit-t", interval=1.0) -> ToolEntry:
    """Tool past 3× interval with high priority."""
    ts = (_NOW - timedelta(hours=96)).isoformat()
    return _entry(id=id, priority="high", interval=interval, last_run=ts)


# ---------------------------------------------------------------------------
# Tests: suggest_at_session_start
# ---------------------------------------------------------------------------

def test_session_start_no_stale_empty():
    registry = [_fresh("a"), _fresh("b")]
    result = suggest_at_session_start(now_dt=_NOW, registry=registry)
    assert result == []


def test_session_start_returns_all_stale():
    registry = [_overdue("t1"), _very_overdue("t2"), _critical("t3")]
    result = suggest_at_session_start(now_dt=_NOW, registry=registry)
    assert len(result) == 3


def test_session_start_critical_first():
    registry = [_overdue("t1", priority="medium"), _critical("t3")]
    result = suggest_at_session_start(now_dt=_NOW, registry=registry)
    assert result[0].urgency == URGENCY_CRITICAL


def test_session_start_suggestion_has_all_fields():
    registry = [_critical()]
    result = suggest_at_session_start(now_dt=_NOW, registry=registry)
    s = result[0]
    assert s.tool_id
    assert s.tool_name
    assert s.urgency
    assert s.message
    assert s.action_button_label
    assert s.command
    assert s.source == "session_start"


def test_session_start_excludes_event_tools():
    registry = [
        ToolEntry(id="dep", name="dep", command="x", description="x",
                  recommended_interval_days=0, trigger_type="event",
                  priority="high", last_run="never"),
    ]
    result = suggest_at_session_start(now_dt=_NOW, registry=registry)
    assert result == []


# ---------------------------------------------------------------------------
# Tests: suggest_inline
# ---------------------------------------------------------------------------

def test_inline_empty_when_no_critical():
    registry = [_overdue("t1", priority="medium"), _very_overdue("t2", priority="medium")]
    result = suggest_inline(block_id="block-101", now_dt=_NOW, registry=registry)
    assert result == []


def test_inline_returns_critical_only():
    registry = [_critical("c1"), _overdue("o1"), _very_overdue("v1")]
    result = suggest_inline(block_id="block-101", now_dt=_NOW, registry=registry)
    assert all(s.urgency == URGENCY_CRITICAL for s in result)


def test_inline_max_two_suggestions():
    registry = [_critical("c1"), _critical("c2"), _critical("c3"), _critical("c4")]
    result = suggest_inline(block_id="block-101", now_dt=_NOW, registry=registry)
    assert len(result) <= _INLINE_MAX


def test_inline_source_is_inline():
    registry = [_critical()]
    result = suggest_inline(now_dt=_NOW, registry=registry)
    assert result[0].source == "inline"


def test_inline_accepts_none_block_id():
    registry = [_critical()]
    result = suggest_inline(block_id=None, now_dt=_NOW, registry=registry)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# Tests: suggest_on_demand
# ---------------------------------------------------------------------------

def test_on_demand_empty_when_all_fresh():
    registry = [_fresh("a"), _fresh("b")]
    result = suggest_on_demand(now_dt=_NOW, registry=registry)
    assert result == []


def test_on_demand_returns_all_stale():
    registry = [_overdue("t1"), _critical("t2")]
    result = suggest_on_demand(now_dt=_NOW, registry=registry)
    assert len(result) == 2


def test_on_demand_source_is_on_demand():
    registry = [_overdue("t1")]
    result = suggest_on_demand(now_dt=_NOW, registry=registry)
    assert result[0].source == "on_demand"


# ---------------------------------------------------------------------------
# Tests: render_suggestions
# ---------------------------------------------------------------------------

def test_render_no_suggestions():
    text = render_suggestions([])
    assert "✅" in text or "current" in text.lower()


def test_render_includes_tool_name():
    registry = [_critical("audit")]
    suggestions = suggest_at_session_start(now_dt=_NOW, registry=registry)
    text = render_suggestions(suggestions)
    assert "audit-name" in text or "audit" in text


def test_render_with_header():
    registry = [_critical()]
    suggestions = suggest_at_session_start(now_dt=_NOW, registry=registry)
    text = render_suggestions(suggestions, header="## Test Header")
    assert "## Test Header" in text


# ---------------------------------------------------------------------------
# Tests: convenience functions
# ---------------------------------------------------------------------------

def test_session_start_block_empty_string_when_no_stale():
    registry = [_fresh()]
    text = session_start_block(now_dt=_NOW, registry=registry)
    assert text == ""


def test_session_start_block_returns_text_when_stale():
    registry = [_critical()]
    text = session_start_block(now_dt=_NOW, registry=registry)
    assert text != ""
    assert "Master Agent" in text or "CRITICAL" in text


def test_inline_block_empty_string_when_no_critical():
    registry = [_overdue("t1", priority="medium")]
    text = inline_block(block_id="block-101", now_dt=_NOW, registry=registry)
    assert text == ""


def test_inline_block_returns_text_with_block_id():
    registry = [_critical()]
    text = inline_block(block_id="block-101", now_dt=_NOW, registry=registry)
    assert text != ""
    assert "block-101" in text
