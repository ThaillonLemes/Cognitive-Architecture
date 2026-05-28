---
id: block-116
tier: M
kind: implementation
phase: phase-18
scope: phase-bound
status: planned
security: false
dependencies:
  - block-113
files:
  read:
    - sdk/pattern_analyzer.py
    - sdk/retro_signals.py
    - governance/token-report.md
  modify:
    - sdk/retro_signals.py
    - sdk/pattern_analyzer.py
  create:
    - sdk/tests/test_token_signals.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: lint-pass
    cmd: python -m flake8 sdk/retro_signals.py sdk/pattern_analyzer.py --max-line-length=120
    expect: "0 errors"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-116-token-analyzer.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-113]
created_at: 2026-05-28
parallel_with: [block-115]
---

# Block 116 — token_analyzer.py Signals

- **Tier:** M
- **Kind:** implementation
- **Status:** planned
- **Parallel-with:** block-115

## 1. Purpose

Extend retro_signals.py to extract token signals (tok_estimated vs tok_actual delta per block). Extend pattern_analyzer.py to detect `budget-overrun-recurring` pattern when token delta > 20% in D1 ≥ 3 blocks. This connects token data into the existing pattern mining pipeline — no new tools, just new signal types and a new pattern detector.

## 2. Dependencies

- block-113: token_tracker.py + token-report.md provides the source data

## 3. Files

- **Read:** sdk/pattern_analyzer.py, sdk/retro_signals.py, governance/token-report.md
- **Modify:** sdk/retro_signals.py — add `extract_token_signals(arch_root)` function; sdk/pattern_analyzer.py — add `detect_budget_overrun(signals)` detector
- **Create:** sdk/tests/test_token_signals.py

## 4. Validation

- Create mock retros with tok_actual > tok_estimated by > 20%; run pattern_analyzer — confirm budget-overrun-recurring detected
- Create mock retros with tok_actual within 20% — confirm pattern NOT detected
- Run full pipeline: `python sdk/pattern_analyzer.py && python sdk/patterns_report.py` — no regression on existing patterns
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, lint-pass, files-updated, dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Token signals pollute existing signal extraction | Low | Token signals use separate prefix (tok_*); existing signal keys unchanged |
| Pattern fires on normal estimation error | Low | 20% threshold; D1 ≥ 3 requirement; same thresholds as existing patterns |

## 7. Out of Scope

- Token signal types beyond over-estimation (under-estimation, zero-actual patterns — future)
- Cross-phase token comparison signals

## 8. New Abstraction

`TokenSignal(block_id, tok_estimated, tok_actual, delta_pct, date)` dataclass added to retro_signals.py. `detect_budget_overrun(token_signals, threshold_pct=20, d1_min=3)` added to pattern_analyzer.py.
