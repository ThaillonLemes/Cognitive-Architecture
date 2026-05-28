---
id: block-133
tier: S
kind: small-fix
phase: phase-22
status: planned
security: false
files:
  read:
    - sdk/dashboard_generator.py
    - sdk/governor.py
    - governance/notifications.md
  modify:
    - sdk/dashboard_generator.py
  create: []
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
parallel_with: [block-131, block-132]
---

# Block 133 — Dashboard Notifications Widget

- **Tier:** S
- **Kind:** small-fix
- **Status:** planned
- **Parallel-with:** block-131, block-132

## 1. Purpose

Add a governor notifications widget to governance/dashboard.html. Shows top 3 pending notifications sorted by priority. Each entry shows: priority badge (color-coded: red=critical, orange=high, yellow=medium, blue=low), message, age in days, notification id. "View all" link points to governance/notifications.md. If 0 pending: shows "No pending notifications — system quiet" in green.

## 2. Dependencies

- block-127: governor.py must exist (dashboard reads notifications.md via governor's Python API)

## 3. Files

- **Read:** sdk/dashboard_generator.py, sdk/governor.py, governance/notifications.md
- **Modify:** sdk/dashboard_generator.py — add `_render_notifications_widget()`
- **Create:** None

## 4. Validation

- Add 4 notifications with different priorities; run dashboard_generator.py — widget shows top 3 by priority
- 4th notification not shown; "view all" link present
- 0 pending notifications — widget shows "system quiet" message in green
- Color badges render correctly in HTML (inline CSS, no external dependencies)
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, files-updated

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Widget breaks if notifications.md is missing | Low | Widget gracefully shows "Notifications file not found" |
| Priority colors clash with dashboard color scheme | Low | Inline CSS uses standard web-safe colors; no external stylesheet dependency |

## 7. Out of Scope

- Dismissing notifications from dashboard (CLI only)
- Notification history in dashboard (current pending only)

## 8. New Abstraction

`_render_notifications_widget(arch_root) -> str` in dashboard_generator.py. Uses `Governor(arch_root).list(pending_only=True)` internally.
