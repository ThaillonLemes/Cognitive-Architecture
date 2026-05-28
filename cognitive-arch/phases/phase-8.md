---
id: phase-8
status: planned
version: v2.2
prev_phase: phase-7
exit_criteria_count: 6
blocks_count: 6
estimated_duration_days: 3
created_at: 2026-05-23
last_updated: 2026-05-23
owner: implementer
---

# Phase 8 — Quality of Planning (v2.2)

BRIEF: Add explicit, measurable protocols that control the quality of planning artifacts. Currently the AI generates phases and blocks by intuition with no rubric. Phase 8 changes that by introducing a Phase Quality Rubric, a Domain→Phase Bridge protocol, a SPARC intra-block execution sequence, a Block Complexity Estimator, a semantic Retrospective Rubric, and a Commands Integration pass that wires everything together.

---

## 1. Purpose

Planning quality has been tacit: each phase and block is generated ad hoc, with no checklist to catch vague exit criteria, no heuristic for tier assignment, and no protocol for how to execute within a block. This phase makes planning quality explicit and verifiable. Every subsequent phase generated after Phase 8 must pass the Phase Quality Rubric before work begins; every block must be assigned a tier using the Complexity Estimator; every M/L block must follow the SPARC sequence; and every retrospective must satisfy the semantic Retrospective Rubric before a block can be closed.

---

## 2. Goals

1. Establish a measurable checklist (Phase Quality Rubric) that any generated phase must satisfy.
2. Provide a step-by-step protocol (Domain→Phase Bridge) for translating design/ domain knowledge into well-structured phases.
3. Define a five-step intra-block execution protocol (SPARC) that prevents scope creep and ensures architecture consistency.
4. Give the implementer an objective heuristic (Block Complexity Estimator) for assigning S/M/L tiers rather than guessing.
5. Raise retrospective quality from "something was written" to "something useful was captured," via a five-criterion semantic rubric enforced by the SDK validator.
6. Integrate all new protocols into the four primary command files so they are triggered automatically during normal workflow.

---

## 3. Invariants

- No protocol file may reference another protocol that does not yet exist within this phase or a prior phase.
- The SPARC protocol is mandatory for M and L tier blocks; it is recommended but not mandatory for S tier blocks.
- The Phase Quality Rubric must be checked before any phase is accepted, including phases generated after Phase 8.
- The Complexity Estimator must be consulted before any new block manifest is written.
- Retrospective rubric failures produce warnings, not hard errors, so they never block a gate pass.
- All command file modifications must be additive: existing steps must not be removed, only extended.

---

## 4. Dependencies

- **Phase 7 (SDK Depth, blocks 051–060):** `sdk/return_validator.py` must exist. Block 065 modifies it.
- **`commands/block-start.md`:** must exist. Blocks 063 and 066 modify it.
- **`commands/block-close.md`:** must exist. Block 066 modifies it.
- **`commands/phase-start.md`:** must exist. Blocks 061 and 066 modify it.
- **`commands/phase-close.md`:** must exist. Block 066 modifies it.
- **`design/`:** must contain at least one documented system for block-062 to reference meaningfully.

---

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Phase Quality Rubric is too strict and rejects well-structured phases | Medium | Medium | Calibrate criteria against existing phases 1–7; adjust thresholds if needed |
| SPARC protocol adds overhead that slows down S-tier blocks | Low | Low | SPARC is recommended, not mandatory, for S blocks |
| `return_validator.py` test suite breaks due to new rubric function | Medium | High | Block 065 includes ≥5 new tests; pytest must pass before block closes |
| Commands integration (block-066) causes conflicts with existing steps | Low | Medium | All modifications are additive; existing content is preserved |
| Domain→Phase Bridge protocol is ignored if design/ is sparse | Medium | Medium | Protocol includes readiness precondition check before invocation |
| Semantic rubric criteria are ambiguous and produce inconsistent results | Medium | Medium | Each criterion is expressed as a detectable text pattern, not a judgment call |

---

## 6. Validation

