# PURPOSE: Tests for notification_manager.surface() — block-179
# INPUTS:  tmp_path, synthetic notifications.md
# OUTPUTS: assertions on surfacing behavior at trigger checkpoints
# DEPS:    pytest, notification_manager
# SEE:     sdk/notification_manager.py, block-179

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from notification_manager import (
    Governor,
    surface,
    TRIGGER_SESSION_START,
    TRIGGER_PHASE_CLOSE,
    TRIGGER_BLOCK_CLOSE,
    TRIGGER_SCAN_COMPLETE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_env(tmp_path: Path) -> Path:
    gov_dir = tmp_path / "governance"
    gov_dir.mkdir(parents=True)
    (gov_dir / "notifications.md").write_text(
        "---\nnotifications: []\n---\n", encoding="utf-8"
    )
    (gov_dir / "notifications-archive.md").write_text(
        "---\nnotifications_archive: []\n---\n", encoding="utf-8"
    )
    return tmp_path


def _add_notification(root: Path, message: str, priority: str = "high") -> str:
    gov = Governor(root)
    return gov.add(message, type_="health", priority=priority)


# ---------------------------------------------------------------------------
# surface() basic behavior
# ---------------------------------------------------------------------------

class TestSurface:
    def test_returns_empty_when_no_pending(self, tmp_path):
        root = _make_env(tmp_path)
        result = surface(TRIGGER_SESSION_START, root)
        assert result == []

    def test_returns_surfaced_notifications(self, tmp_path):
        root = _make_env(tmp_path)
        _add_notification(root, "audit degraded", priority="high")
        result = surface(TRIGGER_SESSION_START, root)
        assert len(result) == 1
        assert result[0].message == "audit degraded"

    def test_marks_notifications_as_seen(self, tmp_path):
        root = _make_env(tmp_path)
        _add_notification(root, "health critical", priority="critical")
        surface(TRIGGER_PHASE_CLOSE, root)
        items = Governor(root).list(pending_only=True)
        assert items == []  # no longer pending after surface

    def test_second_surface_returns_empty(self, tmp_path):
        """After surfacing once, same notifications are no longer pending."""
        root = _make_env(tmp_path)
        _add_notification(root, "some warning")
        surface(TRIGGER_BLOCK_CLOSE, root)
        result = surface(TRIGGER_SCAN_COMPLETE, root)
        assert result == []

    def test_surfaces_sorted_by_priority(self, tmp_path):
        root = _make_env(tmp_path)
        _add_notification(root, "low priority msg", priority="low")
        _add_notification(root, "critical msg", priority="critical")
        _add_notification(root, "high priority msg", priority="high")
        result = surface(TRIGGER_SESSION_START, root)
        assert result[0].priority == "critical"
        assert result[1].priority == "high"
        assert result[2].priority == "low"

    def test_does_not_raise_when_governance_missing(self, tmp_path):
        """surface() must never raise even without governance/ directory."""
        result = surface(TRIGGER_PHASE_CLOSE, tmp_path)
        assert result == []

    def test_all_trigger_constants_are_strings(self):
        for t in [TRIGGER_SESSION_START, TRIGGER_PHASE_CLOSE,
                  TRIGGER_BLOCK_CLOSE, TRIGGER_SCAN_COMPLETE]:
            assert isinstance(t, str) and len(t) > 0
