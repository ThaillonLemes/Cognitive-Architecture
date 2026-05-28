---
id: block-073
tier: S
kind: protocol
phase: phase-9
scope: phase-bound
status: planned
dependencies:
  - block-072
files:
  read:
    - templates/track.md
  modify: []
  create:
    - templates/track-block.md
    - protocols/track-block-execution.md
gates:
  - name: track-block-template-exists
    type: file-changed
    paths: [templates/track-block.md]
  - name: track-block-execution-protocol-exists
    type: file-changed
    paths: [protocols/track-block-execution.md]
created_at: 2026-05-23
---

# block-073 — Track Block Protocol

## Purpose

A Track Block is the unit of work for a Track. It is structurally distinct from a Phase Block in two critical ways:

1. **It is cyclically reopenable.** A Phase Block transitions from planned → wip → complete and stays complete. A Track Block transitions from planned → wip → measured, and after measurement can return to planned — representing a new iteration of the improvement loop. The Track itself is never done, and its blocks reflect that.

2. **It is hypothesis-driven.** Every Track Block begins with a hypothesis about why the system is not at its benchmark target. The hypothesis is tested through implementation. The result — whether confirming or refuting the hypothesis — is recorded. This distinguishes Track work from unbounded "make it better" work, which is unverifiable.

This block delivers:

1. `templates/track-block.md` — the Track Block manifest template. It differs from the phase block template in structure, lifecycle, and required fields.
2. `protocols/track-block-execution.md` — the execution protocol for Track Blocks: how to set one up, run it, measure results, and record outcomes.

## Dependencies

