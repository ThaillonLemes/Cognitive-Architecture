---
id: phase-9
status: planned
version: v2.3
prev_phase: phase-8
exit_criteria_count: 9
blocks_count: 9
estimated_duration_days: 5
created_at: 2026-05-23
last_updated: 2026-05-23
owner: implementer
---

# Phase 9 — Macro Control

## Purpose

Phase 9 extends the cognitive architecture with two orthogonal macro-control capabilities that address the long-term lifecycle of any non-trivial software project.

**9A — Roadmap as Living Document** (blocks 067–071) solves the problem that phases are generated once and never audited as a coherent set. Over time, the design/ corpus grows and diverges from the phase list, producing hidden coverage gaps and silent scope drift. Phase 9A introduces a ROADMAP.md master document, a Domain Coverage Matrix, a Readiness Gate that prevents premature phase generation, a periodic roadmap-audit command, and a roadmap-refresh command that proposes updates without auto-applying them.

**9B — Forever Software / Track System** (blocks 072–075) formalises the reality that certain software categories — MMORPGs, simulation engines, trading platforms — never reach a terminal "done" state. Individual subsystems must improve perpetually. Phase 9B introduces Tracks: perpetual domain improvement streams that are structurally distinct from delivery Phases. Tracks have benchmark targets instead of exit criteria, Track Blocks that are iterative and reopenable, a priority protocol driven by bottleneck data, and parallel dispatch via the Governor.

## Goals

1. Every project using this architecture can generate and maintain a living ROADMAP.md that stays current as design/ evolves.
2. Coverage gaps (systems with no phase, phases with no design concept, stale phases) are detectable on demand and in periodic audits.
3. Phase generation is gated on domain readiness, preventing skeleton phases built on under-specified concepts.
4. The roadmap can propose its own updates, but never self-modify — all changes are human-confirmed.
5. Systems that require perpetual improvement are tracked as Tracks, not as phases, preventing false "completion" signals.
6. Track priority is data-driven (bottleneck scores) and transparent.
7. The Governor can dispatch Track work in parallel with Phase work without regression.

## Invariants

- The roadmap-refresh command MUST output proposals only. It MUST NOT create or modify any phase file without explicit human confirmation.
- A Readiness Gate failure MUST produce a questionnaire and MUST NOT produce a phase outline.
- Track Blocks are cyclically reopenable. A Track is never marked "done."
- The Governor's existing phase-dispatch code path is not modified by block-075; only new flags are added.
- All SDK tests must pass after block-075 is merged (regression gate).

## Dependencies

- Phase 8 (blocks 051–060) must be complete before Phase 9 begins.
- `protocols/phase-generation.md` must exist (Phase 9 modifies it at block-069).
- `sdk/governor.py` and `sdk/dispatch.py` must exist (Phase 9 extends governor at block-075).

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| roadmap-refresh auto-applies changes despite PROPOSAL constraint | Low | High | block-071 gate checks grep for "PROPOSAL" and "Human must review" strings |
| Readiness Gate too strict — blocks legitimate early projects | Medium | Medium | Gate criteria are explicit and documented; questionnaire gives targeted feedback |
| Track Blocks reopening causes infinite loops in Governor dispatch | Low | High | Governor reads open blocks only; closed blocks are archived to improvement_history |
| block-075 introduces regression in existing SDK tests | Medium | High | Regression gate: `pytest sdk/tests/` must pass as exit criterion 9 |
| Coverage matrix false positives (STALE flags on unchanged phases) | Medium | Low | STALE detection compares design/ file last_updated against phase last_updated |

## Validation

Each exit criterion maps to at least one block gate. The final regression check (exit criterion 9) is enforced by block-075's pytest gate, which must pass before Phase 9 is considered complete.

## Exit Criteria

