# governance/governor-log.md
# Append-only audit trail for notification_manager (Governor) operations.
# Format: ISO8601 EVENT_TYPE NOTIFICATION_ID SOURCE
# Events: add | seen | dismiss | archive
# Run `python sdk/notification_manager.py rotate-log` to rotate entries older than 90 days.
#
# --- INTEGRITY BUMP APPROVED ---
# date: 2026-05-30
# file: PROTOCOLS.md
# reason: axiom P-TOK-1 added by block-113/114 (Phase 18, commit c8f65fc); the
#         .integrity.lock generated at block-091 was never regenerated, so audit
#         check 10 has warned MISMATCH ever since. Working tree clean; current
#         file == committed c8f65fc; locked hash == pre-change initial 9ecd13b.
#         No tampering — stale lock only.
# block: block-113/114
# approved_by: thailloncp (user)
# action: python sdk/integrity_check.py --regenerate --arch-root .
# --- END INTEGRITY BUMP ---
