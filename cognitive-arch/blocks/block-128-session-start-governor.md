---
id: block-128
phase: phase-21
tier: S
status: done
actual_duration_hours: 0.3
duration_source: estimated
tok_actual: 2000
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 128 Retrospective — session_start Governor Integration

## 1. What was built

- `sdk/session_start.py`: `_display_governor_notifications(arch_root)` — displays pending+seen notifications at session start
- Sorted by priority (critical → high → medium → low) then created_at (oldest first)
- Format: `[GOVERNOR] PRIORITY — message (id:ID, age:Nd)`
- Calls `gov.seen()` on each pending notification displayed
- Cap: max 10 shown; "N more" overflow message
- Full try/except wrapper — governor failure never blocks session start

## 2. Gates

- tests-pass: 655 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- `sys.path.insert(0, str(arch_root / "sdk"))` ensures notification_manager import works regardless of CWD
- Filtering `status in ("pending", "seen")` — dismissed notifications are not displayed
- Marking seen at display time, not on dismiss — shows without re-showing dismissed

## 4. DX updated

`sdk/session_start.py` extended with `_display_governor_notifications`. `_PRIORITY_ORDER` and `_MAX_GOVERNOR_DISPLAY` constants added at module level.
