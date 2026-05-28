# governance/governor-log.md
# Append-only audit trail for notification_manager (Governor) operations.
# Format: ISO8601 EVENT_TYPE NOTIFICATION_ID SOURCE
# Events: add | seen | dismiss | archive
# Run `python sdk/notification_manager.py rotate-log` to rotate entries older than 90 days.
