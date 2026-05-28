# PURPOSE: CRUD for governance/notifications.md — add/list/seen/dismiss notifications
# INPUTS:  governance/notifications.md, governance/notifications-archive.md
# OUTPUTS: Updated notifications.md; stdout table on list
# DEPS:    stdlib only (pathlib, re, datetime, dataclasses, contextlib)
# SEE:     governance/notifications.md schema, phases/phase-21.md block-127
# NOTE:    Named notification_manager.py (not governor.py) to avoid collision with
#          sdk/governor.py (multi-agent orchestrator). Governor class kept for API compat.

from __future__ import annotations

import contextlib
import re
import time
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterator, Optional

NOTIFICATIONS_PATH = "governance/notifications.md"
ARCHIVE_PATH = "governance/notifications-archive.md"
_LOCK_TIMEOUT = 5.0


# ---------------------------------------------------------------------------
# Notification dataclass
# ---------------------------------------------------------------------------

@dataclass
class Notification:
    id: str
    type: str
    message: str
    priority: str        # critical | high | medium | low
    status: str          # pending | seen | dismissed
    source: str
    created_at: str
    seen_at: str = "~"
    dismissed_at: str = "~"


# ---------------------------------------------------------------------------
# File lock (cross-platform via lock file)
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def _acquire_lock(path: Path, timeout: float = _LOCK_TIMEOUT) -> Iterator[None]:
    lock_path = path.parent / f".{path.name}.lock"
    deadline = time.monotonic() + timeout
    while True:
        if lock_path.exists():
            try:
                if time.time() - lock_path.stat().st_mtime > timeout:
                    lock_path.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            lock_path.touch(exist_ok=False)
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                raise TimeoutError(f"Could not acquire lock on {path} after {timeout}s")
            time.sleep(0.05)
    try:
        yield
    finally:
        lock_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# YAML serializer / deserializer (no external deps)
# ---------------------------------------------------------------------------

def _val(v: str) -> str:
    """Wrap value in quotes if it contains special YAML chars."""
    if not v or v == "~":
        return v or "~"
    if any(c in v for c in (": ", "#", "{", "}", "[", "]", "&", "*", "?")):
        return f'"{v.replace(chr(34), chr(92)+chr(34))}"'
    return v


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
        v = v[1:-1].replace('\\"', '"')
    return v


def _render_notifications(items: list[Notification], key: str = "notifications") -> str:
    if not items:
        return f"{key}: []\n"
    lines = [f"{key}:\n"]
    for n in items:
        lines += [
            f"- id: {_val(n.id)}\n",
            f"  type: {_val(n.type)}\n",
            f"  message: {_val(n.message)}\n",
            f"  priority: {_val(n.priority)}\n",
            f"  status: {_val(n.status)}\n",
            f"  source: {_val(n.source)}\n",
            f"  created_at: {_val(n.created_at)}\n",
            f"  seen_at: {n.seen_at}\n",
            f"  dismissed_at: {n.dismissed_at}\n",
        ]
    return "".join(lines)


def _parse_notifications(text: str, key: str = "notifications") -> list[Notification]:
    if f"{key}: []" in text:
        return []
    items: list[Notification] = []
    current: dict = {}
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == f"{key}:":
            in_block = True
            continue
        if not in_block:
            continue
        if stripped.startswith("- id:"):
            if current:
                _append(items, current)
            current = {"id": _unquote(stripped[len("- id:"):].strip())}
        elif in_block and re.match(r"  \w", line) and ":" in line:
            k, _, v = line.strip().partition(":")
            current[k.strip()] = _unquote(v.strip())
        elif stripped == "---":
            break
    if current:
        _append(items, current)
    return items


def _append(items: list[Notification], d: dict) -> None:
    try:
        items.append(Notification(
            id=d.get("id", ""),
            type=d.get("type", "custom"),
            message=d.get("message", ""),
            priority=d.get("priority", "low"),
            status=d.get("status", "pending"),
            source=d.get("source", "unknown"),
            created_at=d.get("created_at", ""),
            seen_at=d.get("seen_at", "~"),
            dismissed_at=d.get("dismissed_at", "~"),
        ))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _replace_block(text: str, key: str, new_block: str) -> str:
    """Replace the key: ... block in file text."""
    clean = re.sub(rf"{re.escape(key)}:.*?(?=\n---|$)", "", text, flags=re.DOTALL)
    pos = clean.rfind("---")
    if pos < 0:
        return clean.rstrip() + "\n" + new_block
    return clean[:pos] + new_block + "---\n"


def _write_file(path: Path, items: list[Notification], key: str = "notifications") -> None:
    with _acquire_lock(path):
        text = _read_file(path)
        new_block = _render_notifications(items, key)
        path.write_text(_replace_block(text, key, new_block), encoding="utf-8")


# ---------------------------------------------------------------------------
# ID generator
# ---------------------------------------------------------------------------

def _make_id(type_: str, today: str, items: list[Notification]) -> str:
    base = f"{type_}-{today}"
    existing = {n.id for n in items}
    i = 1
    while f"{base}-{i:03d}" in existing:
        i += 1
    return f"{base}-{i:03d}"


# ---------------------------------------------------------------------------
# Governor class (notification CRUD)
# ---------------------------------------------------------------------------

