---
id: block-094
tier: M
kind: implementation
phase: phase-14
scope: phase-bound
status: pending
security: false
dependencies: [block-086]
files:
  read:
    - templates/block-retrospective.md
    - blocks/block-001-retrospective.md
    - blocks/phase-1-retrospective.md
    - protocols/retrospective-rubric.md
    - design/arch-v3.md
  modify: []
  create:
    - sdk/retro_signals.py
    - sdk/tests/test_retro_signals.py
    - sdk/retro_signal_schema.py
gates:
  - name: signals-module-created
    type: file-changed
    paths: [sdk/retro_signals.py, sdk/retro_signal_schema.py]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_retro_signals.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-086]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-094-retro-signals.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 094 — Retro signals extraction

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Build the signal extractor that reads each retrospective and produces a structured `RetroSignal` record with 6+ fields: axioms violated, scope expansion (bool), duration delta vs estimate, gate failures count, block kind, block tier. Foundation for pattern detection in block-095.

## 2. Dependencies

- block-086 (need actual_duration_hours field in retros to extract duration delta)

## 3. Files

- **Read:** retro template, sample retros (existing 85), retrospective rubric protocol, arch-v3 design
- **Modify:** —
- **Create:** `sdk/retro_signals.py` (extraction logic), `sdk/retro_signal_schema.py` (dataclass), `sdk/tests/test_retro_signals.py`

## 4. Validation

- Run extractor against existing 85 retrospectives — successful parse rate >95%
- Failures logged to `sdk/_retro_signal_failures.log` (not raised)
- Schema covers: `block_id`, `tier`, `kind`, `phase`, `duration_actual_h`, `duration_estimated_h`, `axioms_violated[]`, `scope_expansion: bool`, `gate_failures: int`, `forced_pass: bool`, `closed_at`
- Test suite with synthetic retros covering each signal type passes

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Older retros have inconsistent format | High | Log failures and skip; never raise; >95% target acknowledges some loss |
| Extracted signals are subtly wrong | Med | Test suite covers known cases; visual spot-check 10 retros after first run |

## 7. Out of Scope

- Pattern detection (block-095)
- Recommendation generation (block-097)
- Cross-project retros (single-project)
- ML/NLP-based extraction (regex + structured parsing sufficient)

## 8. New Abstraction

`RetroSignal` dataclass + extraction module. Justification: 4 distinct consumers planned (pattern_analyzer, patterns_report, recommendation_engine, master_agent dashboards). Far past Rule of Three.
