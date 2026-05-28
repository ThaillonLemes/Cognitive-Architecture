---
id: block-103
tier: M
kind: implementation
phase: phase-16
scope: phase-bound
status: pending
security: false
dependencies: [block-100]
files:
  read:
    - sdk/master_scheduler.py
    - blocks/BLOCK_LOG.md
    - STATE.md
    - NEXT.md
    - design/arch-v3.md
  modify: []
  create:
    - sdk/briefing_generator.py
    - sdk/tests/test_briefing_generator.py
    - templates/briefing-post-pause.md
gates:
  - name: briefing-module
    type: file-changed
    paths: [sdk/briefing_generator.py, templates/briefing-post-pause.md]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_briefing_generator.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-100]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-103-briefing-generator.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 103 — Briefing pós-pausa generator

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Generate a post-pause briefing when user opens a session and last_activity exceeds the pause threshold (24h default per Q10, configurable). Briefing covers: time since last session, blocks closed during absence, current state delta, stale tools, next recommended action.

## 2. Dependencies

- block-100 (scheduler provides stale tools list)

## 3. Files

- **Read:** scheduler, BLOCK_LOG, STATE.md, NEXT.md, arch-v3
- **Modify:** —
- **Create:** `sdk/briefing_generator.py`, test file, `templates/briefing-post-pause.md` (output template)

## 4. Validation

- Generator produces both markdown and minimal HTML versions
- Template covers: time since last, BLOCK_LOG diff, state changes, stale tools (from scheduler), suggested next action
- Tested across pause durations: 24h, 72h, 7d, 30d (different content emphasis per duration)
- Pause threshold configurable via tools-registry-style override

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Briefing too long, defeats purpose | High | Hard cap: 15 lines max; truncate with "... see dashboard for more" |
| Triggers when user doesn't want it | Med | Configurable threshold + per-session disable flag |

## 7. Out of Scope

- Real-time monitoring during active session (briefing is at session-start only)
- Cross-project briefings (per-project)
- Voice/audio briefing

## 8. New Abstraction

`PostPauseBriefing` dataclass + generator module. Consumed by Master Agent (Phase 15 integration) and dashboard (block-105). Rule of Three met.
