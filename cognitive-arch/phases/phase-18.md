---
id: phase-18
status: planned
prev_phase: phase-17
exit_criteria_count: 4
blocks_count: 5
estimated_duration_minutes: 150
created_at: 2026-05-28
last_updated: 2026-05-28
owner: implementer
---

# Phase 18 — Token Intelligence

BRIEF: Make token consumption a first-class metric. tok_actual becomes mandatory in every retro. A tracker reads all retros, produces per-block and per-phase token reports, exposes a dashboard widget, and feeds token signals into the pattern analyzer.

## 1. Purpose

Token cost has been invisible. Retros record estimated tokens but actual consumption (`tok_actual`) has been optional — so velocity data is incomplete. Phase 18 closes the loop: enforce tok_actual at block-close time, build a tracker that aggregates the data, add a budget axiom, and surface a dashboard widget that shows weekly token burn and projection to phase end. This turns token usage from an afterthought into a governable metric.

## 2. Goals

- tok_actual field mandatory in retro frontmatter; block_close.py warns/halts if missing (unless --force)
- sdk/token_tracker.py reads all retros, produces governance/token-report.md with per-block and per-phase summary
- governance/token-budget.md defines phase-level token budgets; Axiom P-TOK-1 added to PROTOCOLS.md
- Dashboard token widget: last-7-day burn + projection to phase end
- sdk/token_analyzer.py feeds token signals into pattern_analyzer (e.g. budget-overrun-recurring pattern)

## 3. Invariants

- tok_actual is always the user-reported figure, never AI-estimated
- Token budgets are advisory (warn) not hard-blocking at phase level; block-close is the only hard check
- Historical retros without tok_actual are backfilled with `null` — not zeroed — to avoid false velocity data
- Pattern signals from token data use the same D1/D7/D30 thresholds as retro signals

## 4. Dependencies

- Phase 16 complete (retro format stabilized; block_close.py exists)
- Phase 17 complete (pattern_analyzer.py exists and accepts new signal types)
- blocks/BLOCK_LOG.md and blocks/*-retro.md files present

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Forcing tok_actual breaks existing block-close flow | Med | --force flag bypasses; warn only for historical blocks |
| Token tracker parses retros incorrectly (YAML variance) | Med | Unit tests on all retro format variants; null-safe parsing |
| Budget numbers are arbitrary without baseline | Low | Phase-18 itself establishes baseline from historical data |
| Dashboard widget shows misleading projection with sparse data | Low | Widget shows "insufficient data" when < 3 blocks in window |

## 6. Validation

- Run `python -m pytest sdk/tests/ -q` — 0 failures
- Run `python sdk/token_tracker.py --arch-root .` — produces governance/token-report.md
- Open governance/dashboard.html — token widget visible with real data
- Close a test block without tok_actual — block_close.py emits WARN and halts (unless --force)

## 7. Exit Criteria

1. tok_actual field mandatory in retro frontmatter; `sdk/block_close.py` checks presence and emits WARN + halts without `--force`. Existing retros without tok_actual flagged as `null` (not zeroed) in token-report.
2. `sdk/token_tracker.py --arch-root .` reads all blocks/*-retro.md files, produces `governance/token-report.md` with columns: block_id, tok_estimated, tok_actual, delta, phase, date.
3. `governance/token-budget.md` defines per-phase token budgets; Axiom **P-TOK-1** ("Track actual token cost on every block; budget overrun triggers governance review") added to PROTOCOLS.md.
4. Dashboard token widget renders: 7-day burn chart (bar), phase budget vs actual, projection to phase end. Widget gracefully handles < 3 data points.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-112 | tok_actual enforcement | S | planned | `manifests/block-112-tok-actual-enforcement.md` |
| block-113 | token_tracker.py | M | planned | `manifests/block-113-token-tracker.md` |
| block-114 | token-budget.md + axiom | S | planned | `manifests/block-114-token-budget.md` |
| block-115 | Dashboard token widget | M | planned | `manifests/block-115-dashboard-token-widget.md` |
| block-116 | token_analyzer.py signals | M | planned | `manifests/block-116-token-analyzer.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 5
  recommended_agents: 1
  groups:
    - id: 18A
      blocks: [block-112]
      type: sequential
      depends_on: []
    - id: 18B
      blocks: [block-113, block-114]
      type: parallel
      depends_on: [18A]
    - id: 18C
      blocks: [block-115, block-116]
      type: parallel
      depends_on: [18B]
```

Enforcement first; tracker and budget can be built in parallel against the same retro format; widget and analyzer consume tracker output.

## 10. Out of Scope

- Real-time token counting via API hooks (requires Anthropic API access; future phase)
- Per-agent token allocation (single-agent today)
- Token cost in dollars (user can calculate from token counts externally)
- Retroactive enforcement on closed blocks (historical retros get null, not re-opened)

---

End of phase-18.
