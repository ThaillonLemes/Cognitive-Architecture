# sdk/tests/test_calendar_manager.py
# PURPOSE: Validate calendar_manager: add/list/remove meetings, recurring expansion,
#          today's alerts with countdown, multi-day upcoming alerts.
# BLOCK:   block-175

from __future__ import annotations

import re
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


def _make_arch(tmp: str) -> Path:
    arch = Path(tmp) / "arch"
    (arch / "governance").mkdir(parents=True)
    return arch


def _tomorrow() -> str:
    return (date.today() + timedelta(days=1)).isoformat()


def _in_3_days() -> str:
    return (date.today() + timedelta(days=3)).isoformat()


def _today() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Add / list / remove
# ---------------------------------------------------------------------------

def test_add_meeting():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        from calendar_manager import add_meeting, _read_calendar
        add_meeting(arch, _tomorrow(), "14:00", 2.0, "sync semanal")
        meetings = _read_calendar(arch)
        assert len(meetings) == 1
        assert meetings[0].desc == "sync semanal"
        assert meetings[0].duration_hours == 2.0


def test_list_meetings():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        from calendar_manager import add_meeting, list_meetings
        add_meeting(arch, _tomorrow(), "14:00", 1.0, "meeting A")
        add_meeting(arch, _in_3_days(), "10:00", 0.5, "meeting B")
        meetings = list_meetings(arch, horizon_days=7)
        assert len(meetings) >= 2


def test_remove_meeting():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        from calendar_manager import add_meeting, remove_meeting, _read_calendar
        add_meeting(arch, _tomorrow(), "14:00", 2.0, "sync semanal")
        removed = remove_meeting(arch, _tomorrow(), "sync")
        assert removed is True
        meetings = _read_calendar(arch)
        assert len(meetings) == 0


def test_add_meeting_cli():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        import io, contextlib
        from calendar_manager import main
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ret = main(["--add-meeting", f"{_tomorrow()} 09:00 1h daily standup",
                        "--arch-root", str(arch)])
        assert ret == 0
        assert "Added" in buf.getvalue()


# ---------------------------------------------------------------------------
# Recurring expansion
# ---------------------------------------------------------------------------

def test_weekly_recurring_expands():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        from calendar_manager import add_meeting, list_meetings
        # Add weekly meeting starting tomorrow
        add_meeting(arch, _tomorrow(), "14:00", 1.0, "weekly sync", recurring="weekly")
        meetings = list_meetings(arch, horizon_days=30)
        # Should have ~4 occurrences in 30 days
        weekly = [m for m in meetings if "weekly sync" in m.desc]
        assert len(weekly) >= 3


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

def test_upcoming_alerts():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        from calendar_manager import add_meeting, get_upcoming_alerts
        add_meeting(arch, _tomorrow(), "10:00", 1.0, "1:1 com senior")
        alerts = get_upcoming_alerts(arch, days=2)
        assert len(alerts) == 1
        assert "1:1" in alerts[0]
        assert "Amanhã" in alerts[0]


def test_no_meetings_no_alerts():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        from calendar_manager import get_today_alerts, get_upcoming_alerts
        assert get_today_alerts(arch) == []
        assert get_upcoming_alerts(arch) == []


def test_empty_calendar_created():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        # Run list on empty calendar — should not crash
        import io, contextlib
        from calendar_manager import main
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ret = main(["--list", "--arch-root", str(arch)])
        assert ret == 0


def test_pilot_calendar_yaml_exists():
    """The initial pilot-calendar.yaml must exist in governance/."""
    cal = ROOT / "governance" / "pilot-calendar.yaml"
    assert cal.exists(), "pilot-calendar.yaml not created"
    text = cal.read_text(encoding="utf-8")
    assert "meetings:" in text


if __name__ == "__main__":
    test_add_meeting()
    test_list_meetings()
    test_remove_meeting()
    test_add_meeting_cli()
    test_weekly_recurring_expands()
    test_upcoming_alerts()
    test_no_meetings_no_alerts()
    test_empty_calendar_created()
    test_pilot_calendar_yaml_exists()
    print("All block-175 tests passed.")
