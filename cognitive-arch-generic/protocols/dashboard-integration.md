# Protocol: Dashboard Integration
# Purpose: Defines when Master Agent triggers reporting outputs (dashboard, weekly report, briefing).
# Scope: Master Agent session start and ongoing operation.
# Created: block-106

---

## 1. Overview

Three reporting modules are wired into the Master Agent:

| Module | Output | SDK command | Trigger |
|--------|--------|-------------|---------|
| `sdk/dashboard_generator.py` | `governance/dashboard.html` | `python sdk/dashboard_generator.py --arch-root .` | Lazy: age ≥ 1h |
| `sdk/weekly_report.py` | `governance/reports/weekly-YYYY-MM-DD.html` | `python sdk/weekly_report.py --arch-root .` | Time: 7-day interval |
| `sdk/briefing_generator.py` | Post-pause briefing (inline + HTML) | `python sdk/briefing_generator.py --arch-root .` | Event: session gap ≥ 24h |

All are tracked in `governance/tools-registry.yaml` under ids:
- `dashboard-refresh` (interval: 1d, time trigger)
- `weekly-report` (interval: 7d, time trigger) — pre-existing
- `post-pause-briefing` (event trigger; threshold read from `agent-master.md:pause_threshold_hours`)

---

## 2. Session start sequence

Master executes this sequence at every session open, in order:

```
1. READ agents/master-log.md → determine session_gap_hours
2. IF session_gap_hours >= pause_threshold_hours (default: 24):
     GENERATE post-pause briefing (sdk/briefing_generator.py)
     DISPLAY briefing before any other output
     UPDATE tools-registry.yaml: post-pause-briefing.last_run = now
3. CHECK governance/dashboard.html mtime:
     IF absent OR age >= 1 hour:
       GENERATE dashboard (sdk/dashboard_generator.py)
       UPDATE tools-registry.yaml: dashboard-refresh.last_run = now
4. RUN sdk/master_scheduler.py --report --arch-root .
   IF any stale tools: SURFACE suggestions (sdk/master_suggest.py)
5. LOG all actions to agents/master-log.md
6. RESPOND to user
```

---

## 3. Dashboard cache rule (D11)

The dashboard is **lazily regenerated** — not on every user message.

```
regenerate_dashboard_if:
  governance/dashboard.html does not exist
  OR now - dashboard.html.mtime >= 3600 seconds (1 hour)
  OR STATE.md.mtime > dashboard.html.mtime
```

This prevents redundant file writes while keeping the dashboard reasonably fresh.

---

## 4. Weekly report trigger

The `weekly-report` tool has `recommended_interval_days: 7`. Master surfaces it when stale (>7 days since last_run). The user initiates generation; Master updates `last_run` after completion.

Weekly report output path: `governance/reports/weekly-YYYY-MM-DD.html` (date = end of rolling 7-day window).

---

## 5. Post-pause briefing trigger

The `post-pause-briefing` tool has `trigger_type: event`. It is not surfaced by the scheduler time-check; instead it is checked by Master directly on session start by comparing:

```
session_gap_hours = (now - last_master_log_entry).total_seconds() / 3600
briefing_needed   = session_gap_hours > pause_threshold_hours
```

`pause_threshold_hours` defaults to 24 (from `agents/agent-master.md:pause_threshold_hours: 24`).

Briefing output: `sdk/briefing_generator.render_markdown()` printed inline; `sdk/briefing_generator.render_html()` available for archiving.

---

## 6. Output relationship

```
master-log.md (session start timestamp)
    └─→ post-pause-briefing? (gap check)
    └─→ dashboard-refresh? (age check) → governance/dashboard.html
    └─→ stale-tools? → suggestions

STATE.md / BLOCK_LOG.md / board.md (data sources)
    └─→ governance/dashboard.html (4-col grid + timeline + roadmap)
    └─→ governance/reports/weekly-YYYY-MM-DD.html (7-day rolling)
```

---

## 7. Master Agent permissions (reporting scope)

Master may write to:
- `governance/dashboard.html` (owned output)
- `governance/reports/weekly-*.html` (owned output)
- `governance/tools-registry.yaml` (last_run fields only)
- `agents/master-log.md` (append only)

Master may NOT write to:
- SDK source files, manifests, design/, phases/, protocols/
- Immutable files (PROTOCOLS.md, _syntax.md, etc.)

---

End of protocol.
