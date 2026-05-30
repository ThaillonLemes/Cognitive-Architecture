---
id: block-150
phase: phase-26
tier: M
status: done
actual_duration_hours: 0.7
duration_source: estimated
gates_passed: 3/3
created_at: 2026-05-30
---

# Block 150 Retrospective — Risk-at-block-start forecaster

## 1. What was built

- `sdk/risk_forecast.py` — `RiskFlag(heuristic, severity, rationale, fired)` +
  `assess(manifest_path, arch_root) -> list[RiskFlag]` (advisory; never raises, never
  blocks, always exits 0). 4 heuristics:
  1. **scope-expansion-resemblance** — modify+create ≥7, OR block in historical cluster
     {052-057, 086, 094, 097}, OR shares ≥2 files with live R4 evidence.
  2. **l-tier-overrun-history** — tier L + R7 active; honors MEASURED/ESTIMATED (silent on thin history).
  3. **oversized-modify-list** — exceeds tier ceiling (S=4/M=8/L=20) → suggests split.
  4. **immutable-file-touch** — modify list includes a `protection: immutable` file.
- `sdk/tests/test_risk_forecast.py` — 15 tests (bad manifest flags, good manifest clean,
  never-raises, CLI exit 0).

## 2. Gates

- tests-pass: 922 passed, 0 failed (15 new) ✓
- forecast-cli-clean: `risk_forecast.py <manifest> --arch-root .` exits 0, prints flags/"no risks" ✓
- never-raises: assessed all 24 repo manifests, never raised ✓

## 3. Validation against real data

`SCOPE_EXPANSION_CLUSTER` confirmed to match the live R4 evidence set the pipeline emits.
Sample: `block-029` → ELEVATED: oversized-modify-list (6 > tier-S 4) + immutable-file-touch
(_syntax.md). The architecture can now warn about a risky block at its START, not just
diagnose it at close — the first forward-looking signal.

## 4. Files actually touched

`sdk/risk_forecast.py`, `sdk/tests/test_risk_forecast.py` created.