- **block-072** must be complete. `templates/track.md` must exist because the Track Block template references Track fields (benchmark_before, benchmark_after must match the Track's benchmark_unit).

## Files

### Read
- `templates/track.md` — to understand the benchmark_unit and improvement_history table structure that Track Blocks feed into.

### Modify
None.

### Create

**`templates/track-block.md`**

Must contain:

```
---
id: TRK-[NNN]-BLK-[MMM]
track_id: TRK-[NNN]
system: [System Name]
type: track-block
phase: N/A
status: planned
benchmark_before: [value] [unit]
benchmark_after: [value] [unit]
benchmark_target: [value] [unit]
benchmark_unit: [unit of measurement]
hypothesis: "[One sentence: what change do we think will improve performance and why?]"
result: pending
result_notes: ""
improvement_delta: 0
improvement_delta_pct: 0.0
reopened_count: 0
created_at: YYYY-MM-DD
last_updated: YYYY-MM-DD
owner: implementer
---

# Track Block: TRK-[NNN]-BLK-[MMM] — [Short Title]

## Track Reference

- Track: [System Name] (`tracks/[system-slug].md`)
- Track ID: TRK-[NNN]
- Current benchmark target: [value] [unit]

## Benchmark State

| Dimension | Value |
|-----------|-------|
| Benchmark before | [value] [unit] |
| Benchmark target | [value] [unit] |
| Benchmark after | [value] [unit] ← filled after execution |
| Delta | [+/-N] [unit] (0%) ← filled after execution |

## Hypothesis

> [One sentence: what do we believe is limiting performance, and what specific change do we hypothesise will improve it?]

**Confidence**: [Low / Medium / High]

**Evidence for hypothesis**:
[What data, profiling results, or observations support this hypothesis?]

**Predicted outcome**:
[What specific benchmark improvement do we predict if the hypothesis is correct? E.g., "We expect latency to drop from 42ms to 35ms."]

## Implementation Plan

[Describe what will be changed to test the hypothesis. Be specific: file paths, algorithms, data structures, parameters.]

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Execution Notes

[Filled during execution. Record observations, surprises, deviations from the plan.]

## Result

**Status**: [pending | confirmed | refuted | inconclusive]

**Benchmark after**: [value] [unit]

**Delta**: [+/-N] [unit] ([+/-N%])

**Result notes**:
[If confirmed: "Hypothesis confirmed. [System] improved from [before] to [after]. Committed to improvement_history." ]
[If refuted: "Hypothesis refuted. Change did not improve [metric]. [What we observed instead.] New hypothesis: [next hypothesis to test]."]
[If inconclusive: "Results were inconclusive because [reason]. The benchmark varied between [min] and [max]. Will retry with [more controlled conditions]."]

## Next Action

[One of:]
- CLOSE: Benchmark target achieved. Track Block closed. No further iteration needed.
- REOPEN: Hypothesis [confirmed|refuted|inconclusive]. Reopen with new hypothesis: [next hypothesis]. See Block TRK-[NNN]-BLK-[MMM+1].
- ESCALATE: Results require human decision. [What decision is needed?]

## Lifecycle

```
planned → wip → measured → [planned (reopen) | closed]
```

This block has been reopened [N] time(s). Each reopen increments reopened_count.

## Dependencies

[List of any Phase Blocks or Track Blocks that must be complete before this Track Block can begin.]

- [TRK-NNN-BLK-MMM or block-NNN: reason]
```

---

**`protocols/track-block-execution.md`**

Must contain:

**Purpose**: Define the end-to-end execution protocol for a Track Block, from creation to closing or reopening.

**Section 1 — Pre-execution Setup**

Before beginning a Track Block:

1. Read the parent Track file (`tracks/[system-slug].md`). Record the current benchmark_target and benchmark_unit.
2. Measure the current benchmark. Run the measurement procedure defined in the Track file's Benchmark Unit section. Record the value as benchmark_before.
3. Open the Track Block file. Fill in: benchmark_before, benchmark_target, benchmark_unit.
4. Write the hypothesis. The hypothesis must be a single sentence of the form: "We believe [specific change] will improve [metric] from [current] toward [target] because [evidence]." Do not begin execution until the hypothesis is written.
5. Set status to wip.

**Section 2 — Execution**

1. Implement the change described in the Implementation Plan.
2. Record execution notes as work proceeds. Note surprises, deviations, and intermediate measurements.
3. Do not change the hypothesis after execution begins. If execution reveals the hypothesis was wrong before measuring, record this in result_notes and mark result as refuted.

**Section 3 — Measurement**

1. Run the measurement procedure from the Track file's Benchmark Unit section. Take at least 3 measurements and use the median value as benchmark_after.
2. Compute improvement_delta: benchmark_after - benchmark_before (sign convention: positive = improvement for throughput/score metrics; negative = improvement for latency/time metrics).
3. Compute improvement_delta_pct: (improvement_delta / benchmark_before) × 100.
4. Set status to measured.

**Section 4 — Result Classification**

Classify the result:

- **Confirmed**: improvement_delta is in the predicted direction AND improvement_delta_pct ≥ 5%. The hypothesis was correct and produced meaningful improvement.
- **Refuted**: improvement_delta is NOT in the predicted direction, or improvement_delta_pct < 5% in the correct direction. The hypothesis was wrong or the change had negligible effect.
- **Inconclusive**: The measurement variance is greater than the improvement_delta (the signal is too noisy to conclude). Must retry under more controlled conditions.

**Section 5 — Post-measurement Actions**

If result is **Confirmed**:
1. Commit the change to the codebase.
2. Add a row to the Track file's Improvement History table: date, block ID, benchmark_before, benchmark_after, delta, notes.
3. Update `last_improved_at` in the Track file frontmatter.
4. If benchmark_after >= benchmark_target: raise the target. Set current_benchmark_target to (benchmark_after × 1.20) and write a note in the Track file's Benchmark Target section. Create a new Track Block (next ID) with the new hypothesis.
5. If benchmark_after < benchmark_target: create a new Track Block with a new hypothesis targeting the remaining gap.
6. Set this block's status to closed (or measured if it will be referenced historically).
7. Set Next Action to CLOSE.

If result is **Refuted**:
1. Do NOT commit the implementation change to the codebase. Revert it.
2. Record in result_notes: what was tried, what was expected, what was observed.
3. Update the Track file's Open Hypotheses: remove the refuted hypothesis, add a new one based on what was learned.
4. Increment reopened_count.
5. Set Next Action to REOPEN.
6. Create a new Track Block (next ID) with the new hypothesis.

If result is **Inconclusive**:
1. Record measurement conditions and variance in result_notes.
2. Determine whether the measurement environment can be improved (more samples, less noise, isolated test).
3. If environment can be improved: REOPEN with same hypothesis, better measurement protocol.
4. If environment cannot be improved: ESCALATE to human to decide whether to accept the result as Confirmed, Refuted, or to invest in better measurement infrastructure.

**Section 6 — Block ID Convention**

Track Block IDs follow the pattern: TRK-[NNN]-BLK-[MMM] where:
- NNN is the Track ID (zero-padded to 3 digits).
- MMM is the block sequence number within the Track (zero-padded to 3 digits, increments with each new block including reopens).

Example: Track TRK-002's third block is TRK-002-BLK-003.

## Validation

- `templates/track-block.md` exists and is structurally distinct from any phase block template (no exit_criteria field; has benchmark_before, benchmark_after, hypothesis, result fields).
- `templates/track-block.md` contains a lifecycle section showing the cyclical status flow.
- `templates/track-block.md` contains reopened_count field.
- `protocols/track-block-execution.md` exists and defines all 6 sections.
- Section 5 (Post-measurement Actions) covers all three result types: Confirmed, Refuted, Inconclusive.
- The protocol specifies that refuted hypotheses result in reverting the implementation change.

## Gates

| Gate | Type | Path(s) | Condition |
|------|------|---------|-----------|
| track-block-template-exists | file-changed | templates/track-block.md | File must exist and contain benchmark_before, benchmark_after, hypothesis fields |
| track-block-execution-protocol-exists | file-changed | protocols/track-block-execution.md | File must exist and define ≥6 sections |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Track Block reopening produces an infinite loop (hypothesis always refuted) | Medium | Medium | Refuted hypotheses require a NEW hypothesis — the same hypothesis cannot be re-run without modification; this forces forward progress |
| benchmark_unit inconsistency between Track file and Track Block | Low | Medium | Section 1 Step 1 requires reading the Track file before setting benchmark_unit; both files must agree |
| Inconclusive results accumulate without resolution | Medium | Low | Section 5 Inconclusive path includes an ESCALATE option; Inconclusive blocks cannot be silently closed |

## Out of Scope

- Automated benchmark measurement. The protocol defines when to measure; the measurement tool or script is project-specific.
- Statistical significance testing for measurement results. The 5% threshold in Section 4 is a practical heuristic, not a formal statistical test.
- Version control integration (e.g., auto-committing confirmed Track Block results). The protocol says "commit"; the mechanism is outside scope.
