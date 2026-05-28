---
id: block-095
tier: M
kind: implementation
phase: phase-14
scope: phase-bound
status: pending
security: false
dependencies: [block-094]
files:
  read:
    - sdk/retro_signals.py
    - sdk/retro_signal_schema.py
    - design/arch-v3.md
  modify: []
  create:
    - sdk/pattern_analyzer.py
    - sdk/tests/test_pattern_analyzer.py
    - sdk/pattern_schema.py
gates:
  - name: analyzer-module
    type: file-changed
    paths: [sdk/pattern_analyzer.py, sdk/pattern_schema.py]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_pattern_analyzer.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-094]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-095-pattern-analyzer.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 095 — Pattern analyzer

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Consume the stream of RetroSignal records from block-094 and detect patterns. Threshold per D1 (3 occurrences in 30-block window). Produces `Pattern` records each with: name, evidence (block IDs), severity, first_detected, last_detected.

## 2. Dependencies

- block-094 (signal extraction must exist)

## 3. Files

- **Read:** retro_signals output, schemas, arch-v3 design
- **Modify:** —
- **Create:** `sdk/pattern_analyzer.py` (detection rules), `sdk/pattern_schema.py` (Pattern dataclass), `sdk/tests/test_pattern_analyzer.py`

## 4. Validation

- 7+ detection rules implemented: axiom violation frequency, duration overrun (>1.5× estimate), kind-specific gate failure rate, scope expansion clustering, forced-pass clustering, dependency-wait duration anomalies, retro size as proxy for complexity
- Each rule has corresponding test with synthetic signals
- Threshold tunable via constant; default 3 occurrences / 30 blocks per D1

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Too many false-positive patterns | Med | Threshold conservative; severity bands let user filter |
| Rules become hard to maintain | Med | Each rule is a small pure function; isolated; tested individually |

## 7. Out of Scope

- Recommendation generation (block-097)
- Markdown report formatting (block-096)
- ML-based pattern detection (deterministic rules)
- Multi-project patterns (single-project)

## 8. New Abstraction

`Pattern` dataclass. Justification: consumed by report generator, recommendation engine, master agent — clear Rule of Three.
