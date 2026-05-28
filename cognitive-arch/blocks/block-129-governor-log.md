---
id: block-129
phase: phase-21
tier: S
status: done
actual_duration_hours: 0.5
duration_source: estimated
tok_actual: 2400
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 129 Retrospective — governor-log.md + Audit Trail

## 1. What was built

- `governance/governor-log.md`: append-only audit trail; format: `ISO8601 EVENT_TYPE NOTIFICATION_ID SOURCE`
- `sdk/notification_manager.py`: `_log_event(log_path, event_type, id, source)` — pure append function, never raises
- Logging integrated into: `add()`, `seen()`, `dismiss()`, `archive_old()`
- `Governor.rotate_log(days=90)` — moves entries older than N days to `governance/governor-log-YYYY.md`; returns count rotated
- CLI: `rotate-log [--days N]` subcommand added

## 2. Gates

- tests-pass: 655 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Log write is always try/except — log failure never propagates to caller
- Rotation splits by year into `governor-log-YYYY.md` files (human-readable, git-friendly)
- `rotate_log` reads all lines, re-writes only the recent ones; existing year archives are append-only
- Header lines (starting with `#`) are always kept in the main log

## 4. DX updated

`governance/governor-log.md` created. `sdk/notification_manager.py` extended with `_log_event`, `rotate_log()`, and `rotate-log` CLI command.
