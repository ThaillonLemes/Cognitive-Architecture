---
id: block-130
phase: phase-22
tier: S
status: done
actual_duration_hours: 0.3
duration_source: estimated
tok_actual: 1800
gates_passed: 1/1
created_at: 2026-05-28
---

# Block 130 Retrospective — governance/ux-voice.md

## 1. What was built

- `governance/ux-voice.md`: 6-section AI tone guide
  1. Tone rules (direct, specific, scannable, neutral, concise)
  2. Format standards table (9 situations × format type)
  3. Prohibited patterns — 24 banned phrases in fenced code block `prohibited`
  4. 5 positive/negative example pairs (opening, result, error, mid-task, closing)
  5. session_start.py rules (must-appear / must-never-appear)
  6. session_start.py output template
- `governance/ux-config.yaml`: dashboard_link_protocol (file), dashboard_links_enabled, dashboard_notifications_max (3), ux_validator settings

## 2. Gates

- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Prohibited phrases in fenced `prohibited` block — parseable by line by ux_validator.py without YAML overhead
- `ux_validator_exit_zero: true` — validator always succeeds; WARNs never block CI

## 4. DX updated

`governance/ux-voice.md` and `governance/ux-config.yaml` created.
