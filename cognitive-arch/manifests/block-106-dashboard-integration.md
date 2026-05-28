---
id: block-106
tier: S
kind: implementation
phase: phase-16
status: pending
security: false
dependencies: [block-105]
files:
  read:
    - sdk/dashboard_generator.py
    - sdk/briefing_generator.py
    - sdk/weekly_report.py
    - agents/agent-master.md
    - governance/tools-registry.yaml
  modify:
    - agents/agent-master.md
    - governance/tools-registry.yaml
  create:
    - protocols/dashboard-integration.md
gates:
  - name: integration-wired
    type: file-changed
    paths: [agents/agent-master.md, governance/tools-registry.yaml, protocols/dashboard-integration.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-105]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-106-dashboard-integration.md]
created_at: 2026-05-23
---

# Block 106 — Dashboard generator integration

- **Tier:** S
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Wire dashboard + briefing + weekly report into Master Agent's responsibilities. Master triggers briefing at session start (if pause threshold met), regenerates dashboard lazily on open (D11), generates weekly report on relative-7d schedule. Updates tool registry with these as tracked tools.

## 2. Files

- **Read:** dashboard, briefing, weekly_report modules; Master role; tools registry
- **Modify:** `agents/agent-master.md` (add dashboard/reporting responsibilities), `governance/tools-registry.yaml` (add dashboard/weekly-report/briefing entries)
- **Create:** `protocols/dashboard-integration.md` (when Master triggers what)

## 3. Validation

- Master role doc lists 3 new responsibilities with explicit triggers
- tools-registry includes dashboard-refresh, weekly-report-generate, post-pause-briefing with appropriate intervals
- Protocol doc explains the flow: session-start checks pause → briefing if needed → dashboard regen if stale → weekly if interval met

## 4. Out of scope

- Modifying dashboard/briefing/weekly internals (blocks 103-105 own those)
- Notification delivery beyond text-in-conversation
