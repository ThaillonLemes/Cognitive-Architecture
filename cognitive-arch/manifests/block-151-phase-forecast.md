---
id: block-151
tier: M
kind: gate
phase: phase-26
scope: phase-bound
status: pending
security: false
dependencies:
  - block-148
  - block-149
  - block-150
files:
  read:
    - sdk/phase_forecast.py
    - sdk/session_start.py
    - sdk/velocity_inference.py
    - sdk/health_model.py
  modify:
    - sdk/phase_forecast.py
    - sdk/session_start.py
    - governance/tools-registry.yaml
  create:
    - sdk/tests/test_phase_forecast.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: forecast-runs-clean
    type: command
    command: python sdk/phase_forecast.py --arch-root .
    expect: exits 0, no traceback; prints a dated completion estimate + MEASURED/ESTIMATED label
  - name: session-wired
    type: command
    command: python sdk/session_start.py --arch-root . --force
    expect: exits 0; output contains a "Forecast:" line with a date and confidence label
  - name: score-stable
    type: command
    command: python sdk/audit.py --arch-root .
    expect: exits 0; "Result: PASS"; unified score unchanged vs block-149 baseline
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-151-phase-forecast.md]
created_at: 2026-05-30
---

# Block 151 — Activate phase forecast + wire + verify

- **Tier:** M
- **Kind:** gate
- **Status:** pending
- **Parallel-with:** none (closes the phase)

## 1. Purpose

Activate the dormant phase-forecast tool: the `phase-forecast` registry entry exists
(`last_run: never`, points at `sdk/phase_forecast.py`) but the script was never created.
Smoke + repair it into a working forecaster, wire it into `session_start` to print a
dated completion estimate with a confidence label, and verify the unified score stays
stable on the real arch-root — the phase-closing gate.

## 2. Dependencies

- `block-148` (`health_model`), `block-149` (reconciled score — `score-stable` compares
  against its baseline), `block-150` (forecast surfaces alongside risk). All must be `done`.

## 3. Files

- **Read:** `sdk/phase_forecast.py` (dormant target — forecast logic currently lives
  inline in `health_report._section_phase_progress`: remaining-blocks × tier velocity →
  `est_days` → dated completion), `sdk/session_start.py` (`TOOL_RUNNERS` + the `Health:`
  print block), `sdk/velocity_inference.py` (`infer_duration` → `(hours, source)`),
  `sdk/health_model.py`.
- **Modify:**
  - `sdk/phase_forecast.py` — create/repair to run standalone: read remaining blocks via
    `project_state`, × measured tier velocity, emit a dated `est_completion` + a
    `MEASURED`/`ESTIMATED` label (≥3 measured tier samples ⇒ MEASURED, else ESTIMATED —
    block-138 discipline). Extract the inline `health_report` math so both share it.
  - `sdk/session_start.py` — add a `run_phase_forecast` runner to `TOOL_RUNNERS`; print a
    `Forecast: <date> [<label>]` line next to the existing `Health:` line.
  - `governance/tools-registry.yaml` — the `phase-forecast` entry exists; this flips it
    from dormant (`last_run` stamped by session_start on first run).
- **Create:** `sdk/tests/test_phase_forecast.py`.

## 4. Validation

- All tests pass: `python -m pytest sdk/tests/ -q`.
- `phase_forecast.py --arch-root .` exits 0, no traceback, prints a dated estimate +
  MEASURED/ESTIMATED label (Exit Criterion 5).
- `session_start.py --arch-root . --force` exits 0; output contains a `Forecast:` line
  with date + confidence label (wiring proof).
- `audit.py --arch-root .` still `PASS`, same unified score as the block-149 baseline
  (forecast is additive — must not move the health number).
- Unit: forecast math on synthetic states (N remaining × known velocity = expected date);
  label is MEASURED only with ≥3 measured tier samples, else ESTIMATED.

## 5. Gates

Declared in frontmatter: `tests-pass`, `forecast-runs-clean`, `session-wired`,
`score-stable`, `files-updated`. `score-stable` is the phase exit guard (no regression).

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Dormant script never existed; needs more than a smoke fix | Med | Treat like Phase 23's dormant-tool repairs: rebuild from the proven inline `_section_phase_progress` logic; the registry entry/command already define its contract. |
| Forecast overclaims precision from thin velocity data | Med | MEASURED/ESTIMATED label gates the claim (block-138); <3 samples ⇒ ESTIMATED, never a hard date dressed as certain. |
| Wiring into `session_start` slows or crashes session start | Med | Runner wrapped like the others (`_run`, try/except, 60s timeout); a failure prints `FAILED` and continues — never blocks the session. |
| Forecast math duplicated in `phase_forecast` + `health_report` drifts | Low | Extract once; `_section_phase_progress` calls the same function (one forecast, one definition). |

## 7. Out of Scope

- Per-block ETA or Gantt-style projections (single phase-completion date only).
- Acting on the forecast (scheduling/rescheduling blocks — Phase 27).
- Re-tuning health weights (frozen since block-148).
- New dashboard widgets (dashboard consumes the forecast line if present).

## 8. New Abstraction

None. The forecast function is extracted from the existing inline
`_section_phase_progress` logic and shared; the runner follows the established
`TOOL_RUNNERS` shape. Two call sites (health_report + session_start) don't meet Rule of
Three (Axiom Q1), so prefer a plain function returning `(date, label)` over a new type.
