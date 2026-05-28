---
id: track-block-NNN
track: track/[system-name]
phase: perpetual
status: planned
hypothesis: "[What we believe will improve the benchmark, and why]"
benchmark_target: "[specific value to beat, e.g., p99 < 5ms]"
benchmark_before: ""
benchmark_after: ""
benchmark_unit: "[e.g., ms, req/s, MB]"
result: ""
reopened_count: 0
created_at: YYYY-MM-DD
last_updated: YYYY-MM-DD
---

# Track Block NNN — [System Name]: [Short hypothesis title]

- **Track:** [System Name]
- **Status:** planned
- **Reopened:** 0 times

## Hypothesis

[What we believe will improve the benchmark. Be specific: "Switching from synchronous lock to lock-free ring buffer will reduce p99 latency by reducing contention under load."]

**Expected improvement:** [e.g., "p99 from 12ms → <8ms"]

## Benchmark Before

> Fill this section BEFORE making any code changes.

- **Method:** [How to measure — exact command or procedure]
- **Value:** [Measured value] [unit]
- **Conditions:** [Server load, number of connections, etc. at time of measurement]
- **Measured on:** YYYY-MM-DD

```bash
# Benchmark command
[command]
# Output:
[output]
```

## Implementation

[What was changed to implement the hypothesis. Be specific about files, functions, algorithms.]

**Files modified:**
- [file path]: [what changed]

## Benchmark After

> Fill this section AFTER implementation and BEFORE closing the block.

- **Method:** [Same as before — must be identical measurement conditions]
- **Value:** [Measured value] [unit]
- **Conditions:** [Same conditions as before]
- **Measured on:** YYYY-MM-DD

```bash
# Benchmark command (same as before)
[command]
# Output:
[output]
```

## Result

> One of: IMPROVED / NO CHANGE / REGRESSED

**Result:** [IMPROVED / NO CHANGE / REGRESSED]

**Delta:** [benchmark_after] - [benchmark_before] = [delta] [unit]

**Analysis:** [Why did the result happen? If IMPROVED: what caused the improvement? If NO CHANGE: what assumption was wrong? If REGRESSED: what went wrong and is it recoverable?]

## Next Hypothesis

> Fill if result is NO CHANGE or REGRESSED — what to try next.

[Next hypothesis based on what we learned from this attempt.]

## Benchmark Summary

| | Before | After | Delta |
|-|--------|-------|-------|
| `[benchmark_unit]` | `[benchmark_before]` | `[benchmark_after]` | `[after - before]` |

Fill this table at block close using the measured values from the Benchmark Before and After sections.

## Rubric Check (advisory)

- [ ] benchmark_before measured before any code changes
- [ ] Same measurement conditions for before and after
- [ ] Implementation described specifically enough to reproduce
- [ ] Result honestly assessed (don't round down a NO CHANGE to IMPROVED)
- [ ] Next hypothesis stated if result is not IMPROVED

End of track-block template.
