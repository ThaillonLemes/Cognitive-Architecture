# Tracks — Perpetual Domain Improvement

## What is a Track?

A Track is a perpetual improvement stream for one major system of the project. Tracks are fundamentally different from Phases:

| | Phases | Tracks |
|--|--------|--------|
| **Goal** | Build the software | Improve the software |
| **Duration** | Finite (has exit criteria) | Infinite (has benchmark targets) |
| **Done?** | Yes — phases complete | Never — Tracks only improve |
| **Blocks** | Deliver a feature | Measure → hypothesize → implement → measure |
| **Order** | Sequential by dependency | Parallel and priority-driven |
| **Trigger** | Phase plan | Bottleneck data or user priority |

## When does a system get a Track?

A system qualifies for a Track when it meets at least one of:
- It directly affects performance, latency, or scalability that users can observe
- It benefits from iterative benchmarking (not one-time implementation)
- It will receive meaningful improvements in every major version
- It has a measurable benchmark (e.g., p99 latency, throughput, error rate)

Examples (MMORPG):
- ✅ Networking (latency, packet loss) → Track
- ✅ Replication (consistency, sync speed) → Track
- ✅ Combat engine (tick rate, collision accuracy) → Track
- ✅ World loading (density, streaming speed) → Track
- ❌ UI skin system (not performance-critical) → Phase, not Track
- ❌ Settings page (not iteratively benchmarked) → Phase, not Track

## How Tracks work

1. **Create** a Track from `templates/track.md` → save to `tracks/[system-name].md`
2. **Set** an initial benchmark target (realistic, measurable)
3. **Prioritize** via `tracks/PRIORITY.md` (Governor picks highest-priority Track)
4. **Execute** Track Blocks from `templates/track-block.md` — measure, hypothesize, implement, measure again
5. **Record** benchmark_before and benchmark_after in each Track Block
6. **Update** `tracks/PRIORITY.md` after each completed Track Block

## Track Block lifecycle (different from Phase Block)

```
planned → wip → measured → [improved? → done] or [not improved? → planned again]
```

Track Blocks CAN be reopened. If a hypothesis failed (no improvement), document why and state the next hypothesis. The block goes back to planned with updated hypothesis.

## This directory

Each `tracks/[system-name].md` file is one Track document.
`tracks/PRIORITY.md` is the Governor's priority table — which Track to work on next.
`tracks/_placeholder.md` keeps this directory in git when no Tracks exist yet.

For generation protocol: `protocols/track-generation.md`
For block execution: `protocols/track-block-execution.md`
For priority: `protocols/track-priority.md`

End of tracks/README.md.
