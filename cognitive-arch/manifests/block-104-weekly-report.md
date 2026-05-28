---
id: block-104
tier: M
kind: implementation
phase: phase-16
scope: phase-bound
status: pending
security: false
dependencies: [block-095, block-100]
files:
  read:
    - sdk/pattern_analyzer.py
    - sdk/master_scheduler.py
    - sdk/velocity_inference.py
    - blocks/BLOCK_LOG.md
    - design/arch-v3.md
    - governance/health-report-2026-05-23.md
    - comparacao-cognitive-arch-vs-mercado.html
  modify: []
  create:
    - sdk/weekly_report.py
    - sdk/tests/test_weekly_report.py
    - templates/weekly-report.html
gates:
  - name: weekly-report-module
    type: file-changed
    paths: [sdk/weekly_report.py, templates/weekly-report.html]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_weekly_report.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-095, block-100]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-104-weekly-report.md]
created_at: 2026-05-23
estimated_duration_days: 2
---

# Block 104 — Weekly report HTML

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Generate HTML weekly report (relative 7-day rolling per Q11) saved to `governance/reports/weekly-YYYY-MM-DD.html`. Standalone HTML (no CDN, no external JS) styled following the cognitive-arch design baseline. Sections: blocks closed, velocity, gates pass rate, new patterns, next-week forecast.

## 2. Dependencies

- block-095 (pattern data)
- block-100 (scheduler for tools health)

## 3. Files

- **Read:** pattern_analyzer, scheduler, velocity_inference, BLOCK_LOG, arch-v3, sample HTML (the existing comparativo as baseline style)
- **Modify:** —
- **Create:** `sdk/weekly_report.py`, test file, `templates/weekly-report.html` (Jinja-style template)

## 4. Validation

- Output is standalone HTML (no external CDN/JS references)
- Sections render correctly with mock 7-day data
- File size <100KB for typical week
- Dark theme matches existing comparativo style
- Visual inspection of generated report passes

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Style inconsistency with future dashboard (block-105) | Med | Both pull from shared `templates/_styles.css` (created in block-105) — agreed before either implements |
| Report generation slow | Low | Cache patterns/velocity input; HTML render is fast |

## 7. Out of Scope

- Real-time updates (snapshot-only)
- Email delivery (file output only)
- PDF export (browser print works)
- Interactive elements (viewer-only)

## 8. New Abstraction

`WeeklyReport` data structure + generator. Justification: shared rendering pipeline with dashboard (block-105); Rule of Three met.
