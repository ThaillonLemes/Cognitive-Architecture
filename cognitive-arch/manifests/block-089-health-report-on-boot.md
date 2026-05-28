---
id: block-089
tier: S
kind: implementation
phase: phase-12
status: pending
security: false
dependencies: [block-086, block-087, block-088]
files:
  read:
    - CLAUDE.md
    - commands/health-report.md
    - sdk/health_report.py
    - governance/health-report-2026-05-23.md
    - design/arch-v3.md
  modify:
    - CLAUDE.md
  create:
    - protocols/health-on-boot.md
gates:
  - name: claude-md-references-health
    type: file-changed
    paths: [CLAUDE.md]
  - name: protocol-created
    type: file-changed
    paths: [protocols/health-on-boot.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-086, block-087, block-088]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-089-health-report-on-boot.md]
created_at: 2026-05-23
---

# Block 089 — Health report on boot

- **Tier:** S
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Make the health report visible at the start of every session, not buried behind a manual command. Adds a HOT-boot step in CLAUDE.md that surfaces a 5-line summary of audit score, velocity status, current phase, blocked items, and recommendations.

## 2. Files

- **Read:** CLAUDE.md, health-report command, health_report.py source, last generated health report, design doc
- **Modify:** CLAUDE.md (add HOT boot step 5: read or regenerate health summary)
- **Create:** `protocols/health-on-boot.md` (defines what's shown, caching rules, regeneration triggers)

## 3. Validation

- CLAUDE.md HOT read order includes health report (cached or freshly generated based on age)
- `protocols/health-on-boot.md` documents: 5-line summary format, cache freshness rules (1h default), trigger to regenerate
- Output template fits in ~10 lines so it doesn't dominate session start

## 4. Out of scope

- HTML dashboard generation (Phase 16)
- Weekly report (Phase 16)
- Master Agent active triggering (Phase 15 — this is passive read at boot)
- Performance optimization of health_report.py (already fast)
