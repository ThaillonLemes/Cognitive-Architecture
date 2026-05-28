# Track Priority Protocol

BRIEF: How the Governor decides which Track to work on next. Priority is driven by objective bottleneck data, stagnation history, and user-set importance — not by arbitrary ordering. Highest total_priority score = work this Track next.

---

## Priority Formula

```
total_priority = (bottleneck_score × 3) + (stagnation_score × 1) + (user_priority × 2)
```

Maximum possible score: (10 × 3) + (10 × 1) + (10 × 2) = 60.
Default new Track score: (5 × 3) + (0 × 1) + (5 × 2) = 25.

---

## Factor Definitions

### bottleneck_score (weight: 3 — highest)

How much is this Track currently limiting the overall system performance?

| Score | Meaning |
|-------|---------|
| 9–10 | This Track is the primary bottleneck right now — everything else is waiting on it |
| 7–8 | Major bottleneck; fixing it would visibly improve overall system behavior |
| 5–6 | Moderate bottleneck; noticeable but not urgent |
| 3–4 | Minor bottleneck; affects edge cases or high-load scenarios |
| 1–2 | Not currently a bottleneck; system is healthy here |
| 0 | Unknown — no recent measurement |

**Set by:** Real performance data (profiler output, server metrics, user reports). Not by intuition.

**Updated when:** A new benchmark is taken (after any Track Block or any system load test).

---

### stagnation_score (weight: 1 — feedback signal)

How many consecutive Track Blocks have failed to improve this Track?

| Score | Meaning |
|-------|---------|
| 0 | Last attempt improved the benchmark (or no attempts yet) |
| 1–2 | 1–2 consecutive failed attempts (NO CHANGE or REGRESSED) |
| 3–5 | 3–5 consecutive failures — Track is stuck; needs a brainstorm |
| 6–8 | 6–8 failures — Track may need architectural rethink |
| 9–10 | 9+ failures — Track is stagnant; escalate to user for direction |

**Set by:** `protocols/track-block-execution.md` Section 6 (auto-increments on NO CHANGE/REGRESSED, resets to 0 on IMPROVED).

**Stagnation detection:** When stagnation_score ≥ 3, add a note to `tracks/PRIORITY.md`: "⚠️ STAGNANT — brainstorm new approach needed." The Governor should include this in the next health report.

---

### user_priority (weight: 2)

How important is this Track to the user/owner relative to other Tracks?

| Score | Meaning |
|-------|---------|
| 9–10 | Top priority — owner explicitly wants this worked on now |
| 7–8 | High importance for business/gameplay reasons |
| 5–6 | Normal priority |
| 3–4 | Lower priority — fine to work on but not urgent |
| 1–2 | Lowest priority — only work on this when nothing else needs attention |
| 0 | Paused — do not work on this Track right now |

**Set by:** Human owner. Update this score whenever priorities change.

---

## Updating PRIORITY.md

Update `tracks/PRIORITY.md` after:
- Any Track Block completes (IMPROVED → reset stagnation, update benchmark)
- Any Track Block fails (NO CHANGE/REGRESSED → increment stagnation)
- User changes user_priority for any Track
- A new performance profile reveals a different bottleneck

Recompute total_priority for all Tracks after any update.

The Track with the highest total_priority is `current_focus`.

---

## Stagnation Detection

A Track is **STAGNANT** if it has had 3 or more consecutive Track Blocks where `benchmark_after <= benchmark_before` (no improvement or regression). Consecutive means the 3 most recent done Track Blocks for that Track, ordered by close date.

**Detection procedure:**

1. For the Track being evaluated, find its last 3 done Track Blocks (by close date in BLOCK_LOG).
2. For each block, compute `delta = benchmark_after - benchmark_before`.
   - If `benchmark_before` or `benchmark_after` is empty (older block without fields), treat delta as 0.
3. If all 3 deltas are ≤ 0: mark the Track as STAGNANT in `tracks/PRIORITY.md`.

**Response to stagnation:**

When a Track is marked STAGNANT:
1. Add `stagnation_count: <N>` to the Track row in `tracks/PRIORITY.md`.
2. Add a note: `⚠️ STAGNANT — <N> consecutive non-improving blocks. Review Track scope or measurement method.`
3. Do not open another Track Block for this Track until stagnation is reviewed. Either:
   - Redefine the benchmark (if the measurement method is wrong), or
   - Close the Track (if the target quality dimension has reached its ceiling), or
   - Change the implementation approach and document why in an ADR.

**Clearing stagnation:**

A Track clears STAGNANT status when a Track Block produces `benchmark_after > benchmark_before`. Reset `stagnation_count` to 0 and remove the STAGNANT note from `tracks/PRIORITY.md`.

---

## Parallel execution

Multiple Tracks can run in parallel if:
- The Track systems do not share code or data structures
- Each Track has a separate agent or implementer

For MMORPG example: `track/networking` and `track/combat` can run in parallel — they are independent. `track/networking` and `track/replication` may conflict (both touch network layer) — run sequentially.

Governor flag: `python sdk/governor.py --track [name] --parallel N`

---

## Out of scope

- Deciding when to create a new Track (that is `protocols/track-generation.md`).
- Executing Track Blocks (that is `protocols/track-block-execution.md`).
- Selecting Phase Blocks (Tracks and Phases are independent queues).

End of track-priority.md.
