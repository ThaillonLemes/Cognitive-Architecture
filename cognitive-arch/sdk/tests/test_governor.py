# PURPOSE: Tests for sdk/notification_manager.py (block-127 — Governor CRUD)
# INPUTS:  tmp_path, synthetic notifications.md
# OUTPUTS: assertions on CRUD operations and file mutations
# DEPS:    pytest, pathlib, notification_manager module
# SEE:     sdk/notification_manager.py, governance/notifications.md, block-127

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from notification_manager import (
    Governor,
    Notification,
    _acquire_lock,
    _make_id,
    _parse_notifications,
    _render_notifications,
    _unquote,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EMPTY_NOTIF = "---\nnotifications: []\n---\n"

_NOTIF_WITH_ONE = """\
---
notifications:
- id: pattern-2026-05-28-001
  type: pattern
  message: scope-expansion-recurring detected 4 times
  priority: high
  status: pending
  source: pattern_analyzer
  created_at: 2026-05-28
  seen_at: ~
  dismissed_at: ~
---
"""


def _make_env(tmp_path: Path, content: str = _EMPTY_NOTIF) -> tuple[Path, Path]:
    """Create minimal governance env. Returns (arch_root, notif_path)."""
    gov_dir = tmp_path / "governance"
    gov_dir.mkdir()
    notif_path = gov_dir / "notifications.md"
    notif_path.write_text(content, encoding="utf-8")
    archive_path = gov_dir / "notifications-archive.md"
    archive_path.write_text("---\nnotifications_archive: []\n---\n", encoding="utf-8")
    return tmp_path, notif_path


# ---------------------------------------------------------------------------
# _parse_notifications
# ---------------------------------------------------------------------------

class TestParseNotifications:
    def test_empty_list(self):
        assert _parse_notifications(_EMPTY_NOTIF) == []

    def test_parses_one(self):
        items = _parse_notifications(_NOTIF_WITH_ONE)
        assert len(items) == 1
        assert items[0].id == "pattern-2026-05-28-001"
        assert items[0].status == "pending"

    def test_message_unquoted(self):
        text = "---\nnotifications:\n- id: x\n  type: custom\n  message: \"hello world\"\n  priority: low\n  status: pending\n  source: manual\n  created_at: 2026-05-28\n  seen_at: ~\n  dismissed_at: ~\n---\n"
        items = _parse_notifications(text)
        assert items[0].message == "hello world"


# ---------------------------------------------------------------------------
# _render_notifications
# ---------------------------------------------------------------------------

class TestRenderNotifications:
    def test_empty_renders_empty_list(self):
        assert _render_notifications([]) == "notifications: []\n"

    def test_one_item_renders(self):
        n = Notification(id="x-001", type="custom", message="test", priority="low",
                         status="pending", source="manual", created_at="2026-05-28")
        rendered = _render_notifications([n])
        assert "- id: x-001" in rendered
        assert "message: test" in rendered


# ---------------------------------------------------------------------------
# Governor.add
# ---------------------------------------------------------------------------

class TestGovernorAdd:
    def test_add_creates_notification(self, tmp_path):
        root, notif = _make_env(tmp_path)
        gov = Governor(root)
        nid = gov.add("test message", type_="pattern", priority="high")
        assert nid.startswith("pattern-")
        items = gov.list()
        assert len(items) == 1
        assert items[0].message == "test message"

    def test_add_returns_id(self, tmp_path):
        root, _ = _make_env(tmp_path)
        gov = Governor(root)
        nid = gov.add("msg")
        assert isinstance(nid, str) and len(nid) > 0

    def test_add_idempotent_same_message_type(self, tmp_path):
        root, _ = _make_env(tmp_path)
        gov = Governor(root)
        id1 = gov.add("dup msg", type_="pattern")
        id2 = gov.add("dup msg", type_="pattern")
        assert id1 == id2
        assert len(gov.list()) == 1

    def test_add_different_types_not_idempotent(self, tmp_path):
        root, _ = _make_env(tmp_path)
        gov = Governor(root)
        id1 = gov.add("same msg", type_="pattern")
        id2 = gov.add("same msg", type_="proposal")
        assert id1 != id2
        assert len(gov.list()) == 2

    def test_add_persists_priority(self, tmp_path):
        root, _ = _make_env(tmp_path)
        gov = Governor(root)
        gov.add("critical issue", type_="health", priority="critical")
        items = gov.list()
        assert items[0].priority == "critical"


# ---------------------------------------------------------------------------
# Governor.list
# ---------------------------------------------------------------------------

class TestGovernorList:
    def test_list_empty(self, tmp_path):
        root, _ = _make_env(tmp_path)
        gov = Governor(root)
        assert gov.list() == []

    def test_list_pending_only(self, tmp_path):
        root, _ = _make_env(tmp_path, _NOTIF_WITH_ONE)
        gov = Governor(root)
        gov.add("another", type_="proposal")
        items = gov.list(pending_only=True)
        assert all(n.status == "pending" for n in items)

    def test_list_all_includes_seen(self, tmp_path):
        root, _ = _make_env(tmp_path, _NOTIF_WITH_ONE)
        gov = Governor(root)
        gov.seen("pattern-2026-05-28-001")
        all_items = gov.list(pending_only=False)
        assert any(n.status == "seen" for n in all_items)
        pending_items = gov.list(pending_only=True)
        assert len(pending_items) == 0


# ---------------------------------------------------------------------------
# Governor.seen
# ---------------------------------------------------------------------------

class TestGovernorSeen:
    def test_seen_marks_seen(self, tmp_path):
        root, _ = _make_env(tmp_path, _NOTIF_WITH_ONE)
        gov = Governor(root)
        ok = gov.seen("pattern-2026-05-28-001")
        assert ok
        items = gov.list()
        assert items[0].status == "seen"
        assert items[0].seen_at != "~"

    def test_seen_returns_false_for_missing_id(self, tmp_path):
        root, _ = _make_env(tmp_path)
        gov = Governor(root)
        assert gov.seen("nonexistent") is False


# ---------------------------------------------------------------------------
# Governor.dismiss
# ---------------------------------------------------------------------------

class TestGovernorDismiss:
    def test_dismiss_sets_dismissed(self, tmp_path):
        root, _ = _make_env(tmp_path, _NOTIF_WITH_ONE)
        gov = Governor(root)
        ok, msg = gov.dismiss("pattern-2026-05-28-001", force=True)
        assert ok
        items = gov.list()
        assert items[0].status == "dismissed"
        assert items[0].dismissed_at != "~"

    def test_dismiss_removes_from_pending(self, tmp_path):
        root, _ = _make_env(tmp_path, _NOTIF_WITH_ONE)
        gov = Governor(root)
        gov.dismiss("pattern-2026-05-28-001", force=True)
        assert gov.list(pending_only=True) == []

    def test_dismiss_twice_returns_false(self, tmp_path):
        root, _ = _make_env(tmp_path, _NOTIF_WITH_ONE)
        gov = Governor(root)
        gov.dismiss("pattern-2026-05-28-001", force=True)
        ok, msg = gov.dismiss("pattern-2026-05-28-001", force=True)
        assert not ok
        assert "already" in msg.lower()

    def test_dismiss_not_found_returns_false(self, tmp_path):
        root, _ = _make_env(tmp_path)
        gov = Governor(root)
        ok, msg = gov.dismiss("nonexistent", force=True)
        assert not ok


# ---------------------------------------------------------------------------
# Governor.archive_old
# ---------------------------------------------------------------------------

class TestGovernorArchiveOld:
    def test_archive_old_moves_dismissed(self, tmp_path):
        root, _ = _make_env(tmp_path, _NOTIF_WITH_ONE)
        gov = Governor(root)
        gov.dismiss("pattern-2026-05-28-001", force=True)
        # Manually set dismissed_at to old date
        items = gov.list()
        items[0].dismissed_at = "2026-01-01"
        from notification_manager import _write_file
        _write_file(root / "governance" / "notifications.md", items)
        n = gov.archive_old(days=30)
        assert n == 1
        assert gov.list() == []

    def test_archive_old_keeps_recent(self, tmp_path):
        root, _ = _make_env(tmp_path, _NOTIF_WITH_ONE)
        gov = Governor(root)
        gov.dismiss("pattern-2026-05-28-001", force=True)
        n = gov.archive_old(days=30)
        assert n == 0  # dismissed today — not old enough
        assert len(gov.list()) == 1


class TestAtomicReadModifyWrite:
    """Verify CRUD methods do read-modify-write inside a single lock (no lost-update gap)."""

    def test_add_does_not_call_write_file_with_lock(self, tmp_path, monkeypatch):
        """add() must call _write_file_unlocked (inside lock), not _write_file (double-lock)."""
        root, _ = _make_env(tmp_path)
        import notification_manager as nm
        write_file_calls = []
        write_file_unlocked_calls = []
        original_unlocked = nm._write_file_unlocked

        def spy_write_file(path, items, key="notifications"):
            write_file_calls.append(1)

        def spy_unlocked(path, items, key="notifications"):
            write_file_unlocked_calls.append(1)
            original_unlocked(path, items, key)

        monkeypatch.setattr(nm, "_write_file", spy_write_file)
        monkeypatch.setattr(nm, "_write_file_unlocked", spy_unlocked)
        gov = Governor(root)
        gov.add("test msg", type_="custom")
        assert write_file_calls == [], "_write_file (double-lock) must not be called by add()"
        assert write_file_unlocked_calls == [1], "_write_file_unlocked must be called once"

    def test_seen_uses_unlocked_write(self, tmp_path, monkeypatch):
        root, _ = _make_env(tmp_path, _NOTIF_WITH_ONE)
        import notification_manager as nm
        write_file_calls = []
        original_unlocked = nm._write_file_unlocked

        def spy_write_file(path, items, key="notifications"):
            write_file_calls.append(1)

        monkeypatch.setattr(nm, "_write_file", spy_write_file)
        monkeypatch.setattr(nm, "_write_file_unlocked", original_unlocked)
        gov = Governor(root)
        gov.seen("pattern-2026-05-28-001")
        assert write_file_calls == [], "seen() must not call _write_file (would double-lock)"

    def test_dismiss_uses_unlocked_write(self, tmp_path, monkeypatch):
        root, _ = _make_env(tmp_path, _NOTIF_WITH_ONE)
        import notification_manager as nm
        write_file_calls = []
        original_unlocked = nm._write_file_unlocked

        def spy_write_file(path, items, key="notifications"):
            write_file_calls.append(1)

        monkeypatch.setattr(nm, "_write_file", spy_write_file)
        monkeypatch.setattr(nm, "_write_file_unlocked", original_unlocked)
        gov = Governor(root)
        gov.dismiss("pattern-2026-05-28-001")
        assert write_file_calls == [], "dismiss() must not call _write_file (would double-lock)"
