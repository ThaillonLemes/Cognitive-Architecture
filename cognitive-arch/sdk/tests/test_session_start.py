# PURPOSE: Tests for sdk/session_start.py — _create_session_notifications()
# INPUTS:  tmp_path, synthetic governance/notifications.md
# OUTPUTS: assertions on notification creation logic
# DEPS:    pytest, session_start, notification_manager
# SEE:     sdk/session_start.py, sdk/notification_manager.py, block-177

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from session_start import _create_session_notifications
from notification_manager import Governor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_env(tmp_path: Path) -> Path:
    """Create minimal governance env for notifications."""
    gov_dir = tmp_path / "governance"
    gov_dir.mkdir(parents=True)
    (gov_dir / "notifications.md").write_text(
        "---\nnotifications: []\n---\n", encoding="utf-8"
    )
    (gov_dir / "notifications-archive.md").write_text(
        "---\nnotifications_archive: []\n---\n", encoding="utf-8"
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Invariant notifications
# ---------------------------------------------------------------------------

class TestInvariantNotifications:
    def test_critical_invariant_creates_critical_notification(self, tmp_path):
        root = _make_env(tmp_path)
        _create_session_notifications(root, inv_critical=1, inv_warn=0, health_score=None)
        items = Governor(root).list(pending_only=False)
        assert any(n.priority == "critical" and "invariant" in n.message.lower() for n in items)

    def test_warn_invariants_creates_high_notification(self, tmp_path):
        root = _make_env(tmp_path)
        _create_session_notifications(root, inv_critical=0, inv_warn=5, health_score=None)
        items = Governor(root).list(pending_only=False)
        assert any(n.priority == "high" and "invariant" in n.message.lower() for n in items)

    def test_consolidated_warn_is_single_notification(self, tmp_path):
        """42 warnings → 1 notification (consolidated), not 42."""
        root = _make_env(tmp_path)
        _create_session_notifications(root, inv_critical=0, inv_warn=42, health_score=None)
        items = [n for n in Governor(root).list(pending_only=False)
                 if "invariant" in n.message.lower() and n.priority == "high"]
        assert len(items) == 1

    def test_zero_invariants_creates_no_notification(self, tmp_path):
        root = _make_env(tmp_path)
        _create_session_notifications(root, inv_critical=0, inv_warn=0, health_score=None)
        assert Governor(root).list(pending_only=False) == []


# ---------------------------------------------------------------------------
# Health score notifications
# ---------------------------------------------------------------------------

class TestHealthScoreNotifications:
    def test_score_below_60_creates_critical(self, tmp_path):
        root = _make_env(tmp_path)
        _create_session_notifications(root, inv_critical=0, inv_warn=0, health_score=55)
        items = Governor(root).list(pending_only=False)
        assert any(n.priority == "critical" and "health" in n.message.lower() for n in items)

    def test_score_between_60_and_75_creates_high(self, tmp_path):
        root = _make_env(tmp_path)
        _create_session_notifications(root, inv_critical=0, inv_warn=0, health_score=72)
        items = Governor(root).list(pending_only=False)
        assert any(n.priority == "high" and "degraded" in n.message.lower() for n in items)

    def test_score_75_or_above_creates_no_health_notification(self, tmp_path):
        root = _make_env(tmp_path)
        _create_session_notifications(root, inv_critical=0, inv_warn=0, health_score=80)
        assert Governor(root).list(pending_only=False) == []

    def test_none_score_creates_no_notification(self, tmp_path):
        root = _make_env(tmp_path)
        _create_session_notifications(root, inv_critical=0, inv_warn=0, health_score=None)
        assert Governor(root).list(pending_only=False) == []


# ---------------------------------------------------------------------------
# Idempotency — running twice does not duplicate notifications
# ---------------------------------------------------------------------------

class TestIdempotency:
    def test_same_conditions_twice_deduplicates(self, tmp_path):
        root = _make_env(tmp_path)
        _create_session_notifications(root, inv_critical=0, inv_warn=5, health_score=72)
        _create_session_notifications(root, inv_critical=0, inv_warn=5, health_score=72)
        items = Governor(root).list(pending_only=False)
        # Should not have duplicates — notification_manager is idempotent on same message+type
        messages = [n.message for n in items]
        assert len(messages) == len(set(messages))


# ---------------------------------------------------------------------------
# Resilience — missing governance/ dir does not raise
# ---------------------------------------------------------------------------

class TestResilience:
    def test_missing_governance_dir_does_not_raise(self, tmp_path):
        """_create_session_notifications must never raise even if governance/ is absent."""
        _create_session_notifications(tmp_path, inv_critical=1, inv_warn=5, health_score=50)
