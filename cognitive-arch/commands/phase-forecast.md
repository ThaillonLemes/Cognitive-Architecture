# phase-forecast

BRIEF: Estimates when the current phase will complete based on measured velocity and remaining planned blocks. Produces a point estimate with confidence level.

**Depends on:** `commands/velocity.md` (velocity data required)
**Consumer:** `sdk/health_report.py`, project planning sessions
**Protocol:** `protocols/estimation-tracking.md`

---

## When to Run

- At the start of each work session to calibrate expectations
- When new blocks are added to the current phase
- When `sdk/health_report.py` is generated (called automatically)
- Whenever the project owner asks "when will Phase N be done?"

---

## Algorithm

### Step 1 — Load velocity data

Run `commands/velocity.md` or read its most recent output. Extract:
- `avg_S` — mean hours for S-tier blocks
- `avg_M` — mean hours for M-tier blocks
- `avg_L` — mean hours for L-tier blocks

If any tier has `INSUFFICIENT DATA` (fewer than 3 blocks), use the fallback defaults:

| Tier | Fallback default |
|------|-----------------|
| S | 1.0h |
| M | 3.5h |
| L | 9.0h |

Note which tiers used fallback vs. measured values — this affects confidence.

### Step 2 — Count remaining blocks

Open the current phase file (`phases/phase-N.md`). Find the Block Index table. Collect all rows where status is `planned` or `in-progress` (not `done` or `skipped`).

Count by tier:
- `count_S` = number of remaining S-tier blocks
- `count_M` = number of remaining M-tier blocks
- `count_L` = number of remaining L-tier blocks

### Step 3 — Calculate estimated remaining hours

```
estimated_remaining_hours = (count_S × avg_S) + (count_M × avg_M) + (count_L × avg_L)
```

### Step 4 — Convert to days

```
estimated_days = ceil(estimated_remaining_hours / 4)
```

Assumes **4 productive hours per working day** (accounts for context switching, reviews, and non-block work). Round up to the nearest 0.5 day.

### Step 5 — Calculate estimated completion date

```
estimated_completion = today + estimated_days (calendar days)
```

Calendar days (not working days) — this is intentionally conservative and avoids the complexity of a calendar.

---

## Confidence Levels

Confidence is determined by the weakest velocity input used:

| Condition | Confidence |
|-----------|-----------|
| All tiers used have HIGH confidence (10+ blocks each) | HIGH |
| All tiers used have at least MEDIUM confidence (3–9 blocks) | MEDIUM |
| Any tier used fallback due to INSUFFICIENT DATA | LOW |
| No velocity data at all (zero completed blocks with duration) | NONE |

When confidence is NONE, do not produce a date estimate — output the insufficient data message instead.

---

## Output Format

### Normal case

```
## Phase Forecast — Phase <N> — YYYY-MM-DD

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
- Today's date: YYYY-MM-DD
- **estimated_completion: YYYY-MM-DD**
- **Confidence: MEDIUM** (weakest input: S tier at MEDIUM)
```

### Insufficient data case

```
## Phase Forecast — Phase <N> — YYYY-MM-DD

Insufficient history — complete at least 3 blocks of each tier to generate a forecast.

Completed blocks with duration data: <N>
Minimum required per tier: 3

Fallback estimate (low confidence): estimated_completion: YYYY-MM-DD
(Uses tier defaults: S=1.0h, M=3.5h, L=9.0h)
```

---

## Notes

- The `estimated_completion` field is the key output used by the health report (`sdk/health_report.py`).
- "4 productive hours per day" is a calibrated default. If your project consistently delivers at a different rate, override the constant in the health report config.
- The forecast is a point estimate, not a guarantee. Re-run after each block closes — accumulated velocity data improves accuracy over time.
- If new blocks are added to the current phase mid-phase, re-run the forecast immediately — block count changes shift the estimate significantly.
- Do not archive old forecasts. They are ephemeral planning outputs, not project records. Only the current forecast matters.

End of phase-forecast.md.
