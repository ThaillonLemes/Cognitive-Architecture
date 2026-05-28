---
id: phase-21
status: planned
prev_phase: phase-20
exit_criteria_count: 4
blocks_count: 4
estimated_duration_minutes: 85
created_at: 2026-05-28
last_updated: 2026-05-28
owner: implementer
---

# Phase 21 — Governor Persistent

BRIEF: Governor notifications persist every session until explicitly dismissed. A notification queue lives in governance/notifications.md. sdk/governor.py provides CRUD. session_start.py displays ALL pending notifications at every session start — not once, every time. governance/governor-log.md captures an append-only audit trail of all governance events.

## 1. Purpose

Today, governor notifications (patterns, health warnings, proposal counts) appear once at session start and disappear. If the user doesn't act on them, they're lost. Phase 21 makes notifications persistent: they go into a YAML queue in governance/notifications.md with status pending|seen|dismissed. Every session start shows all pending notifications again. A notification only stops appearing when the user explicitly dismisses it via `sdk/governor.py --dismiss <id>`. governor-log.md provides an append-only audit trail so the history of what was raised and when is always available.

## 2. Goals

- governance/notifications.md: YAML queue with id, type, message, priority, status, created_at, seen_at, dismissed_at
- sdk/governor.py: add / list / seen / dismiss operations; idempotent; thread-safe file writes
- session_start.py: shows ALL pending notifications at EVERY session start (not just once)
- governance/governor-log.md: append-only log of all governor events (add/seen/dismiss/escalate)

## 3. Invariants

- Notifications are NEVER auto-dismissed; only explicit --dismiss removes them from pending view
- seen_at is set when notification appears in session_start output (not when user reads it)
- dismissed_at is set only via governor.py --dismiss; governs when notification stops appearing
- governor-log.md is append-only; no line is ever deleted or modified after writing
- Priority levels: critical | high | medium | low — critical always shows first, regardless of age

## 4. Dependencies

- Phase 15 complete (session_start.py exists and extensible)
- Phase 20 complete (proposals generate governor notifications)
- governance/ directory writable; no immutability conflict on notifications.md or governor-log.md

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| notifications.md grows unbounded over time | Med | Auto-archive dismissed notifications older than 30 days to governance/notifications-archive.md |
| Concurrent session starts corrupt notifications.md | Low | governor.py uses file-level lock (.notifications.lock) during write |
| User dismisses wrong notification | Low | --dismiss requires confirmation prompt; --force skips it |
| governor-log.md grows too large | Low | Log rotation: governor.py --rotate-log moves entries older than 90 days to governor-log-YYYY.md |

## 6. Validation

- Add a test notification via governor.py --add; run session_start.py; verify notification appears
- Run session_start.py again; verify notification STILL appears (not auto-dismissed)
- Run governor.py --dismiss <id>; run session_start.py; verify notification gone
- Verify governor-log.md has entries for add, seen, dismiss events

## 7. Exit Criteria

1. `governance/notifications.md` YAML queue format defined and documented; fields: id, type, message, priority (critical|high|medium|low), status (pending|seen|dismissed), created_at, seen_at, dismissed_at, source (tool/agent that created it).
2. `sdk/governor.py` supports: `--add "message" --type <type> --priority <p>`, `--list [--pending]`, `--seen <id>`, `--dismiss <id> [--force]`. File-level locking prevents corruption. Idempotent: adding duplicate message+type returns existing id.
3. `session_start.py` displays ALL pending+seen notifications at EVERY session start, sorted by priority then age. Output format: `[GOVERNOR] <priority> — <message> (id:<id>, age:<N>d)`. Seen_at updated on display. Dismissed notifications never shown.
4. `governance/governor-log.md` append-only log; every governor.py operation writes one line: `<ISO8601> <event_type> <id> <source>`. Log is never truncated by normal operations; `--rotate-log` moves old entries to archive.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-126 | notifications.md schema | S | planned | `manifests/block-126-notifications-schema.md` |
| block-127 | governor.py CRUD | M | planned | `manifests/block-127-governor-crud.md` |
| block-128 | session_start governor integration | S | planned | `manifests/block-128-session-start-governor.md` |
| block-129 | governor-log.md + audit trail | S | planned | `manifests/block-129-governor-log.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 1
  groups:
    - id: 21A
      blocks: [block-126]
      type: sequential
      depends_on: []
    - id: 21B
      blocks: [block-127]
      type: sequential
      depends_on: [21A]
    - id: 21C
      blocks: [block-128, block-129]
      type: parallel
      depends_on: [21B]
```

Schema first; CRUD second; session integration and log can be built in parallel.

## 10. Out of Scope

- Push notifications (email, Slack, webhook) — local governance only
- Notification expiry / TTL (dismiss is always manual)
- Multi-agent notification routing (all notifications go to master agent today)
- Rich notification content (attachments, links) — message is plain text only

---

End of phase-21.
