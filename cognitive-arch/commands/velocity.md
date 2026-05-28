# velocity

BRIEF: Calculates per-tier implementation velocity from completed block retrospectives. Required input for `commands/phase-forecast.md` and `sdk/health_report.py`.

**Data source:** `actual_duration_hours` field in block retrospective files (`blocks/block-NNN-*.md`)
**Protocol:** `protocols/estimation-tracking.md`
**Consumer:** `commands/phase-forecast.md`, `sdk/health_report.py`

---

## When to Run

- Before planning a new phase (to inform block count decisions)
- Before running `commands/phase-forecast.md`
- When `sdk/health_report.py` is generated (called automatically)
- Any time you want to know how fast blocks are actually completing

---

## Algorithm

1. Open `blocks/BLOCK_LOG.md`. Collect all rows with status `done`.
2. For each done block, locate the retrospective file: `blocks/block-<id>-*.md` (search by prefix pattern matching the block ID).
3. From each retrospective file's frontmatter, extract:
   - `tier` — S, M, or L
   - `actual_duration_hours` — the active implementation time in hours
4. **Exclude** blocks where `actual_duration_hours` is `0`, missing, or marked `skipped`.
5. Group valid data points by tier.
6. For each tier, compute:
   - `count` — number of blocks with valid duration data
   - `mean` — arithmetic mean, rounded to 1 decimal place
   - `min` — minimum recorded duration
   - `max` — maximum recorded duration
   - `confidence` — based on count thresholds (see below)

---

## Confidence Thresholds

| Confidence | Count |
|-----------|-------|
| HIGH | 10 or more blocks in tier |
| MEDIUM | 3 to 9 blocks in tier |
| INSUFFICIENT DATA | fewer than 3 blocks in tier |

---

## Fallback Defaults

When a tier has `INSUFFICIENT DATA`, phase-forecast uses these conservative defaults:

| Tier | Default (h) |
|------|------------|
| S | 1.0 |
| M | 3.5 |
| L | 9.0 |

Replace these defaults with real velocity data as soon as ≥3 blocks per tier are available.

---

## Output Format

```
## Velocity Report — YYYY-MM-DD

| Tier | Count | Mean (h) | Min (h) | Max (h) | Confidence |
|------|-------|----------|---------|---------|------------|
| S    | 12    | 1.2      | 0.5     | 2.5     | HIGH       |
| M    | 4     | 3.8      | 2.0     | 6.0     | MEDIUM     |
| L    | 1     | 9.0      | 9.0     | 9.0     | INSUFFICIENT DATA — 1 block |

Tier defaults used for INSUFFICIENT DATA tiers: S=1.0h, M=3.5h, L=9.0h.
```

---

## Interpretation Guide

| Pattern | What It Means |
|---------|--------------|
| Mean much higher than tier default | The default is too optimistic for this project; adjust phase planning |
| Mean much lower than tier default | Blocks are completing faster than expected; consider more ambitious phase scope |
| Max >> Mean | Outlier blocks are skewing estimates; investigate the high-duration blocks |
| INSUFFICIENT DATA after 10+ blocks | Many blocks lack `actual_duration_hours`; backfill per `protocols/estimation-tracking.md` |

---

## Notes

- Blocks with `actual_duration_hours: 0` are excluded — this is the unfilled default, not a real measurement.
- Blocks that were split, abandoned, or have `status: reverted` should be excluded. Mark them `skipped` with a note in the retro file.
- Velocity is descriptive, not prescriptive. It reflects past performance. Actual future block time will vary; the report is a calibration aid, not a guarantee.
- The velocity report is regenerated fresh each time it is run — it does not cache. Old velocity reports should not be committed to the repository (they go stale as more blocks complete).

End of velocity.md.
