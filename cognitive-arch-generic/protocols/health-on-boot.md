# Protocol: health-on-boot

BRIEF: Defines what the AI surfaces at session start from the health report, caching rules, and when to regenerate.

---

## Summary format (5-line output at boot)

When step 5 of the HOT read order runs, output exactly this block (filled from latest report):

```
HEALTH [YYYY-MM-DD] — audit:<score>/100 (<HEALTHY|DEGRADED|CRITICAL>)
velocity: S=<h>h M=<h>h L=<h>h (<trend: stable|improving|declining>)
phase-<N>: <blocks_done>/<blocks_total> blocks done · forecast: <date or unknown>
blocked: <count> items (<or "none">)
top recommendation: <one line from report §recommendations, or "none">
```

If no health report exists yet: output `HEALTH — no report found. Run: python sdk/health_report.py --arch-root .`

---

## Cache freshness rules

| Condition | Action |
|---|---|
| Latest `governance/health-report-*.md` is ≤ 1h old | Read and surface summary — skip regeneration |
| Latest report is > 1h old | Regenerate: `python sdk/health_report.py --arch-root .` then read new report |
| No `governance/health-report-*.md` exists | Generate immediately |
| `--dry-run` mode or no Python available | Skip regeneration; note in output |

**How to find latest report:** list `governance/health-report-*.md` sorted by filename (date in name); take the last one.

---

## Regeneration triggers

Regenerate (outside the 1h cache window) when:
1. A new phase just started (phase transition in STATE.md detected)
2. A block was just closed with a gate failure
3. User explicitly requests: "run health report" or similar

Do NOT regenerate mid-block just because the report is stale — wait for block close.

---

## What NOT to do at boot

- Do not block the session if `health_report.py` fails. Log the error and continue.
- Do not print the full report at boot — only the 5-line summary.
- Do not skip step 5 even when `STATE.md` shows `status:active` with recent activity.

---

End of health-on-boot.md.
