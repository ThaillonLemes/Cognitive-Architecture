---
id: block-128
tier: S
kind: small-fix
phase: phase-21
status: planned
security: false
files:
  read:
    - sdk/session_start.py
    - sdk/governor.py
  modify:
    - sdk/session_start.py
  create: []
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
parallel_with: [block-129]
---

# Block 128 — session_start Governor Integration

- **Tier:** S
- **Kind:** small-fix
- **Status:** planned
- **Parallel-with:** block-129

## 1. Purpose

Extend session_start.py to display ALL pending+seen governor notifications at EVERY session start, sorted by priority (critical first) then age (oldest first). Format: `[GOVERNOR] <PRIORITY> — <message> (id:<id>, age:<N>d)`. Call governor.seen() on each displayed notification. Governor integration must never crash or block session_start — wrap in try/except with graceful fallback.

## 2. Dependencies

- block-127: governor.py must exist with Python API

## 3. Files

- **Read:** sdk/session_start.py, sdk/governor.py
- **Modify:** sdk/session_start.py — add `_display_governor_notifications(arch_root)` call in summary section
- **Create:** None

## 4. Validation

- Add 3 notifications with different priorities via governor.py --add
- Run session_start.py — all 3 appear, sorted critical > high > medium > low
- Run session_start.py again — notifications still appear (not auto-dismissed)
- Dismiss one via governor.py --dismiss; run session_start.py — dismissed notification gone
- Run with governance/notifications.md missing — session_start proceeds normally, no governor section
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, files-updated

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Governor display clutters session_start output | Low | Cap display at 10 notifications; show "N more — use governor.py --list" |
| governor.py import error breaks session_start | Low | Import wrapped in try/except; governor section skipped on import error |

## 7. Out of Scope

- Dismissing notifications from session_start (CLI only)
- Notification content truncation (full message always shown)

## 8. New Abstraction

`_display_governor_notifications(arch_root)` in session_start.py. Calls governor.list(pending_only=False) filtered to pending+seen; calls governor.seen() for each displayed.
