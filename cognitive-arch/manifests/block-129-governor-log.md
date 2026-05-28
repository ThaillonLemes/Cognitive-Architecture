---
id: block-129
tier: S
kind: small-fix
phase: phase-21
status: planned
security: false
files:
  read:
    - sdk/governor.py
    - governance/governor-log.md
  modify:
    - sdk/governor.py
  create:
    - governance/governor-log.md
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
parallel_with: [block-128]
---

# Block 129 — governor-log.md + Audit Trail

- **Tier:** S
- **Kind:** small-fix
- **Status:** planned
- **Parallel-with:** block-128

## 1. Purpose

Add append-only audit logging to governor.py. Every governor operation (add, seen, dismiss, archive) writes one line to governance/governor-log.md: `<ISO8601> <event_type> <notification_id> <source>`. Create governance/governor-log.md. Add --rotate-log command to governor.py that moves entries older than 90 days to governance/governor-log-YYYY.md.

## 2. Dependencies

- block-127: governor.py must exist (adding logging to existing operations)

## 3. Files

- **Read:** sdk/governor.py (to add logging calls), governance/governor-log.md (if exists)
- **Modify:** sdk/governor.py — add `_log_event(event_type, notification_id, source)` call to each operation
- **Create:** governance/governor-log.md (initially empty with header comment)

## 4. Validation

- Run governor.py --add → governor-log.md has new "add" entry
- Run governor.py --seen <id> → governor-log.md has "seen" entry
- Run governor.py --dismiss <id> --force → governor-log.md has "dismiss" entry
- governor-log.md is never modified (only appended) — no line changes after writing
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, files-updated

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Log write failure crashes governor.py | Low | Log write wrapped in try/except; operation succeeds even if log fails |
| Log grows too large | Low | --rotate-log command; documentation recommends running monthly |

## 7. Out of Scope

- Structured log format (JSON) — plain text is sufficient for human reading
- Log analysis tooling (future phase)

## 8. New Abstraction

`_log_event(log_path, event_type, notification_id, source)` — appends one line to governor-log.md. Pure function, no side effects beyond file append.
