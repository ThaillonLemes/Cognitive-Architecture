---
id: block-127
tier: M
kind: implementation
phase: phase-21
scope: phase-bound
status: planned
security: false
dependencies:
  - block-126
files:
  read:
    - governance/notifications.md
    - sdk/state_manager.py
  modify: []
  create:
    - sdk/governor.py
    - sdk/tests/test_governor.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: lint-pass
    cmd: python -m flake8 sdk/governor.py --max-line-length=120
    expect: "0 errors"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-127-governor-crud.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-126]
created_at: 2026-05-28
---

# Block 127 — governor.py CRUD

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Build sdk/governor.py: full CRUD for governance/notifications.md. Operations: --add "message" --type <type> --priority <p> (returns id), --list [--pending] (prints table), --seen <id> (marks seen_at), --dismiss <id> [--force] (marks dismissed_at, prompts without --force). File-level locking during writes (.notifications.lock). Idempotent: adding duplicate message+type returns existing id instead of creating new. Provides Python API (not just CLI) for use by session_start.py and other tools.

## 2. Dependencies

- block-126: governance/notifications.md schema must be defined

## 3. Files

- **Read:** governance/notifications.md (schema reference), sdk/state_manager.py (file-write pattern reference)
- **Modify:** None
- **Create:** sdk/governor.py, sdk/tests/test_governor.py

## 4. Validation

- `python sdk/governor.py --add "test notification" --type pattern --priority high` → returns id
- `python sdk/governor.py --list --pending` → shows added notification
- `python sdk/governor.py --seen <id>` → seen_at set
- `python sdk/governor.py --dismiss <id> --force` → dismissed_at set; notification no longer in --list --pending
- Add duplicate message+type → returns same id (idempotent)
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, lint-pass, files-updated, dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| File lock deadlock if governor.py crashes mid-write | Low | Lock has 5s timeout; lock file deleted on normal exit; stale lock detected and removed |
| notifications.md grows unbounded | Low | --archive-old command moves dismissed notifications older than 30d to notifications-archive.md |

## 7. Out of Scope

- Push notifications (local file only)
- Notification routing to specific agents (all notifications to master today)
- Notification expiry / TTL (dismiss is always manual)

## 8. New Abstraction

`Governor(arch_root)` class with methods: `.add(message, type, priority) -> str`, `.list(pending_only=False) -> list[Notification]`, `.seen(id)`, `.dismiss(id, force=False)`. `Notification` dataclass mirrors notifications.md schema. File lock via `_acquire_lock(path, timeout=5)` context manager.
