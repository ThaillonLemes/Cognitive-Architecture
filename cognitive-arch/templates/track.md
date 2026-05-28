---
id: track/[system-name]
system: [System Name]
description: [One-line description of what this system does]
created_at: YYYY-MM-DD
last_improved_at: YYYY-MM-DD
benchmark_target: [e.g., "p99 latency < 5ms", "throughput > 10K req/s"]
benchmark_unit: [e.g., "ms", "req/s", "entities/chunk", "%"]
priority_score: 5
stagnation_count: 0
---

# Track: [System Name]

## System Overview

[2-3 sentences: what this system does, why it matters for the project, what users experience when it works well vs. poorly.]

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| [metric name] | [target value] | [current value] | YYYY-MM-DD |

## Benchmark History

Track Block improvements recorded here, newest first.

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| track-block-NNN | YYYY-MM-DD | [what we tried] | [value] | [value] | IMPROVED / NO CHANGE / REGRESSED |

## Open Hypotheses

Ideas not yet tested, ordered by expected impact:

1. [Hypothesis]: [Why we think this will improve the metric]
2. [Hypothesis]: [Why we think this will improve the metric]

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 5 | [Is this the current server bottleneck?] |
| stagnation_score | 0 | [How many consecutive failed Track Blocks?] |
| user_priority | 5 | [How important to user experience?] |
| **total_priority** | **25** | bottleneck×3 + stagnation×1 + user_priority×2 |

## Technical Context

[Key architectural facts about this system that an implementer needs to know before starting a Track Block. Include: where the code lives, what the main data structures are, what the bottleneck was last time, what tools are used for benchmarking.]

## Benchmark Tooling

How to measure this system's performance:

```bash
# [Command to run benchmark]
# Expected output format: [describe what the output looks like]
```

End of track template.
