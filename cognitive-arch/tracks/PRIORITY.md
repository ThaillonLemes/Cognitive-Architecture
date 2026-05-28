# tracks/PRIORITY.md — Track Priority Table

This file is the Governor's runtime priority source. Updated after every Track Block (close or reopen) and whenever the human changes user_priority.

**Priority formula:** `total_priority = (bottleneck_score × 3) + (stagnation_score × 1) + (user_priority × 2)`

**Highest total_priority = current_focus.**

Protocol: `protocols/track-priority.md`

---

## Active Tracks

| track_id | bottleneck_score | stagnation_count | user_priority | total_priority | current_best | last_improved_at | stagnation_alert | notes |
|----------|-----------------|-----------------|--------------|----------------|-------------|-----------------|-----------------|-------|
| _(no tracks yet)_ | — | — | — | — | — | — | — | Create tracks via `protocols/track-generation.md` |

---

## current_focus

```
current_focus: none
reason: no tracks created yet
```

---

## Stagnation Alerts

Tracks where `stagnation_count ≥ 3` appear here. The Governor includes these in the next health report.

| track_id | stagnation_count | alert |
|----------|-----------------|-------|
| _(none)_ | — | — |

---

## Update Log

| date | event | track_id | field_changed | old_value | new_value |
|------|-------|----------|--------------|-----------|-----------|
| _(no entries yet)_ | — | — | — | — | — |

---

## Score Reference

| Factor | Weight | 0 | 3–4 | 5–6 | 7–8 | 9–10 |
|--------|--------|---|-----|-----|-----|------|
| bottleneck_score | ×3 | Unknown | Minor | Moderate | Major | Primary bottleneck |
| stagnation_count | ×1 | Improving | Stuck | Very stuck | Rethink needed | Escalate |
| user_priority | ×2 | Paused | Low | Normal | High | Top priority |

End of PRIORITY.md.
