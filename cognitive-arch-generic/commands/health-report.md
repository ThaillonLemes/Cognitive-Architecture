# health-report

BRIEF: Generates a composite project health report covering audit score, velocity, phase progress, design coverage, and Track health. Writes to `governance/health-report-YYYY-MM-DD.md`.

**Script:** `sdk/health_report.py`
**Dependencies:** `BLOCK_LOG.md`, `PROTOCOLS.md`, `phases/`, `design/`, `tracks/PRIORITY.md`
**Related commands:** `commands/velocity.md`, `commands/phase-forecast.md`

---

## Usage

```bash
# Generate full health report (output: governance/health-report-YYYY-MM-DD.md)
python sdk/health_report.py --arch-root .

# Dry-run — validates inputs are readable, no file written
python sdk/health_report.py --arch-root . --dry-run

# Write to a different output directory
python sdk/health_report.py --arch-root . --output-dir governance/
```

---

## When to Run

- At the start of a new phase (to baseline project health before new work begins)
- After closing 5 or more blocks (to recalibrate velocity and forecast)
- Before presenting project status to any stakeholder
- When you suspect the project is drifting from plan
- At the start of any major debugging or replanning session

---

## Report Sections

| Section | What It Shows | Key Metric |
|---------|--------------|------------|
| 1. Audit Score | Structural health of the arch directory (files, pointers, axioms) | Score/100 (HEALTHY / DEGRADED / CRITICAL) |
| 2. Velocity | Per-tier implementation speed from completed block retrospectives | Mean hours per tier (S/M/L) |
| 3. Phase Progress | Current phase completion and estimated completion date | Blocks done/total + forecast date |
| 4. Design Coverage | How many design concepts have corresponding phases or manifests | Coverage % + gap list |
| 5. Track Health | Active Tracks, priority scores, stagnation warnings | OK / STUCK / STAGNANT per Track |

---

## Output Location

`governance/health-report-YYYY-MM-DD.md`

Multiple health reports accumulate in `governance/`. They are not automatically pruned. Old reports remain for historical comparison.

The most recent report is always the one with the latest date in the filename.

---

## Interpreting Results

**Audit Score CRITICAL (<70):** Stop new block work. Fix the structural errors before continuing.

**Velocity DECLINING:** Blocks are taking longer than historical average. Investigate: are blocks scope-creeping? Is the codebase getting harder to work with? Are estimates realistic?

**Phase Progress forecast date far from expected:** Either the phase has more blocks than planned, or velocity is lower than expected. Consider splitting the phase or descoping lower-priority blocks.

**Design Coverage gaps:** Systems with no corresponding phase coverage are at risk of being forgotten or implemented inconsistently. Add them to the roadmap via `commands/roadmap-refresh.md`.

**Track STAGNANT:** A Track has had no improvement in too long (stagnation_count ≥ 9). Escalate to the project owner for direction — either rethink the approach, deprioritize the Track, or pause it.

---

## Integration with Governor

In SDK mode, the Governor can run the health report automatically at phase transitions:
```bash
python sdk/health_report.py --arch-root . --output-dir governance/
```

In manual mode, run the command manually at the start of each phase.

End of health-report.md.
