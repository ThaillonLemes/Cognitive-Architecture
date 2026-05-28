---
id: block-120
tier: M
kind: implementation
phase: phase-19
scope: phase-bound
status: planned
security: false
dependencies:
  - block-118
files:
  read:
    - sdk/adr_drafter.py
    - sdk/dashboard_generator.py
    - design/adrs/
  modify:
    - sdk/adr_drafter.py
    - sdk/dashboard_generator.py
  create:
    - governance/adrs/index.md
    - sdk/tests/test_adr_index.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: lint-pass
    cmd: python -m flake8 sdk/adr_drafter.py sdk/dashboard_generator.py --max-line-length=120
    expect: "0 errors"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-120-adr-index-dashboard.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-118]
created_at: 2026-05-28
---

# Block 120 — ADR Index + Dashboard Widget

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Add two capabilities to complete phase-19: (1) governance/adrs/index.md maintained automatically — adr_drafter.py appends a row on each new ADR draft; (2) dashboard widget showing ADR count, last ADR date, and count by status (draft/accepted/rejected). Dashboard reads governance/adrs/index.md.

## 2. Dependencies

- block-118: synthesis trigger must be wired before index can be validated end-to-end

## 3. Files

- **Read:** sdk/adr_drafter.py, sdk/dashboard_generator.py, design/adrs/ (scan for existing ADRs)
- **Modify:** sdk/adr_drafter.py — add `_update_index()` call after file creation; sdk/dashboard_generator.py — add `_render_adr_widget()`
- **Create:** governance/adrs/index.md (initial build from existing design/adrs/ scan), sdk/tests/test_adr_index.py

## 4. Validation

- Run adr_drafter on a synthesis with significant decisions — confirm governance/adrs/index.md has new row
- Run dashboard_generator — confirm ADR widget section visible in dashboard.html
- Widget shows: total ADRs, last ADR date, count by status
- index.md scan picks up existing ADRs in design/adrs/ on first run
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, lint-pass, files-updated, dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Index gets out of sync with actual ADR files | Low | `adr_drafter.py --rebuild-index` scans design/adrs/ and rebuilds from scratch |
| Dashboard widget breaks if index.md missing | Low | Widget shows "ADR index not found — run adr_drafter --rebuild-index" |

## 7. Out of Scope

- ADR search or filtering in dashboard
- ADR content rendering in dashboard (link only — user opens file)

## 8. New Abstraction

`_update_index(adr_path, arch_root)` in adr_drafter.py. `_render_adr_widget(index_path) -> str` in dashboard_generator.py.
