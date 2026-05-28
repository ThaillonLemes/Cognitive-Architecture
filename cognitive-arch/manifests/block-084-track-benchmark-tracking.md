---
id: block-084
tier: S
kind: implementation
phase: phase-11
scope: phase-bound
status: planned
dependencies: []
files:
  read:
    - templates/track-block.md
    - protocols/track-block-execution.md
    - protocols/track-priority.md
    - tracks/PRIORITY.md
  modify:
    - templates/track-block.md
    - protocols/track-block-execution.md
    - protocols/track-priority.md
    - tracks/PRIORITY.md
gates:
  - name: template-has-benchmark-before
    type: command
    command: grep -q "benchmark_before" templates/track-block.md
    expect: exit 0
  - name: priority-has-stagnation
    type: command
    command: grep -q "stagnation" protocols/track-priority.md
    expect: exit 0
  - name: files-changed
    type: file-changed
    paths:
      - templates/track-block.md
      - protocols/track-priority.md
created_at: 2026-05-23
---

# block-084 — Track Benchmark Tracking

## Purpose

Formalize benchmark measurement in Track Blocks by adding three fields to the track-block template, making benchmark recording mandatory in the execution protocol, and adding stagnation detection to the Track priority protocol. Without measured benchmarks, a Track Block that runs successfully might have changed nothing meaningful — this block ensures every Track Block produces a verifiable before/after measurement.

## Background

Track Blocks exist to improve a specific quality dimension (e.g., latency, throughput, memory usage, test coverage). Currently the template and execution protocol do not require the implementer to record what the metric was before the block started or what it became after. This means Track improvement is asserted rather than measured. Stagnation — a Track that keeps running blocks without real gains — is invisible. This block adds the minimal structure to make improvement visible and stagnation detectable.

## Implementation Steps

### Step 1 — Read all four files before making any edits

Read `templates/track-block.md`, `protocols/track-block-execution.md`, `protocols/track-priority.md`, and `tracks/PRIORITY.md` in full before modifying any of them.

### Step 2 — Modify `templates/track-block.md`

Locate the frontmatter block. Add three new fields after the existing `tier` or `track` field (whichever comes last in the frontmatter):

```yaml
benchmark_before: ""
benchmark_after: ""
benchmark_unit: ""
```

Field semantics:
- `benchmark_before`: the measured value of the target metric immediately before any code change in this block begins. Must be filled before implementation starts.
- `benchmark_after`: the measured value of the same metric after implementation is complete and verified. Must be filled before the block is closed.
- `benchmark_unit`: the unit and measurement method, e.g. `"ms p99 latency (k6 load test, 100 VUs, 60s)"`, `"req/sec (wrk, 4 threads, 30s)"`, `"MB RSS (process_memory Python, idle)"`, `"% line coverage (pytest-cov)"`. Must be the same measurement method for before and after — changing the method invalidates the comparison.

Backward compatibility note: existing Track Blocks without these fields are valid. The fields are only required for Track Blocks opened after block-084 is closed. When reading older Track Blocks, treat missing fields as empty strings.

Also add a body section if not already present:

```markdown
## Benchmark

| | Before | After | Delta |
|-|--------|-------|-------|
| `<benchmark_unit>` | `<benchmark_before>` | `<benchmark_after>` | `<after - before>` |
```

This section is filled by the implementer at block close.

### Step 3 — Modify `protocols/track-block-execution.md`

Find the step-by-step execution section. Make the following additions mandatory (add as explicit numbered steps or as mandatory sub-steps to existing steps):

**Before any code change (Step 1 or equivalent):**

> **Mandatory: record `benchmark_before`.** Before writing any code or modifying any file, run the benchmark measurement defined in `benchmark_unit` and record the result in `benchmark_before`. If you have not yet defined what you will measure, define it now and record it. Do not begin implementation without this value.

**After implementation is complete and verified (Step 4 or equivalent):**

> **Mandatory: record `benchmark_after`.** Run the same benchmark measurement as `benchmark_before` (same tool, same parameters, same conditions as closely as possible) and record the result in `benchmark_after`. If the measurement conditions changed (e.g., different load, different dataset), note the change in the block retrospective and mark the comparison as approximate.

**At block close:**

> Fill in the `## Benchmark` table in the track-block document with the before, after, and delta values.

### Step 4 — Modify `protocols/track-priority.md`

Add a **Stagnation Detection** section. Insert it after the existing priority scoring section (or at the end if no clear insertion point):

---

### Stagnation Detection

A Track is **STAGNANT** if it has had 3 or more consecutive Track Blocks where `benchmark_after <= benchmark_before` (no improvement or regression). Consecutive means the 3 most recent done Track Blocks for that Track, in close-date order.

**Detection procedure:**

1. For the Track being evaluated, find its last 3 done Track Blocks (by close date in BLOCK_LOG).
2. For each block, compute `delta = benchmark_after - benchmark_before`.
   - If `benchmark_before` or `benchmark_after` is empty (older block without fields), treat delta as 0.
3. If all 3 deltas are ≤ 0: mark the Track as STAGNANT.

**Response to stagnation:**

When a Track is marked STAGNANT:
1. Add a `stagnation_count: <N>` field to the Track entry in `tracks/PRIORITY.md`.
2. Add a note: `# STAGNANT — <N> consecutive non-improving blocks. Review Track scope or measurement method.`
3. Do not open another Track Block for this Track until the stagnation is reviewed. Either:
   a. Redefine the benchmark (if the measurement method is wrong), or
   b. Close the Track (if the target quality dimension has reached its ceiling), or
   c. Change the implementation approach and document why in a decision file.

**Clearing stagnation:**

A Track clears STAGNANT status when a Track Block produces `benchmark_after > benchmark_before`. Reset `stagnation_count` to 0 and remove the STAGNANT note.

---

### Step 5 — Modify `tracks/PRIORITY.md`

Add a `stagnation_count` column to the Track table. Example updated table header:

```markdown
| Track | Priority Score | Last Block | Status | Stagnation Count |
|-------|---------------|------------|--------|-----------------|
```

For all existing rows, set `Stagnation Count` to `0` (no stagnation data yet — backfill as Track Blocks are reviewed).

## Verification

After completing all edits:

```
grep -q "benchmark_before" templates/track-block.md && echo "template PASS" || echo "template FAIL"
grep -q "stagnation" protocols/track-priority.md && echo "protocol PASS" || echo "protocol FAIL"
```

Both must print PASS.