1. `templates/roadmap.md` and `protocols/roadmap-generation.md` exist; roadmap template contains a domain-coverage section.
2. `protocols/domain-coverage-matrix.md` and `commands/coverage-check.md` exist with a complete audit procedure covering all three gap types (UNCOVERED, DRIFT, STALE).
3. `protocols/readiness-gate.md` exists with at least 4 readiness criteria and a questionnaire-trigger rule; `templates/readiness-questionnaire.md` exists; `protocols/phase-generation.md` references the readiness gate as Step 0.
4. `commands/roadmap-audit.md` exists with a step-by-step audit procedure covering all three coverage dimensions (Coverage, Sequencing, Completeness) plus Forever Tracks dimension.
5. `commands/roadmap-refresh.md` exists and contains explicit "propose, do not auto-apply" clause plus "Human must review and confirm" language.
6. `tracks/README.md`, `templates/track.md`, and `protocols/track-generation.md` exist; track template contains a `benchmark_target` field.
7. `templates/track-block.md` (structurally distinct from phase block template) and `protocols/track-block-execution.md` exist.
8. `protocols/track-priority.md` and `tracks/PRIORITY.md` exist; priority formula is documented and driven by bottleneck data.
9. `python sdk/governor.py --track NAME --dry-run` exits 0; `pytest sdk/tests/` passes with no regressions.

## Block Index

| Block ID | Title | Tier | Status | Manifest |
|----------|-------|------|--------|----------|
| block-067 | Roadmap Structure & Template | S | planned | manifests/block-067-roadmap-structure.md |
| block-068 | Domain Coverage Matrix | S | planned | manifests/block-068-domain-coverage-matrix.md |
| block-069 | Readiness Gate | S | planned | manifests/block-069-readiness-gate.md |
| block-070 | Roadmap Audit Command | S | planned | manifests/block-070-roadmap-audit-command.md |
| block-071 | Roadmap Refresh Command | S | planned | manifests/block-071-roadmap-refresh-command.md |
| block-072 | Track Structure & Template | S | planned | manifests/block-072-track-structure.md |
| block-073 | Track Block Protocol | S | planned | manifests/block-073-track-block-protocol.md |
| block-074 | Track Priority Protocol | S | planned | manifests/block-074-track-priority.md |
| block-075 | Parallel Track Dispatch | M | planned | manifests/block-075-parallel-track-dispatch.md |

## Dependency Graph

```
9A — Roadmap Foundation
  block-067 (Roadmap Structure & Template)
      |
  block-068 (Domain Coverage Matrix)
      |
  block-069 (Readiness Gate)
      |
  block-070 (Roadmap Audit Command)
      |
  block-071 (Roadmap Refresh Command)
      |
      +---------------------------------------+
                                              |
9B — Track System                             |
  block-072 (Track Structure & Template)      |
      |                                       |
  block-073 (Track Block Protocol)            |
      |                                       |
  block-074 (Track Priority Protocol)         |
      |                                       |
      +---------------------------------------+
                      |
                block-075 (Parallel Track Dispatch)
                [regression gate — must not break existing tests]
```

Dependency groups summary:
- Group 9A: block-067 — no upstream dependencies; first block of roadmap stream.
- Group 9B: block-068, block-069 — depend on block-067 (roadmap template must exist first).
- Group 9C: block-070, block-071 — depend on block-068 and block-069.
- Group 9D: block-072 — no upstream dependencies; track stream is independent of roadmap stream.
- Group 9E: block-073, block-074 — depend on block-072.
- Group 9F: block-075 — depends on block-071 (roadmap complete) and block-074 (track structure complete); acts as combined regression gate.

## Out of Scope

- Automatic phase file creation or modification triggered by the roadmap-refresh command. All changes are proposals only.
- UI or dashboard for the coverage matrix. This phase produces markdown commands only.
- Cross-project roadmap federation (multiple repositories sharing one ROADMAP.md).
- Track benchmarking infrastructure (profilers, CI integration). Phase 9 defines the protocol; instrumentation is a future phase.
- Automatic track prioritisation without human-provided bottleneck scores. The Governor reads scores set by the human; it does not derive them.
- Removal or replacement of the existing phase-block model. Track Blocks are additive; phase blocks are unchanged.
