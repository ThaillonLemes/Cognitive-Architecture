---
id: block-081
tier: S
kind: implementation
phase: phase-11
scope: phase-bound
status: planned
dependencies: []
files:
  read:
    - templates/block-retrospective.md
  modify:
    - templates/block-retrospective.md
  create:
    - protocols/estimation-tracking.md
    - commands/velocity.md
gates:
  - name: retro-has-duration-field
    type: command
    command: grep -q "actual_duration_hours" templates/block-retrospective.md
    expect: exit 0
  - name: files-changed
    type: file-changed
    paths:
      - templates/block-retrospective.md
      - commands/velocity.md
      - protocols/estimation-tracking.md
created_at: 2026-05-23
---

# block-081 — Estimation Tracking & Velocity

## Purpose

Add time-tracking to the retrospective template and create the velocity command that converts accumulated retro data into per-tier speed estimates. Velocity is the foundation for phase forecasting (block-082) and the health report (block-083); no other Phase 11 intelligence is reliable without it.

## Background

Block retrospectives currently capture qualitative outcome data but no duration measurement. This means the project has no way to know whether S-tier blocks actually take less time than M-tier blocks in practice, which phases were under- or over-estimated, or whether implementation speed is improving over time. Adding a single numeric field to the retro template and building a command to aggregate it closes this gap with minimal overhead on the implementer.

## Implementation Steps

### Step 1 — Add `actual_duration_hours` to the retrospective template

Read `templates/block-retrospective.md`. Locate the frontmatter block. Add the field:

```yaml
actual_duration_hours: 0
```

Place it immediately after the `duration_estimate` or equivalent effort field if one exists, or after the `tier` field if no estimate field is present. The value `0` is the unfilled default; the implementer replaces it with a number (integer or decimal to one place, e.g. `1.5`) when closing the block.

### Step 2 — Create `protocols/estimation-tracking.md`

Create the protocol document with the following sections:

**What to fill in**
The `actual_duration_hours` field in the block retrospective records active implementation time for the block — the sum of all focused work sessions on that block, not wall-clock elapsed time. If you started a block on Monday and finished it Thursday but only worked on it for 90 minutes total, `actual_duration_hours` is `1.5`, not `72`.

**How to estimate if you did not track time**
Use the following heuristics to reconstruct duration:
- Count the number of focused sessions on the block. A session is a period of uninterrupted work, typically 25–90 minutes.
- Assign each session a rough duration: short session = 0.5h, normal session = 1h, long session = 1.5h.
- Sum and round to the nearest 0.5h.
- If genuinely uncertain, use the tier default: S = 1h, M = 3h, L = 8h.

**What "active implementation time" means**
Included: writing code or content, reading files directly related to the block, debugging, testing, writing the retrospective itself.
Excluded: context-switching time, waiting for tools, rereading unrelated documentation, planning sessions for future blocks.

**Minimum data requirements for velocity**
The velocity command requires at least 3 completed blocks per tier to report a reliable estimate for that tier. Until that threshold is met, the tier is flagged as "insufficient data."

**Backfilling historical blocks**
For blocks closed before this protocol existed, backfill `actual_duration_hours` using the heuristics above. Backfilled values are valid for velocity calculation; mark them with a comment `# estimated retroactively` on the same line if desired.

### Step 3 — Create `commands/velocity.md`

Create the command document with the following content:

---

## Command: velocity

**Purpose:** Calculate per-tier implementation velocity from completed block retrospectives.

**When to run:** Before opening a new block (to check current estimates), before running phase-forecast, or when the health report is generated.

**Algorithm:**

1. Open `BLOCK_LOG.md`. Collect all rows where status is `done`.
2. For each done block, derive the retro file path: `blocks/<block-id>/<block-id>-retro.md` (or the retro file pattern used in this project).
3. From each retro file, extract:
   - `tier` (S, M, or L)
   - `actual_duration_hours` (numeric; skip the block if the value is `0` or missing)
4. Group extracted durations by tier.
5. For each tier that has at least 1 data point, compute:
   - `count` — number of blocks with valid duration data
   - `mean` — arithmetic mean of durations, rounded to 1 decimal place
   - `min` — minimum duration
   - `max` — maximum duration
6. Flag tiers with fewer than 3 data points as `[INSUFFICIENT DATA — <N> block(s)]`.

**Output format:**

```
## Velocity Report — <date>

| Tier | Count | Mean (h) | Min (h) | Max (h) | Confidence |
|------|-------|----------|---------|---------|------------|
| S    | 12    | 1.2      | 0.5     | 2.5     | HIGH       |
| M    | 4     | 3.8      | 2.0     | 6.0     | MEDIUM     |
| L    | 1     | 9.0      | 9.0     | 9.0     | INSUFFICIENT DATA — 1 block |

Confidence levels: HIGH = 10+ blocks, MEDIUM = 3–9 blocks, INSUFFICIENT DATA = fewer than 3 blocks.
```

**Confidence thresholds:**
- HIGH: 10 or more blocks in tier
- MEDIUM: 3 to 9 blocks in tier
- INSUFFICIENT DATA: fewer than 3 blocks in tier

**Fallback defaults (used by phase-forecast when data is insufficient):**
- S tier: 1.0 h
- M tier: 3.5 h
- L tier: 9.0 h

These defaults are conservative estimates; replace them with real velocity data as soon as possible.

**Notes:**
- Blocks with `actual_duration_hours: 0` are excluded (unfilled field).
- Blocks that were split or abandoned should not be included in velocity calculation; mark them `skipped` in the retro file with a note.
- Velocity is descriptive, not prescriptive — it reflects past performance, not a target.

---

## Retrospective Changes

After completing this block, update `templates/block-retrospective.md` to confirm the field was added. No other templates require modification.

## Verification

Run after closing:

```
grep -q "actual_duration_hours" templates/block-retrospective.md && echo "PASS" || echo "FAIL"
```

Both `commands/velocity.md` and `protocols/estimation-tracking.md` must exist and be non-empty.
