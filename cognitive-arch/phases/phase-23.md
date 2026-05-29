---
id: phase-23
status: active
prev_phase: phase-22
exit_criteria_count: 5
blocks_count: 5
estimated_duration_minutes: 180
created_at: 2026-05-29
last_updated: 2026-05-29
owner: implementer
---

# Phase 23 — Instrument Repair

BRIEF: Fix the self-observation machinery built in Phases 18–22. A dogfooding pass (pointing the architecture at itself) revealed that its own instruments are broken: `recommendation_engine.py` crashes on Windows, `health_report.py` reports the wrong phase (lexical sort picks phase-9 over phase-22), block counters disagree across four sources, and velocity reads 0 samples despite 49 retros having durations. Phase 23 makes the instruments trustworthy again.

## 1. Purpose

The whole value of cognitive-arch is "the system observes itself and tells you what to do next." Phases 18–22 built that loop (token tracking, patterns, recommendations, proposals, notifications, health, dashboard). When pointed at itself, almost none of it works end-to-end: the recommendation engine crashes, the health report lies about the current phase, velocity is permanently blind, and the learning loop has produced zero proposals. A broken measuring instrument is the highest-leverage fix — until it works, the system cannot honestly prioritize its own future.

## 2. Goals

- CLI smoke-test harness: every `sdk/*.py` runs without crashing (catches the class of bug that shipped a crashing recommendation_engine despite 690 unit tests)
- Fix the two confirmed crashers: `recommendation_engine.py` (UnicodeEncodeError on `→` under cp1252) and `velocity_inference.py` (PermissionError opening `.`)
- Single source of truth (`sdk/project_state.py`): one canonical reader for current phase, block count, and done-list — every tool reads it instead of re-deriving with its own parser
- Fix `health_report.py`: lexical-sort phase bug + block undercount, via the single source of truth
- Fix velocity data pipeline: read durations correctly; surface estimated data with a confidence flag instead of "INSUFFICIENT DATA" forever
- Re-mine patterns over the full 134-block history and confirm the pattern→recommendation→proposal loop fires end-to-end once

## 3. Invariants

- Tool stdout is ASCII-safe by default OR every CLI entry point applies the shared UTF-8 guard (enforced by the smoke test under cp1252)
- `sdk/project_state.py` is the only place that answers "what phase/block are we on"; other tools import it
- No behavior change to passing tools — only fixes to broken ones; all 690 existing tests stay green
- Velocity never claims more confidence than the data supports (estimated ≠ measured)
- Fixes are verified by tests that assert correct values, not just non-crash

## 4. Dependencies

- Phases 18–22 complete (the machinery being repaired)
- No external dependencies; stdlib + pytest only

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Refactoring health/velocity to use project_state breaks their existing tests | Med | Run full suite after each block; project_state returns same shape existing code expects |
| ASCII-only invariant rejected for losing pretty glyphs | Low | Shared UTF-8 guard is the fallback; both satisfy the smoke test |
| "estimated" data policy hides real uncertainty | Med | Confidence flag is explicit (ESTIMATED vs MEASURED); never silently upgrades |
| Smoke test too slow (39 subprocesses) | Low | --help is fast; curated real-runs limited to read-only generators |

## 6. Validation

- `python -m pytest sdk/tests/ -q` — 0 failures (was 690 passing; new tests added)
- `python sdk/recommendation_engine.py --arch-root .` — exits 0 under cp1252
- `python sdk/health_report.py --arch-root .` — reports phase-22/23, correct block count
- `python sdk/velocity_inference.py` — no PermissionError
- `governance/patterns.md` — last-seen block ≥ 130 (full history mined)

## 7. Exit Criteria

1. `sdk/tests/test_cli_smoke.py` runs every `sdk/*.py` under `PYTHONIOENCODING=cp1252` and asserts no traceback; recommendation_engine + velocity_inference are caught before the fix and pass after.
2. `sdk/safe_io.py` provides a shared UTF-8 stdout guard; recommendation_engine.py and velocity_inference.py no longer crash; the `→`-class of bug cannot recur (smoke test enforces).
3. `sdk/project_state.py` exposes canonical `current_phase()`, `completed_block_ids()`, `block_count()` reading STATE.md `p:` + BLOCK_LOG as the single source of truth, with tests.
4. `health_report.py` reports the correct current phase (no lexical-sort bug) and a block count that matches `project_state`, verified by a test asserting phase ≥ 22 on the real arch-root.
5. Velocity surfaces available duration data with an explicit confidence label (ESTIMATED/MEASURED); patterns re-mined over full history (last-seen block ≥ 130); pattern→recommendation→proposal demonstrated end-to-end once.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-135 | CLI smoke-test harness | M | done | `manifests/block-135-cli-smoke.md` |
| block-136 | Fix crashers (UTF-8 + PermissionError) | M | done | `manifests/block-136-fix-crashers.md` |
| block-137 | project_state.py single source of truth | M | done | `manifests/block-137-project-state.md` |
| block-138 | Velocity + BLOCK_LOG parse fix | M | planned | `manifests/block-138-velocity-fix.md` |
| block-139 | Re-mine patterns + close loop | M | planned | `manifests/block-139-close-loop.md` |
