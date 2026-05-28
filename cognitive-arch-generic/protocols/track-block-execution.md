# Track Block Execution Protocol

BRIEF: 6-section execution protocol for Track Blocks. Track Blocks differ from Phase Blocks: they are iterative, can be reopened, and always produce a measurement. The protocol enforces: measure first, hypothesize, implement, measure again, assess honestly.

---

## Key differences from Phase Block execution

| | Phase Block | Track Block |
|--|-------------|------------|
| Can reopen? | No | Yes — if hypothesis fails, block goes back to planned |
| Measurement required? | Only for test gates | Always — before AND after |
| Failure handling | Fix until gates pass | Document failure, state next hypothesis, reopen |
| Exit criteria | Defined gates in manifest | benchmark_after vs. benchmark_before delta |
| Protocol | SPARC (protocols/block-execution-sparc.md) | This protocol |

---

## Section 1 — Pre-implementation measurement (MANDATORY)

**Do this BEFORE writing any code.**

1. Record the current benchmark using the method in `tracks/[system].md` Benchmark Tooling section.
2. Write the value into `benchmark_before:` in the Track Block file.
3. Note the measurement conditions (load, connections, test setup).
4. Take a screenshot or log the raw output — this is your baseline.

**Hard rule:** If you cannot measure `benchmark_before` before changing code, HALT. Do not proceed with implementation until you have a baseline. A Track Block with no `benchmark_before` is invalid.

---

## Section 2 — Hypothesis validation

Read the hypothesis in the Track Block file. Before implementing:

1. Can the hypothesis actually be tested with the current benchmark tooling? If no: update the hypothesis or create benchmarking tooling first.
2. Is the expected improvement realistic? (>50% improvement from a single change is exceptional — flag if so.)
3. Is the scope limited to one mechanism? If the hypothesis involves 3 different changes at once: narrow it. Track Blocks test one hypothesis at a time for clean attribution.

---

## Section 3 — Implementation

Implement the hypothesis. Rules:
- Scope is limited to the system named in the Track file. Do not spread changes across multiple systems.
- Preserve the original code path as a commented-out fallback when possible (in case the change needs to be reverted).
- Write any new code with performance in mind — this is an optimization context, not a feature context.
- If a change requires modifying a public API: HALT. Create a Phase Block for the API change first; the Track Block builds on top of it.

---

## Section 4 — Post-implementation measurement

**After implementation, before closing the block:**

1. Measure using the exact same method and conditions as Section 1.
2. Write the value into `benchmark_after:`.
3. Compute delta: `benchmark_after - benchmark_before`.

**Measurement integrity rules:**
- Same server load, same client count, same test duration.
- Do not cherry-pick the best run — use the median of 3 runs.
- If conditions changed between before and after: note why and acknowledge the comparison may be imprecise.

---

## Section 5 — Result assessment

Assign one of three results:

**IMPROVED:** `benchmark_after` beats `benchmark_target` or shows meaningful improvement toward it (>5% delta in the right direction). Record in `tracks/[system].md` Benchmark History table. Update `last_improved_at`.

**NO CHANGE:** Delta is within noise (±2%). The hypothesis was incorrect or the implementation was too small. Analyze why. State next hypothesis. Reopen the block to planned status with updated hypothesis and increment `reopened_count`.

**REGRESSED:** Performance got worse. Immediately revert the implementation. Record the regression and the reason. State next hypothesis. Do NOT close the block as done — reopen to planned.

---

## Section 6 — Closing a Track Block

A Track Block is **done** only when result is IMPROVED.

**Close steps:**
1. Set `status: done` in the Track Block file.
2. Add entry to `tracks/[system].md` Benchmark History.
3. Update `tracks/[system].md` `last_improved_at`.
4. Update `tracks/PRIORITY.md`: reset `stagnation_count` to 0 for this Track, update current best benchmark.
5. Add entry to `blocks/BLOCK_LOG.md`: `track-block-NNN done YYYY-MM-DD`.

**Reopen steps (NO CHANGE or REGRESSED):**
1. Update hypothesis in Track Block file with new hypothesis.
2. Increment `reopened_count`.
3. Set `status: planned`.
4. Update `tracks/PRIORITY.md`: increment `stagnation_count` if NO CHANGE or REGRESSED.
5. The block is NOT added to BLOCK_LOG until it closes as IMPROVED.

---

## Out of scope

- Changing the Track's benchmark target (that is the Track owner's decision, not the implementer's).
- Creating new Tracks (that is `protocols/track-generation.md`).
- Deciding which Track to work on next (that is `protocols/track-priority.md` and the Governor).

End of track-block-execution.md.
