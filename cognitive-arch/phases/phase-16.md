---
id: phase-16
status: done
prev_phase: phase-15
exit_criteria_count: 5
blocks_count: 5
estimated_duration_days: 6
created_at: 2026-05-23
last_updated: 2026-05-23
owner: implementer
---

# Phase 16 — Visibility & Dashboard

BRIEF: HTML dashboard + weekly reports + post-pause briefings. Master Agent generates and refreshes these. User opens browser, sees project state in 30 seconds.

## 1. Purpose

Phases 12-15 produced rich state, patterns, and a Master Agent — but they live in text files the user must read manually. Phase 16 surfaces all that information via HTML reports designed for human consumption. Live dashboard (`governance/dashboard.html`), weekly archived snapshots (`governance/reports/weekly-YYYY-MM-DD.html`), and automatic post-pause briefings. The Master is the generator; the HTML is the consumer interface.

## 2. Goals

- Live dashboard HTML rendered from current STATE/NEXT/patterns/health
- Weekly report HTML generated automatically (relative-day per Q11)
- Post-pause briefing surfaces what changed during pause (24h threshold per Q10, configurable)
- Dashboard styled like `comparacao-cognitive-arch-vs-mercado.html` baseline (dark, modern, standalone)
- Dependency resolution automated: when block-A closes and block-B unblocks, Master notifies

## 3. Invariants

- HTML is standalone (no external CDN, no JS dependencies)
- HTML files in `governance/dashboard.html` and `governance/reports/` count as generated outputs (protection: open)
- Master is the only writer; user reads but doesn't edit
- Latest dashboard always at fixed path; archives at dated paths

## 4. Dependencies

- Phase 12 complete (health report data exists)
- Phase 14 complete (patterns to display)
- Phase 15 complete (Master Agent exists to generate)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Dashboard becomes stale if Master fails to refresh | Med | Lazy regeneration on open (D11); timestamp visible in dashboard so user knows |
| HTML file size grows unbounded with embedded patterns | Low | Archive old entries to dated weekly reports; dashboard shows recent only |
| Weekly report generation conflicts with active session | Low | Generation is fast (<5s); runs at session start, not background |

## 6. Validation

- Render dashboard against 3 simulated project states (empty, mid-phase, post-phase)
- Weekly report generated against last 7 days of mock data passes visual inspection
- Briefing post-pause correctly identifies events for pause durations 24h, 72h, 7d

## 7. Exit Criteria

1. `sdk/briefing_generator.py` produces post-pause briefing (markdown + HTML versions). Triggered when session starts and last_activity > pause_threshold (24h default per Q10).
2. `sdk/weekly_report.py` generates `governance/reports/weekly-YYYY-MM-DD.html` (relative-day per Q11). Sections: blocks closed, velocity, gates pass rate, patterns new this week, next week forecast.
3. `sdk/dashboard_generator.py` produces `governance/dashboard.html` — single page HTML with 4-column layout (active agents, next actions, health metrics, recent patterns) + timeline + roadmap visual. Auto-refresh manual.
4. Master Agent integration: Master runs `briefing_generator` at session start (if pause met), `weekly_report` on relative-7d trigger, `dashboard_generator` lazily on user open (D11).
5. `sdk/dependency_resolver.py` watches BLOCK_LOG: when a block closes, identifies any block with `dependencies:` now fully satisfied and notifies via Master (per D7).

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-103 | Briefing pós-pausa generator | M | planned | `manifests/block-103-briefing-generator.md` |
| block-104 | Weekly report HTML | M | planned | `manifests/block-104-weekly-report.md` |
| block-105 | Live dashboard HTML | L | planned | `manifests/block-105-dashboard.md` |
| block-106 | Dashboard generator integration | S | planned | `manifests/block-106-dashboard-integration.md` |
| block-107 | Dependency resolution automation | M | planned | `manifests/block-107-dependency-resolution.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 5
  recommended_agents: 2
  groups:
    - id: 16A
      blocks: [block-103, block-104, block-107]
      type: parallel
      depends_on: []
    - id: 16B
      blocks: [block-105]
      type: sequential
      depends_on: [16A]
    - id: 16C
      blocks: [block-106]
      type: sequential
      depends_on: [16B]
```

Generators are independent and can run in parallel. Dashboard (16B) composes their outputs. Master integration (16C) wires the whole pipeline.

## 10. Out of Scope

- Real-time websocket updates (overkill for solo use)
- Multi-user dashboard with auth (deferred to product future)
- Mobile-responsive dashboard (desktop only sufficient today)
- Export to PDF (browser print works fine)
- Interactive dashboard (filtering, drill-down) — viewer-only for v1

---

End of phase-16.
