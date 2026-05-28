---
id: block-127
phase: phase-21
tier: M
status: done
actual_duration_hours: 1.2
duration_source: estimated
tok_actual: 5800
gates_passed: 2/3
created_at: 2026-05-28
---

# Block 127 Retrospective — governor.py CRUD (notification_manager.py)

## 1. What was built

- `sdk/notification_manager.py`: `Governor(arch_root)` class with full CRUD
  - `.add(message, type_, priority, source)` → id (idempotent: same message+type returns existing)
  - `.list(pending_only)` → list[Notification]
  - `.seen(id)` → bool (marks seen_at)
  - `.dismiss(id, force)` → (bool, str) (marks dismissed_at; guards against double-dismiss)
  - `.archive_old(days=30)` → int (moves dismissed notifications to notifications-archive.md)
- `Notification` dataclass mirrors governance/notifications.md schema
- `_acquire_lock(path, timeout)` context manager — lock file based, stale-lock detection
- `_parse_notifications(text, key)` / `_render_notifications(items, key)` — YAML list parser/writer
- `sdk/tests/test_governor.py`: 21 tests

## 2. Gates

- tests-pass: 655 passed, 0 failed ✓
- lint-pass: flake8 not installed — syntax verified with py_compile ✓ (skipped)
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Named `notification_manager.py` (not governor.py) — sdk/governor.py already exists as multi-agent orchestrator; collision avoided
- `Governor` class name kept for API compatibility with block-127 spec
- Idempotency guard: checks message+type combination; dismissed notifications do NOT trigger the idempotency guard (allows re-notification after dismiss)
- `archive_old()` reuses the same parse/render stack with `key="notifications_archive"` for the archive file

## 4. DX updated

`sdk/notification_manager.py` created. CLI: `add`, `list [--pending]`, `seen ID`, `dismiss ID [--force]`, `archive-old [--days N]`.
