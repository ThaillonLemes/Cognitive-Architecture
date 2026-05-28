---
id: block-083
tier: M
kind: implementation
phase: phase-11
scope: phase-bound
status: planned
dependencies:
  - block-082
files:
  read:
    - sdk/governor.py
  create:
    - commands/health-report.md
    - sdk/health_report.py
gates:
  - name: dry-run-passes
    type: command
    command: python sdk/health_report.py --arch-root . --dry-run
    expect: exit 0
  - name: files-changed
    type: file-changed
    paths:
      - commands/health-report.md
      - sdk/health_report.py
created_at: 2026-05-23
---

# block-083 — Health Report

## Purpose

Create `commands/health-report.md` (the command document describing the report) and `sdk/health_report.py` (the Python script that generates it). The health report is the primary project dashboard — a single command produces a markdown file in `governance/` that shows whether the project is healthy across five dimensions: audit compliance, velocity, phase progress, design coverage, and Track health.

## Background

After blocks 081 and 082, the architecture has raw velocity and forecast data. The health report aggregates these plus governance audit results, design coverage, and Track status into a single document that can be reviewed at the start of any work session. Without an aggregation step, the implementer must manually read STATE.md, BLOCK_LOG.md, the velocity output, the forecast, and each track file to assess project health — a process that takes more time than the check is worth.

## Prerequisites

- block-081 complete (`commands/velocity.md` exists)
- block-082 complete (`commands/phase-forecast.md` exists)
- `sdk/governor.py` readable (for structural reference)

## Implementation Steps

### Step 1 — Read `sdk/governor.py`

Read the existing governor script to understand the SDK file conventions: how it imports modules, how it handles `--arch-root`, how it writes output files, and any shared utilities. Mirror these conventions in `health_report.py`.

### Step 2 — Design the five report sections

**Section 1 — Audit Score**

Run `audit.sh` with a dry-run or non-destructive mode if available, or parse its output. Count:
- `errors`: lines matching `ERROR` or `FAIL` patterns
- `warnings`: lines matching `WARN` or `WARNING` patterns

Compute: `audit_score = 100 - (errors × 20) - (warnings × 5)`

Clamp to range [0, 100]. Report: score, error count, warning count, and a status label:
- 90–100: HEALTHY
- 70–89: DEGRADED
- below 70: CRITICAL

**Section 2 — Velocity**

Implement the velocity algorithm from `commands/velocity.md` directly in the script. Output the velocity table (count, mean, min, max per tier) and a trend indicator:
- Compare mean duration of the last 5 completed blocks to the 5 before that (by close date in BLOCK_LOG).
- If last-5 mean < prev-5 mean by more than 10%: IMPROVING (faster)
- If last-5 mean > prev-5 mean by more than 10%: DECLINING (slower)
- Otherwise: STABLE

If fewer than 10 total completed blocks: label trend as INSUFFICIENT DATA.

**Section 3 — Phase Progress**

Read the current phase file from `phases/`. Identify the current phase as the one with `status: in-progress` (or if none, the highest-numbered planned phase). Compute:
- `done_blocks`: count of blocks with status `done`
- `total_blocks`: total blocks in phase
- `completion_pct`: done_blocks / total_blocks × 100
- `days_in_phase`: today - phase start date (from phase file `created_at` or first block open date in BLOCK_LOG)
- `forecast`: run the phase-forecast algorithm; include estimated completion date and confidence level

**Section 4 — Design Coverage**

List all files in `design/` (non-recursive, top-level `.md` files). For each design concept file, check whether a corresponding phase or block references it (search for the filename stem in `phases/` and `manifests/`). Compute:
- `total_design_concepts`: count of design files
- `covered_concepts`: count of design files referenced in at least one phase or manifest
- `coverage_pct`: covered / total × 100
- List uncovered concepts as gaps

**Section 5 — Track Health**

Read `tracks/PRIORITY.md`. For each Track listed, extract:
- Track name and current priority score
- Last improvement date (from the most recent done Track Block in BLOCK_LOG referencing this track)
- Benchmark delta trend: if `templates/track-block.md` has benchmark fields (added in block-084), show the last recorded `benchmark_after - benchmark_before`; otherwise show "benchmark data not available"
- Stagnation flag: if the track has not had a done Track Block in the last 30 calendar days, mark STAGNANT

### Step 3 — Create `sdk/health_report.py`

The script must:

1. Accept `--arch-root <path>` argument (default: `.`). All file reads are relative to arch-root.
2. Accept `--dry-run` flag: validate all input files are readable and the output directory is writable, print "Health report dry-run passed." and exit 0. Do not write any output file in dry-run mode.
3. Accept `--output-dir <path>` argument (default: `governance/`).
4. Generate the report filename as `health-report-YYYY-MM-DD.md` using today's date.
5. Write the markdown report to `<output-dir>/health-report-YYYY-MM-DD.md`.
6. Print the output path to stdout on success.
7. Exit with code 0 on success, non-zero on error.

The script must be self-contained (no imports from other SDK files beyond standard library and `pathlib`/`datetime`). It may replicate logic from velocity and forecast rather than importing it, to avoid coupling.

**Report output structure:**

```markdown
# Project Health Report — YYYY-MM-DD

Generated by: sdk/health_report.py
Architecture root: <arch-root>

---

## 1. Audit Score

Score: <N>/100 — <STATUS>
Errors: <N> | Warnings: <N>

<details or table if errors/warnings exist>

---

## 2. Velocity

| Tier | Count | Mean (h) | Min (h) | Max (h) | Confidence |
|------|-------|----------|---------|---------|------------|
...

Trend (last 5 vs previous 5): <IMPROVING / STABLE / DECLINING / INSUFFICIENT DATA>

---

## 3. Phase Progress

Current phase: phase-<N> — <phase title>
Blocks complete: <done>/<total> (<pct>%)
Days in phase: <N>
Estimated completion: <date> (Confidence: <level>)

---

## 4. Design Coverage

Design concepts: <total>
Covered by phases/manifests: <covered> (<pct>%)

Gaps:
- <uncovered concept>
...

---

## 5. Track Health

| Track | Priority | Last Improvement | Benchmark Delta | Status |
|-------|----------|-----------------|-----------------|--------|
...
```

### Step 4 — Create `commands/health-report.md`

Document the command:

---

## Command: health-report

**Purpose:** Generate a composite project health report covering audit score, velocity, phase progress, design coverage, and Track health.

**Script:** `sdk/health_report.py`

**Usage:**
```
python sdk/health_report.py --arch-root .
python sdk/health_report.py --arch-root . --dry-run
python sdk/health_report.py --arch-root . --output-dir governance/
```

**Output:** `governance/health-report-YYYY-MM-DD.md`

**When to run:** At the start of a new phase, after closing 5+ blocks, or when assessing whether the project needs course correction.

**Sections:** Audit Score, Velocity, Phase Progress, Design Coverage, Track Health.

**Dependencies:** `audit.sh` (for Section 1), `BLOCK_LOG.md`, `phases/`, `design/`, `tracks/PRIORITY.md`.

---

## Verification

```
python sdk/health_report.py --arch-root . --dry-run
```

Must exit 0. Then run without `--dry-run` and confirm a file appears in `governance/`.
