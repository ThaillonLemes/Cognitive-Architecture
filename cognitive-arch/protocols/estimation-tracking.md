# Estimation Tracking Protocol

BRIEF: How to fill `actual_duration_hours` in block retrospectives, and what counts as implementation time. Provides the data foundation for the velocity command and phase forecast.

**Field location:** `templates/block-retrospective.md` frontmatter
**Consumer:** `commands/velocity.md`, `commands/phase-forecast.md`, `sdk/health_report.py`

---

## What to Fill In

The `actual_duration_hours` field in the block retrospective records **active implementation time** for the block — the sum of all focused work sessions on that block, not wall-clock elapsed time.

**Example:** You started a block on Monday, set it aside, and finished it Thursday. You worked on it in three focused sessions of roughly 45 minutes, 1 hour, and 30 minutes. `actual_duration_hours` is `2.25`, not `72`.

**Format:** A number (integer or decimal to one place). Examples: `1`, `2.5`, `0.5`, `12`.

Fill this field at block close, immediately after finishing the retrospective. Do not leave it at `0` — blocks with `actual_duration_hours: 0` are excluded from velocity calculations and contribute no data.

---

## What "Active Implementation Time" Means

**Included in the count:**
- Writing code or content directly for this block
- Reading files listed in the manifest's `files.read` section
- Debugging implementation failures related to this block's scope
- Running gates and interpreting results
- Writing the block retrospective itself

**NOT included:**
- Context-switching time (switching to another task and back)
- Waiting for tools to run (build, test, CI) — only the time reviewing results counts
- Rereading documentation unrelated to this block
- Planning sessions for future blocks
- Interruptions and breaks

---

## How to Estimate If You Did Not Track Time

If you worked without a timer, use these heuristics to reconstruct duration:

1. Count the number of focused sessions. A session is a period of uninterrupted work — typically 25–90 minutes.
2. Assign each session a rough duration:
   - Short session (≤ 30 min): 0.5h
   - Normal session (30–75 min): 1.0h
   - Long session (> 75 min): 1.5h
3. Sum and round to the nearest 0.5h.

**If genuinely uncertain**, use the tier default as a reasonable estimate:
- S tier: **1.0h**
- M tier: **3.5h**
- L tier: **9.0h**

These defaults are also the fallback values used by `commands/phase-forecast.md` when insufficient velocity data exists.

---

## Minimum Data Requirements for Velocity

The `commands/velocity.md` command requires at least **3 completed blocks per tier** to report a reliable estimate for that tier. Tiers with fewer data points are flagged as `[INSUFFICIENT DATA]` and the forecast falls back to tier defaults.

To reach reliable velocity data:
- S tier: at least 3 S-tier blocks with `actual_duration_hours > 0`
- M tier: at least 3 M-tier blocks with valid data
- L tier: at least 3 L-tier blocks with valid data

---

## Backfilling Historical Blocks

For blocks closed before this protocol existed (i.e., blocks that do not have `actual_duration_hours` in their retrospective), backfill using the estimation heuristics above.

Backfilled values are valid for velocity calculation. To mark them as retroactive estimates:
```yaml
actual_duration_hours: 2.5  # estimated retroactively
```

Backfilling is optional but recommended — more historical data produces more accurate velocity estimates and better phase forecasts.

---

## Why This Matters

Without duration data:
- Phase estimates are guesses based on block count alone
- It is impossible to tell whether S-tier blocks take 30 minutes or 3 hours in practice
- Patterns of underestimation cannot be detected and corrected
- The health report (block-083) cannot forecast completion dates

With even modest duration data (≥3 blocks per tier):
- Phase forecasts become grounded in actual project performance
- Systematic estimation errors become visible (e.g., "M blocks always take twice as long as expected")
- The project owner can make informed decisions about scope and scheduling

End of estimation-tracking.md.
