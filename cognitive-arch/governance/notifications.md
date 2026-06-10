---
# Notification Queue Schema
# This file is the persistent notification queue for cognitive-arch governor.
# Managed by sdk/governor.py — do not edit manually while governor is running.
#
# Schema per notification entry:
#   id:           string  — unique, deterministic (type-source-date-seq)
#   type:         string  — one of: pattern, proposal, health, phase, block, custom
#   message:      string  — human-readable notification text
#   priority:     string  — one of: critical | high | medium | low
#   status:       string  — one of: pending | seen | dismissed
#   source:       string  — tool or context that created the notification
#   created_at:   date    — ISO 8601 (YYYY-MM-DD)
#   seen_at:      date    — ISO 8601 or ~ (null)
#   dismissed_at: date    — ISO 8601 or ~ (null)
#
# Lifecycle:
#   pending → seen (shown at session start or dashboard)
#   seen → dismissed (user acknowledges via sdk/governor.py --dismiss <id>)
#   dismissed entries older than 30 days are moved to notifications-archive.md
#
# Types reference:
#   pattern   — from pattern_analyzer: recurring signal above threshold
#   proposal  — from protocol_updater: new proposal created or stale
#   health    — from health_report: score dropped below threshold
#   phase     — phase transition events
#   block     — block-level events (gate failures, overruns)
#   custom    — manually created via sdk/governor.py --notify


notifications:
- id: health-2026-06-01-001
  type: health
  message: 29 invariant warning(s) active — run sdk/invariant_check.py for details
  priority: high
  status: pending
  source: manual
  created_at: 2026-06-01
  seen_at: ~
  dismissed_at: ~
---