class Governor:
    """Notification queue manager. Named Governor for API compatibility with block-127 spec."""

    def __init__(self, arch_root: Path) -> None:
        self.arch_root = arch_root
        self.notifications_path = arch_root / NOTIFICATIONS_PATH
        self.archive_path = arch_root / ARCHIVE_PATH

    def _load(self) -> list[Notification]:
        return _parse_notifications(_read_file(self.notifications_path))

    def add(
        self,
        message: str,
        type_: str = "custom",
        priority: str = "medium",
        source: str = "manual",
    ) -> str:
        """Add notification. Idempotent: same message+type returns existing id."""
        items = self._load()
        for n in items:
            if n.message == message and n.type == type_ and n.status != "dismissed":
                return n.id
        today = date.today().isoformat()
        nid = _make_id(type_, today, items)
        items.append(Notification(
            id=nid, type=type_, message=message, priority=priority,
            status="pending", source=source, created_at=today,
        ))
        _write_file(self.notifications_path, items)
        return nid

    def list(self, pending_only: bool = False) -> list[Notification]:
        items = self._load()
        return [n for n in items if n.status == "pending"] if pending_only else items

    def seen(self, notification_id: str) -> bool:
        items = self._load()
        today = date.today().isoformat()
        for n in items:
            if n.id == notification_id:
                if n.status == "pending":
                    n.status = "seen"
                    n.seen_at = today
                _write_file(self.notifications_path, items)
                return True
        return False

    def dismiss(self, notification_id: str, force: bool = False) -> tuple[bool, str]:
        items = self._load()
        today = date.today().isoformat()
        for n in items:
            if n.id == notification_id:
                if n.status == "dismissed":
                    return False, f"Already dismissed: {notification_id}"
                n.status = "dismissed"
                n.dismissed_at = today
                if n.seen_at == "~":
                    n.seen_at = today
                _write_file(self.notifications_path, items)
                return True, f"Dismissed: {notification_id}"
        return False, f"Not found: {notification_id}"

    def archive_old(self, days: int = 30) -> int:
        items = self._load()
        cutoff = date.today() - timedelta(days=days)
        to_archive, to_keep = [], []
        for n in items:
            if n.status == "dismissed" and n.dismissed_at != "~":
                try:
                    if date.fromisoformat(n.dismissed_at) < cutoff:
                        to_archive.append(n)
                        continue
                except ValueError:
                    pass
            to_keep.append(n)
        if not to_archive:
            return 0
        _write_file(self.notifications_path, to_keep)
        archived = _parse_notifications(
            _read_file(self.archive_path), key="notifications_archive"
        )
        archived.extend(to_archive)
        _write_file(self.archive_path, archived, key="notifications_archive")
        return len(to_archive)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _print_table(items: list[Notification]) -> None:
    if not items:
        print("  (no notifications)")
        return
    sorted_items = sorted(items, key=lambda n: (_PRIORITY_ORDER.get(n.priority, 9), n.created_at))
    print(f"  {'ID':<36} {'Type':<10} {'Priority':<10} {'Status':<10} Message")
    print("  " + "-" * 88)
    for n in sorted_items:
        msg = n.message[:44] + "…" if len(n.message) > 45 else n.message
        print(f"  {n.id:<36} {n.type:<10} {n.priority:<10} {n.status:<10} {msg}")


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Governor — notification queue manager")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    sub = parser.add_subparsers(dest="cmd", required=True)

    add_p = sub.add_parser("add")
    add_p.add_argument("message")
    add_p.add_argument("--type", dest="type_", default="custom",
                       choices=["pattern", "proposal", "health", "phase", "block", "custom"])
    add_p.add_argument("--priority", default="medium", choices=["critical", "high", "medium", "low"])
    add_p.add_argument("--source", default="manual")

    list_p = sub.add_parser("list")
    list_p.add_argument("--pending", action="store_true")

    seen_p = sub.add_parser("seen")
    seen_p.add_argument("id")

    dis_p = sub.add_parser("dismiss")
    dis_p.add_argument("id")
    dis_p.add_argument("--force", action="store_true")

    arch_p = sub.add_parser("archive-old")
    arch_p.add_argument("--days", type=int, default=30)

    args = parser.parse_args(argv)
    root = Path(args.arch_root).resolve()
    gov = Governor(root)

    if args.cmd == "add":
        nid = gov.add(args.message, type_=args.type_, priority=args.priority, source=args.source)
        print(f"[notification_manager] OK — id: {nid}")
        return 0
    if args.cmd == "list":
        items = gov.list(pending_only=args.pending)
        print(f"[notification_manager] Notifications ({'pending' if args.pending else 'all'}):")
        _print_table(items)
        return 0
    if args.cmd == "seen":
        ok = gov.seen(args.id)
        print(f"[notification_manager] {'OK — marked seen' if ok else 'ERROR — not found'}: {args.id}")
        return 0 if ok else 1
    if args.cmd == "dismiss":
        ok, msg = gov.dismiss(args.id, force=args.force)
        print(f"[notification_manager] {'OK' if ok else 'ERROR'} — {msg}")
        return 0 if ok else 1
    if args.cmd == "archive-old":
        n = gov.archive_old(days=args.days)
        print(f"[notification_manager] Archived {n} dismissed notification(s) older than {args.days} days.")
        return 0
    return 1


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