- All six protocol files listed in the block index exist on disk after phase completion.
- `python -m pytest sdk/tests/test_return_validator.py -q` passes with no failures.
- Each of the four command files (`block-start.md`, `block-close.md`, `phase-start.md`, `phase-close.md`) contains at least one reference to a Phase 8 protocol.
- `protocols/phase-quality-rubric.md` contains at least 8 numbered criteria that are each testable or verifiable.
- `protocols/block-complexity-estimator.md` contains a decision tree with at least 3 criteria per tier (S/M/L).
- `protocols/block-execution-sparc.md` defines all five SPARC phases with entry and completion conditions.

---

## 7. Exit Criteria

1. `protocols/phase-quality-rubric.md` exists with ≥8 measurable criteria.
2. `protocols/domain-phase-bridge.md` exists with explicit step-by-step protocol referencing `design/`.
3. `protocols/block-execution-sparc.md` exists with all 5 SPARC phases defined; `commands/block-start.md` references it.
4. `protocols/block-complexity-estimator.md` exists with tier decision tree (S/M/L with ≥3 criteria per tier).
5. `protocols/retrospective-rubric.md` exists; `sdk/return_validator.py` has `validate_rubric()` function with semantic checks; `pytest sdk/tests/ -q` passes.
6. `commands/block-start.md`, `commands/block-close.md`, `commands/phase-start.md`, `commands/phase-close.md` all reference new Phase 8 protocols.

---

## 8. Block Index

| Block ID | Title | Tier | Status | Manifest |
|---|---|---|---|---|
| block-061 | Phase Quality Rubric | S | planned | `manifests/block-061-phase-quality-rubric.md` |
| block-062 | Domain→Phase Bridge | S | planned | `manifests/block-062-domain-phase-bridge.md` |
| block-063 | SPARC Intra-Block Protocol | S | planned | `manifests/block-063-sparc-intra-block.md` |
| block-064 | Block Complexity Estimator | S | planned | `manifests/block-064-block-complexity-estimator.md` |
| block-065 | Retrospective Rubric Semantic | M | planned | `manifests/block-065-retrospective-rubric-semantic.md` |
| block-066 | Commands Integration | S | planned | `manifests/block-066-commands-integration.md` |

---

## 9. Dependency Graph & Parallel Execution Plan

```yaml
phase: phase-8
groups:
  - id: 8A
    label: "Foundation — Rubric First"
    blocks: [block-061]
    depends_on: []
    note: "Phase Quality Rubric must exist before any other block can reference rubric concepts."

  - id: 8B
    label: "Protocol Layer — Builds on Rubric"
    blocks: [block-062, block-063, block-064]
    depends_on: [8A]
    note: >
      All three blocks in 8B can execute in parallel once 8A is complete.
      block-062 (Domain→Phase Bridge) reads phase-quality-rubric.md.
      block-063 (SPARC) modifies commands/block-start.md.
      block-064 (Complexity Estimator) depends conceptually on SPARC tiers but not on block-063 output file.
      If executing sequentially: 062 → 063 → 064 (all S-tier, fast).

  - id: 8C
    label: "Semantic Validation"
    blocks: [block-065]
    depends_on: [8B]
    note: >
      Retrospective Rubric semantic implementation is M-tier and touches SDK code.
      Requires block-064 complete so complexity criteria are understood.
      Must not start until all 8B blocks are closed.

  - id: 8D
    label: "Integration"
    blocks: [block-066]
    depends_on: [8A, 8B, 8C]
    note: >
      Commands Integration wires all Phase 8 protocols into command files.
      Depends on all prior blocks being closed so references are accurate.
      Final block in phase; its completion triggers phase exit criteria check.

parallel_slots: 3
critical_path: [block-061, block-062, block-065, block-066]
estimated_sequential_days: 3
estimated_parallel_days: 2
```

---

## 10. Out of Scope

- Retroactively applying the Phase Quality Rubric to phases 1–7. Existing phases are not re-evaluated.
- Automated CI/CD enforcement of the Phase Quality Rubric. The rubric is a manual or AI-assisted checklist, not a pipeline gate.
- Rewriting any existing protocol files from phases 1–7. All changes to prior-phase files are additive only.
- Adding the SPARC protocol to existing closed blocks. SPARC applies only to blocks opened after Phase 8 completes.
- Machine-readable schema validation of manifest YAML front-matter. Out of scope for this phase; may be addressed in a future phase.
- Translating the Complexity Estimator into an automated script. The estimator is a human/AI decision tree, not a code tool.

---

End of phase-8.md.
