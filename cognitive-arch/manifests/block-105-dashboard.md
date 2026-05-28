---
id: block-105
tier: M
kind: implementation
phase: phase-16
scope: phase-bound
status: pending
security: false
dependencies: [block-103, block-104, block-107]
files:
  read:
    - sdk/briefing_generator.py
    - sdk/weekly_report.py
    - sdk/pattern_analyzer.py
    - sdk/master_scheduler.py
    - STATE.md
    - board.md
    - design/arch-v3.md
    - comparacao-cognitive-arch-vs-mercado.html
  modify: []
  create:
    - sdk/dashboard_generator.py
    - sdk/tests/test_dashboard.py
    - templates/dashboard.html
    - templates/_styles.css
    - governance/dashboard.html
gates:
  - name: dashboard-and-styles
    type: file-changed
    paths: [sdk/dashboard_generator.py, templates/dashboard.html, templates/_styles.css, governance/dashboard.html]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_dashboard.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-103, block-104, block-107]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-105-dashboard.md]
created_at: 2026-05-23
estimated_duration_days: 2
---

# Block 105 — Live dashboard HTML

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Generate the live dashboard at `governance/dashboard.html` — single-page HTML viewable in browser. Four-column layout (active agents / next actions / health metrics / recent patterns) + timeline (last 7 days) + roadmap visual (phases done/active/planned) + footer (quick commands). Lazy regeneration on open with 1h cache (D11).

## 2. Dependencies

- block-103 (briefing data integrates)
- block-104 (weekly report links from dashboard; shared styles)
- block-107 (dependency resolution status shown)

## 3. Files

- **Read:** briefing, weekly_report, pattern_analyzer, scheduler, STATE.md, board.md, arch-v3, existing comparativo HTML as baseline
- **Modify:** —
- **Create:** `sdk/dashboard_generator.py`, test file, `templates/dashboard.html`, `templates/_styles.css` (shared with weekly report), `governance/dashboard.html` (initial output)

## 4. Validation

- Dashboard renders standalone (no CDN)
- Four-column layout responsive within reasonable width (1200px+)
- Timeline shows last 7 days of block activity
- Roadmap visual shows all phases with status colors
- Cache busts on STATE.md change or 1h elapsed (D11)
- Visual inspection passes against design intent

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cache invalidation bugs leave stale data | Med | Cache key includes STATE.md mtime + 1h floor; conservative regen |
| HTML grows large with embedded patterns | Med | Recent patterns only (last 30 blocks); link to weekly report for full history |
| Dashboard generation slow | Low | Most data pre-computed by master pipeline; HTML render is fast |

## 7. Out of Scope

- Multi-page dashboard (single page)
- User customization of layout (fixed columns)
- Real-time updates (lazy refresh only)
- Mobile responsive (desktop-first sufficient)
- Drill-down interactivity (links to weekly reports for detail)

## 8. New Abstraction

`Dashboard` renderer + shared `_styles.css`. Justification: styles reused by weekly report (block-104), pattern of HTML standalone reused by future docs. Past Rule of Three.

## 9. Tier note

May upgrade to Tier L during execution if styling/layout proves more involved than estimated. Initial Tier M based on roughly-known scope.
