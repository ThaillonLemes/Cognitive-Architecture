---
id: block-082
tier: S
kind: protocol
phase: phase-11
scope: phase-bound
status: planned
dependencies:
  - block-081
files:
  read:
    - commands/velocity.md
  create:
    - commands/phase-forecast.md
gates:
  - name: forecast-file-exists
    type: file-changed
    paths:
      - commands/phase-forecast.md
  - name: forecast-has-completion-field
    type: command
    command: grep -q "estimated_completion" commands/phase-forecast.md
    expect: exit 0
created_at: 2026-05-23
---

# block-082 — Phase Forecast Command

## Purpose

Create `commands/phase-forecast.md`, a command document that describes how to estimate when the current phase will complete based on measured velocity and the remaining planned blocks. The forecast gives the implementer a data-grounded answer to "when will this phase be done?" rather than an intuitive guess.

## Background

After block-081 provides velocity data (mean duration per tier), phase forecast is the direct application of that data. The forecast algorithm is intentionally simple: count the remaining blocks, weight them by tier, divide by a fixed productive-hours-per-day constant, and add to today's date. Confidence is derived from the velocity data quality, not a separate calculation. This simplicity is a feature — a forecast that requires complex input will not be run.

## Prerequisites

block-081 must be complete and `commands/velocity.md` must exist before this block is opened.

## Implementation Steps

### Step 1 — Design the algorithm

The forecast algorithm has six steps:

1. **Load velocity data.** Run or read the velocity command output. Extract `avg_S`, `avg_M`, `avg_L` (the mean durations per tier). If any tier has INSUFFICIENT DATA, use the fallback defaults defined in `commands/velocity.md` (S=1.0h, M=3.5h, L=9.0h) and note this in the output.

2. **Read the current phase block index.** Open the current phase file (`phases/phase-N.md`). Find the Block Index table. Collect all rows where status is `planned` or `in-progress` (i.e., not `done` or `skipped`). Record the tier of each remaining block.

3. **Count remaining blocks by tier.**
   ```
   count_S = number of remaining S-tier blocks
   count_M = number of remaining M-tier blocks
   count_L = number of remaining L-tier blocks
   ```

4. **Calculate estimated remaining hours.**
   ```
   estimated_remaining_hours = (count_S × avg_S) + (count_M × avg_M) + (count_L × avg_L)
   ```

5. **Convert hours to days.** Assume 4 productive hours per working day (accounts for context switching, review, and non-block work):
   ```
   estimated_days = estimated_remaining_hours / 4
   ```
   Round up to the nearest 0.5 day.

6. **Calculate estimated completion date.**
   ```
   estimated_completion = today + estimated_days (calendar days, not working days)
   ```
   Note: using calendar days is conservative and avoids requiring a calendar to skip weekends.

### Step 2 — Define confidence levels

Confidence is determined by the weakest velocity input used:

| Condition | Confidence |
|-----------|------------|
| All tiers used have HIGH velocity confidence (10+ blocks) | HIGH |
| All tiers used have at least MEDIUM confidence (3–9 blocks) | MEDIUM |
| Any tier used has INSUFFICIENT DATA (< 3 blocks) and fallback was used | LOW |
| No velocity data exists at all (zero completed blocks) | NONE |

When confidence is NONE, output: "Insufficient history — complete at least 3 blocks of each tier to generate a forecast."

### Step 3 — Create `commands/phase-forecast.md`

Create the file with the following content:

---

## Command: phase-forecast

**Purpose:** Estimate when the current phase will complete, based on measured velocity and remaining planned blocks.

**Depends on:** velocity command output (`commands/velocity.md`)

**When to run:** At the start of each work session to calibrate expectations, when adding new blocks to the current phase, or when the health report is generated.

**Algorithm:**

See block-082 manifest for the full algorithm specification. Summary:

1. Load per-tier mean durations from velocity data (or use fallback defaults if insufficient).
2. Count remaining planned/in-progress blocks in the current phase by tier.
3. `estimated_remaining_hours = (count_S × avg_S) + (count_M × avg_M) + (count_L × avg_L)`
4. `estimated_days = ceil(estimated_remaining_hours / 4)` (4 productive hours/day assumed)
5. `estimated_completion = today + estimated_days`

**Output format:**

```
## Phase Forecast — Phase <N> — <date>

### Velocity inputs
| Tier | Mean (h) | Confidence | Source |
|------|----------|------------|--------|
| S    | 1.2      | MEDIUM     | measured (6 blocks) |
| M    | 3.8      | HIGH       | measured (11 blocks) |
| L    | 9.0      | LOW        | fallback default (0 blocks) |

### Remaining blocks
| Tier | Count | Est. Hours |
|------|-------|------------|
| S    | 3     | 3.6        |
| M    | 1     | 3.8        |
| L    | 0     | 0.0        |
| **Total** | **4** | **7.4** |

### Forecast
- Estimated remaining hours: 7.4
- Productive hours per day: 4
- Estimated days remaining: 2.0
- Today's date: 2026-05-23
- **Estimated completion: 2026-05-25**
- **Confidence: MEDIUM** (weakest input tier: S at MEDIUM)
```

**Insufficient data case:**

```
## Phase Forecast — Phase <N> — <date>

Insufficient history — complete at least 3 blocks of each tier to generate a forecast.

Completed blocks with duration data: <N>
Minimum required per tier: 3
```

**Notes:**
- "4 productive hours per day" is a conservative default. If your actual pace differs significantly, note the actual value when presenting the forecast.
- Estimated completion is in calendar days from today, not working days. This is intentionally conservative.
- The forecast is a point estimate, not a guarantee. Re-run it after each block closes to track drift.
- If the current phase has blocks added mid-phase, re-run the forecast immediately — the block count change can shift the estimate significantly.
- `estimated_completion` is the key output field used by the health report (block-083).

---

## Verification

After creating `commands/phase-forecast.md`:

```
grep -q "estimated_completion" commands/phase-forecast.md && echo "PASS" || echo "FAIL"
```

The file must exist and contain the string `estimated_completion`.
