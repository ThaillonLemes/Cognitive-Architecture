---
id: phase-26
status: done
prev_phase: phase-25
exit_criteria_count: 6
blocks_count: 4
estimated_duration_minutes: 180
created_at: 2026-05-30
last_updated: 2026-05-30
owner: implementer
---

# Phase 26 — Unified + Predictive Health

BRIEF: Two instruments disagree — `sdk/audit.py` says 32/100 while `health_report`
says 100/100. This phase collapses them into ONE explainable health score, then makes
the instruments look *forward* (risk at block-start, phase completion forecast) instead
of only backward.

## 1. Purpose

Phase 23 made the instruments stop lying *individually*; this phase makes them agree
*with each other* and start predicting. Today `audit.py` and `health_report.py`
compute health independently and contradict each other (32 vs 100) — a credibility
hole that undermines every "is the project healthy?" answer. This phase defines a
single canonical health model that both consume, and crucially makes the score
**explain itself**: "you are at X/100; the top 3 drags are A (−N), B (−M), C (−K);
fix A first." It then adds the architecture's first forward-looking signals: flag a
block as risky *at its start* when it resembles a known-bad cluster, and forecast when
the current phase will finish from measured velocity. Backward-looking observation
(Phases 14–23) becomes foresight.

## 2. Goals

- A canonical health model (`sdk/health_model.py`): one `HealthScore` derived from
  `project_state` + invariants (Phase 25) + audit signals, with a breakdown of
  weighted factors and their point cost.
- The score **explains itself**: `top_drags()` returns the N factors costing the most
  points, each with a one-line "how to fix" and the points recovered.
- `audit.py` and `health_report.py` report the SAME score (or audit = detail view of
  the same model); the 32-vs-100 contradiction is gone, asserted by a test.
- Risk-at-block-start (`sdk/risk_forecast.py`): given a manifest at block-start, flag
  risk if it resembles a known-bad pattern (scope-expansion cluster, L-tier overrun
  history, oversized `files.modify` list) with a rationale.
- Phase-completion forecast: **create** `sdk/phase_forecast.py` — the `phase-forecast`
  registry entry points to it but the script was never built; the forecast math
  currently lives inline in `health_report._section_phase_progress`. Extract + share
  it, estimate remaining time from velocity + open blocks, and wire into `session_start`.
- Everything reads the single source of truth (`project_state`) — no third parser.

## 3. Invariants

- One health number, one definition. No tool computes health a second way.
- The score is explainable by construction — a number with no breakdown is a bug.
- Forecasts state confidence and never claim more than the data supports
  (reuse the MEASURED/ESTIMATED discipline from block-138).
- No regression: existing audit checks and health fields keep working; the model
  aggregates them, it doesn't replace their detail.

## 4. Dependencies

- Phase 25 (invariants) — the unified score consumes invariant results as a health input.
- `project_state.py` (block-137), `velocity_inference.py` (block-138). NOTE: `phase_forecast.py`
  does NOT exist yet — only a dangling `phase-forecast` registry entry does; block-151 creates the script.

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Unifying scores changes the number people are used to | Med | Document the new model + mapping; keep audit's per-check detail; one block (149) is purely reconciliation with tests asserting agreement. |
| Risk-at-block-start produces false alarms | Med | Advisory only (never blocks); rationale + evidence shown; thresholds tuned against history in block-151. |
| `phase-forecast` registry entry points to a script that was never created (logic is inline in `health_report`) | Med | block-151 creates `sdk/phase_forecast.py`, extracting the shared inline math; treat like the dormant-tool repairs in Phase 23. |
| Health model double-counts audit + invariants | Low | Single weighting table in `health_model`; factors are namespaced; test asserts total = sum of parts. |

## 6. Validation

- Unit: `health_model` scoring + `top_drags` on synthetic states; `risk_forecast` on
  known-good and known-bad manifests; forecast math.
- Integration: audit and health_report on the real arch-root return the same score.
- Regression: a test asserts the two instruments cannot diverge (same model input → same score).

## 7. Exit Criteria

1. `sdk/health_model.py` exposes a single `HealthScore` (score + weighted factor breakdown) read from `project_state` + invariants + audit, with tests.
2. `top_drags(n)` returns the worst factors with point cost + a one-line fix each; surfaced in `health_report` output.
3. `audit.py` and `health_report.py` report the same score on the real arch-root; a test asserts they agree (no more 32-vs-100).
4. `sdk/risk_forecast.py` flags risky manifests at block-start (≥3 heuristics) with rationale + tests; advisory only.
5. `sdk/phase_forecast.py` is created (the dangling registry entry now resolves), runs without error, is wired into `session_start`, and produces a dated completion estimate with a confidence label.
6. Full suite green; `sdk/audit.py` PASS, 0 errors.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-148 | Canonical health model + self-explaining top_drags | M | done | `manifests/block-148-health-model.md` |
| block-149 | Reconcile audit ↔ health_report onto one score | M | done | `manifests/block-149-reconcile-health.md` |
| block-150 | Risk-at-block-start forecaster (heuristics + tests) | M | done | `manifests/block-150-risk-forecast.md` |
| block-151 | Activate phase forecast + wire + verify | M | done | `manifests/block-151-phase-forecast.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 2
  groups:
    - id: 26A
      blocks: [block-148]
      type: sequential
      depends_on: []
    - id: 26B
      blocks: [block-149, block-150]
      type: parallel          # 149 reconciles; 150 is an independent forecaster
      depends_on: [26A]
    - id: 26C
      blocks: [block-151]
      type: sequential
      depends_on: [26B]
```

## 10. Out of Scope

- Acting on health/risk automatically (it informs; humans/Phase 27 act).
- New visual dashboards (the dashboard already renders; it just consumes the new score).
- Cross-project benchmarking.
- Changing the audit's individual checks beyond pointing them at the shared model.
