---
id: block-126
tier: S
kind: doc-only
phase: phase-21
status: planned
security: false
files:
  read:
    - governance/patterns.md
  modify: []
  create:
    - governance/notifications.md
    - governance/notifications-archive.md
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
---

# Block 126 — notifications.md Schema

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Define governance/notifications.md: a YAML-fronted file acting as the persistent notification queue. Each notification is a YAML entry with: id, type, message, priority (critical|high|medium|low), status (pending|seen|dismissed), source, created_at, seen_at, dismissed_at. Create governance/notifications-archive.md for dismissed notifications older than 30 days. Document the schema and lifecycle in the files themselves.

## 2. Dependencies

None (first block of phase-21).

## 3. Files

- **Read:** governance/patterns.md (notification type reference for patterns notifications)
- **Modify:** None
- **Create:** governance/notifications.md (empty queue with schema documentation header), governance/notifications-archive.md (empty archive)

## 4. Validation

- governance/notifications.md exists with valid YAML schema header
- governance/notifications-archive.md exists
- `python -c "import yaml; yaml.safe_load(open('governance/notifications.md').read())"` — no error
- Schema documentation is clear: field names, allowed values, lifecycle states

## 5. Gates

- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md changed

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| YAML queue format incompatible with governor.py parser | Low | governor.py (block-127) is built against this exact schema |

## 7. Out of Scope

- Notification content (governor.py creates content)
- Rendering notifications (session_start.py, block-128)

## 8. New Abstraction

None. Schema definition file only.
