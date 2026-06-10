# PURPOSE: Tests for calendar → notification integration (block-178)
# INPUTS:  tmp_path, synthetic pilot-calendar.yaml, governance/notifications.md
# OUTPUTS: assertions on meeting notification creation and priority
# DEPS:    pytest, calendar_manager, notification_manager, session_start
# SEE:     sdk/calendar_manager.py, sdk/session_start.py, block-178

import sys
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
from unittest.mock import patch

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from calendar_manager import get_today_meetings_with_times, _write_calendar, Meeting
from session_start import _create_calendar_notifications
from notification_manager import Governor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_env(tmp_path: Path) -> Path:
    """Create minimal env with governance/ dir."""
    gov_dir = tmp_path / "governance"
    gov_dir.mkdir(parents=True)
    (gov_dir / "notifications.md").write_text(
        "---\nnotifications: []\n---\n", encoding="utf-8"
    )
    (gov_dir / "notifications-archive.md").write_text(
        "---\nnotifications_archive: []\n---\n", encoding="utf-8"
    )
    return tmp_path


def _add_meeting(arch_root: Path, minutes_from_now: int, desc: str = "sync") -> None:
    """Add a meeting at now + minutes_from_now to the calendar."""
    now = datetime.now(timezone.utc)
    meeting_dt = now + timedelta(minutes=minutes_from_now)
    _write_calendar(arch_root, [
        Meeting(
            date=meeting_dt.strftime("%Y-%m-%d"),
            time=meeting_dt.strftime("%H:%M"),
            duration_hours=1.0,
            desc=desc,
        )
    ])


# ---------------------------------------------------------------------------
# get_today_meetings_with_times
# ---------------------------------------------------------------------------

class TestGetTodayMeetingsWithTimes:
    def test_returns_empty_when_no_calendar(self, tmp_path):
        result = get_today_meetings_with_times(tmp_path)
        assert result == []

    def test_returns_meeting_today(self, tmp_path):
        root = _make_env(tmp_path)
        _add_meeting(root, minutes_from_now=60, desc="daily standup")
        result = get_today_meetings_with_times(root)
        assert len(result) == 1
        assert result[0]["desc"] == "daily standup"
        assert result[0]["is_past"] is False

    def test_minutes_remaining_is_positive_for_future(self, tmp_path):
        root = _make_env(tmp_path)
        _add_meeting(root, minutes_from_now=90)
        result = get_today_meetings_with_times(root)
        # Allow ±5 min tolerance for test execution time
        assert 80 <= result[0]["minutes_remaining"] <= 100

    def test_is_past_for_past_meeting(self, tmp_path):
        root = _make_env(tmp_path)
        _add_meeting(root, minutes_from_now=-30)
        result = get_today_meetings_with_times(root)
        assert len(result) == 1
        assert result[0]["is_past"] is True

    def test_alert_str_is_non_empty(self, tmp_path):
        root = _make_env(tmp_path)
        _add_meeting(root, minutes_from_now=45, desc="client review")
        result = get_today_meetings_with_times(root)
        assert len(result[0]["alert_str"]) > 0
        assert "client review" in result[0]["alert_str"]


# ---------------------------------------------------------------------------
# _create_calendar_notifications priority rules
# ---------------------------------------------------------------------------

class TestCalendarNotificationPriority:
    def test_imminent_meeting_under_10min_creates_critical(self, tmp_path):
        root = _make_env(tmp_path)
        _add_meeting(root, minutes_from_now=5, desc="urgent call")
        _create_calendar_notifications(root)
        items = Governor(root).list(pending_only=False)
        assert any(n.priority == "critical" and "urgent call" in n.message for n in items)

    def test_meeting_under_5h_creates_high(self, tmp_path):
        root = _make_env(tmp_path)
        _add_meeting(root, minutes_from_now=120, desc="planning")
        _create_calendar_notifications(root)
        items = Governor(root).list(pending_only=False)
        assert any(n.priority == "high" and "planning" in n.message for n in items)

    def test_meeting_over_5h_creates_medium(self, tmp_path):
        root = _make_env(tmp_path)
        _add_meeting(root, minutes_from_now=360, desc="end of day review")
        _create_calendar_notifications(root)
        items = Governor(root).list(pending_only=False)
        assert any(n.priority == "medium" and "end of day review" in n.message for n in items)

    def test_past_meeting_creates_no_notification(self, tmp_path):
        root = _make_env(tmp_path)
        _add_meeting(root, minutes_from_now=-60, desc="already done")
        _create_calendar_notifications(root)
        assert Governor(root).list(pending_only=False) == []

    def test_no_meetings_creates_no_notification(self, tmp_path):
        root = _make_env(tmp_path)
        _create_calendar_notifications(root)
        assert Governor(root).list(pending_only=False) == []

    def test_does_not_raise_when_no_governance_dir(self, tmp_path):
        """Must be resilient to missing governance/ directory."""
        _create_calendar_notifications(tmp_path)
