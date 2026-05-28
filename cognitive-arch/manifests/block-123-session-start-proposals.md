---
id: block-123
tier: S
kind: small-fix
phase: phase-20
status: planned
security: false
files:
  read:
    - sdk/session_start.py
    - governance/proposals/index.md
  modify:
    - sdk/session_start.py
  create: []
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
parallel_with: [block-124]
---

# Block 123 — session_start Proposals

- **Tier:** S
- **Kind:** small-fix
- **Status:** planned
- **Parallel-with:** block-124

## 1. Purpose

Extend session_start.py to read governance/proposals/index.md and display pending proposal count at every session start. Output format: `[PROPOSALS] N pending — see governance/proposals/`. Always shows even when N=0 (shows "0 pending — none to review"). This ensures proposals are never silently ignored.

## 2. Dependencies

- block-122: protocol_updater.py + proposals/index.md must exist

## 3. Files

- **Read:** sdk/session_start.py, governance/proposals/index.md
- **Modify:** sdk/session_start.py — add `_count_pending_proposals(arch_root)` and call in summary section
- **Create:** None

## 4. Validation

- Run session_start.py with 2 pending proposals — confirm `[PROPOSALS] 2 pending` in output
- Run session_start.py with 0 proposals — confirm `[PROPOSALS] 0 pending — none to review`
- Run session_start.py with missing proposals/index.md — no crash; shows "proposals index not found"
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, files-updated

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Proposals/index.md parsing fails | Low | Null-safe read; session_start never blocked by proposal read failure |

## 7. Out of Scope

- Showing proposal content inline (link only — user reads governance/proposals/)
- Auto-accepting proposals at session start

## 8. New Abstraction

`_count_pending_proposals(arch_root) -> int` — reads index.md, counts rows with status:pending.
