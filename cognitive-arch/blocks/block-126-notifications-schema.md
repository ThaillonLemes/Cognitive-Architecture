---
id: block-126
phase: phase-21
tier: S
status: done
actual_duration_hours: 0.2
duration_source: estimated
tok_actual: 1200
gates_passed: 1/1
created_at: 2026-05-28
---

# Block 126 Retrospective — notifications.md Schema

## 1. What was built

- `governance/notifications.md`: YAML-fronted queue file with full schema documentation (id, type, message, priority, status, source, created_at, seen_at, dismissed_at)
- `governance/notifications-archive.md`: empty archive for dismissed notifications older than 30 days
- Types documented: pattern, proposal, health, phase, block, custom
- Lifecycle documented: pending → seen → dismissed; archive trigger at 30d

## 2. Gates

- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Notifications stored as YAML list (not Markdown table) — parseable by sdk/governor.py without regex
- `notifications: []` empty list valid YAML — governor.py can append without special-case initialization
- Archive is separate file to prevent main queue from growing unbounded

## 4. DX updated

`governance/notifications.md` and `governance/notifications-archive.md` created.
