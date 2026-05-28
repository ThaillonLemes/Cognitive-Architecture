---
id: phase-11
status: planned
version: v2.5
prev_phase: phase-10
exit_criteria_count: 5
blocks_count: 5
estimated_duration_days: 3
created_at: 2026-05-23
last_updated: 2026-05-23
owner: implementer
---

# Phase 11 — Project Intelligence

## Purpose

Phase 11 adds measurement and decision-support to the architecture. The architecture currently produces work but does not measure it — how long blocks actually take, which phases are ahead or behind schedule, which Tracks are genuinely improving, and whether the project as a whole is healthy. Phase 11 closes this gap with five tightly scoped blocks: estimation tracking, phase forecasting, a composite health report, Track benchmark formalization, and a hierarchical project memory protocol that separates the three distinct audiences the architecture serves.

## Context

Phases 1–10 established the structural foundation: a block execution loop, Track system, governance tooling, SDK utilities, and a living protocol library. What is missing is the feedback loop that tells the implementer whether the system is working. Without measured velocity, every estimate is a guess. Without benchmark deltas, Track Blocks may iterate without meaningful improvement. Without a health report, the project state is only knowable by reading many files manually. Phase 11 makes the architecture self-aware.

## Exit Criteria

1. `templates/block-retrospective.md` has `actual_duration_hours` field; `commands/velocity.md` exists and calculates S/M/L velocity from BLOCK_LOG + retrospectives; `protocols/estimation-tracking.md` documents the tracking protocol.
2. `commands/phase-forecast.md` exists and uses velocity data to estimate phase completion date with a stated confidence level.
3. `commands/health-report.md` and `sdk/health_report.py` exist; running `python sdk/health_report.py --arch-root . --dry-run` exits 0; the script generates a markdown report with at least 4 sections (audit score, velocity, phase progress, track health).
4. `templates/track-block.md` has `benchmark_before`, `benchmark_after`, and `benchmark_unit` fields; `protocols/track-priority.md` is updated to use benchmark delta for stagnation detection.
5. `protocols/project-memory-layers.md` exists defining 3 layers (Agent Experience, User Experience, Developer Experience); `CLAUDE.md` references it; `protocols/block-close-checklist.md` has a step asking which memory layer the block updated.

## Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-081 | Estimation Tracking & Velocity | S | planned | manifests/block-081-estimation-tracking.md |
| block-082 | Phase Forecast Command | S | planned | manifests/block-082-phase-forecast.md |
| block-083 | Health Report | M | planned | manifests/block-083-health-report.md |
| block-084 | Track Benchmark Tracking | S | planned | manifests/block-084-track-benchmark-tracking.md |
| block-085 | Hierarchical Project Memory | S | planned | manifests/block-085-project-memory-layers.md |

## Dependency Groups

```
11A: [block-081]                       — velocity data foundation
11B: [block-082]  depends_on [11A]     — forecast requires velocity
11C: [block-083]  depends_on [11B]     — health report aggregates forecast + velocity
11D: [block-084]                       — independent; parallel to 11A-C
11E: [block-085]  depends_on [11C, 11D] — memory layers capstone; wires everything together
```

Execution order: start 11A and 11D in parallel. After 11A completes, start 11B. After 11B completes, start 11C. After both 11C and 11D complete, start 11E.

## Recommended Execution Sequence

1. block-081 and block-084 (parallel start — no shared files)
2. block-082 (after block-081)
3. block-083 (after block-082)
4. block-085 (after block-083 and block-084)

## Phase Notes

- Phase 11 introduces the first Python SDK file that generates persistent output artifacts (`governance/health-report-*.md`). Ensure `governance/` directory exists before running block-083.
- The velocity command (block-081) is the keystone dependency: blocks 082, 083, and 085 all depend on its output being reliable. Do not mark block-081 done until at least one retro file with `actual_duration_hours` filled has been verified.
- Track benchmark fields (block-084) are backward-compatible additions to `templates/track-block.md` — existing Track Blocks without these fields are valid; the fields are only required for blocks opened after block-084 is closed.
- Block-085 modifies both `CLAUDE.md` and `protocols/block-close-checklist.md`, which are high-traffic files. Read both immediately before editing to avoid stale-content conflicts.
