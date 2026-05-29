---
id: block-135
phase: phase-23
tier: M
status: done
actual_duration_hours: 0.8
duration_source: estimated
tok_actual: 2400
gates_passed: 2/2
created_at: 2026-05-29
---

# Block 135 Retrospective — CLI smoke-test harness

## 1. What was built

- `sdk/tests/test_cli_smoke.py`: runs every `sdk/*.py` as a subprocess under `PYTHONIOENCODING=cp1252` (the user's real Windows console condition)
  - `test_help_no_crash` — parametrized over all 39 tools; `--help` must exit 0 with no traceback
  - `test_real_run_no_crash` — 6 read-only generators run against a throwaway copy of `cognitive-arch-generic`
  - 2 known crashers (`recommendation_engine.py`, `velocity_inference.py`) marked `xfail(strict=True)`

## 2. Gates

- tests-collected: 45 smoke tests run (43 passed, 2 xfailed) ✓
- full suite: 735 passed, 2 xfailed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- **cp1252 forced via env** so the encoding bug reproduces on any OS (not just Windows) — makes the test CI-portable
- **strict xfail** on the 2 crashers: suite is green now; when block-136 fixes them the xfail flips to XPASS (red), forcing removal of the markers — TDD wiring
- `--help` for all tools + curated real-runs for generators: `--help` alone catches both confirmed crashers (recommendation_engine crashes even on --help; velocity_inference too)
- Real-runs use a tmp copy of the generic scaffold so the repo is never dirtied

## 4. Key finding

690 unit tests existed but **none ran the CLIs as the user runs them** — that gap let a crashing recommendation_engine ship. This harness closes that gap permanently.

## 5. DX updated

`sdk/tests/test_cli_smoke.py` created.
