---
id: block-124
tier: S
kind: small-fix
phase: phase-20
status: planned
security: false
files:
  read:
    - sdk/dashboard_generator.py
    - governance/proposals/index.md
  modify:
    - sdk/dashboard_generator.py
  create: []
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
parallel_with: [block-123]
---

# Block 124 — Dashboard Proposals Widget

- **Tier:** S
- **Kind:** small-fix
- **Status:** planned
- **Parallel-with:** block-123

## 1. Purpose

Add a proposals section to governance/dashboard.html. Shows: pending count badge (highlighted when > 0), table of last 5 proposals with columns: id, status, pattern_id, target_file, created_at. Reads governance/proposals/index.md. Gracefully handles missing index.

## 2. Dependencies

- block-122: proposals/index.md must exist

## 3. Files

- **Read:** sdk/dashboard_generator.py, governance/proposals/index.md
- **Modify:** sdk/dashboard_generator.py — add `_render_proposals_widget()`
- **Create:** None

## 4. Validation

- Run dashboard_generator.py — dashboard.html has proposals section
- With 3 pending proposals — table shows all 3; badge shows count
- With 0 proposals — section shows "No proposals — learning loop quiet"
- With missing index.md — section shows graceful fallback message
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, files-updated

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Dashboard proposals section breaks dashboard layout | Low | Widget is self-contained HTML block; isolated CSS class |

## 7. Out of Scope

- Accepting/rejecting proposals from dashboard (CLI only — proposal_resolver.py)

## 8. New Abstraction

`_render_proposals_widget(index_path) -> str` in dashboard_generator.py.
