---
id: block-115
tier: M
kind: implementation
phase: phase-18
scope: phase-bound
status: planned
security: false
dependencies:
  - block-113
  - block-114
files:
  read:
    - sdk/dashboard_generator.py
    - governance/token-report.md
    - templates/dashboard.html
  modify:
    - sdk/dashboard_generator.py
  create:
    - sdk/tests/test_dashboard_token_widget.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: lint-pass
    cmd: python -m flake8 sdk/dashboard_generator.py --max-line-length=120
    expect: "0 errors"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-115-dashboard-token-widget.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-113, block-114]
created_at: 2026-05-28
---

# Block 115 — Dashboard Token Widget

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Add a token widget to governance/dashboard.html. Widget shows: last-7-day token burn (bar chart using HTML/CSS only — no JS frameworks), total tokens this phase vs budget, and projection to phase end based on velocity. Gracefully shows "Insufficient data (< 3 blocks)" when data is sparse. dashboard_generator.py reads governance/token-report.md to populate.

## 2. Dependencies

- block-113: token_tracker.py + token-report.md must exist
- block-114: token-budget.md must exist for budget comparison

## 3. Files

- **Read:** sdk/dashboard_generator.py, governance/token-report.md, templates/dashboard.html
- **Modify:** sdk/dashboard_generator.py — add `_render_token_widget()` function
- **Create:** sdk/tests/test_dashboard_token_widget.py

## 4. Validation

- Run `python sdk/dashboard_generator.py --arch-root .` — dashboard.html contains token widget section
- Widget renders with real data (shows bar chart HTML)
- Widget renders with < 3 blocks — shows "Insufficient data" message
- Widget renders with missing token-report.md — shows "Token report not found — run token_tracker.py"
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, lint-pass, files-updated, dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| CSS bar chart misaligns in different browsers | Low | Use simple inline-style percentage widths; no external CSS |
| Projection formula inaccurate with sparse data | Low | Require ≥ 3 blocks for projection; show raw average otherwise |

## 7. Out of Scope

- Interactive charts (JavaScript) — static HTML only
- Historical token trend beyond 7 days (future widget)
- Per-agent token breakdown

## 8. New Abstraction

`_render_token_widget(records, budget) -> str` — pure function returning HTML string. Testable in isolation.
