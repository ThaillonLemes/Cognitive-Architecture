---
id: block-074
tier: S
kind: protocol
phase: phase-9
scope: phase-bound
status: planned
dependencies:
  - block-073
files:
  read:
    - protocols/track-generation.md
  modify: []
  create:
    - protocols/track-priority.md
    - tracks/PRIORITY.md
    - tracks/_placeholder.md
gates:
  - name: track-priority-protocol-exists
    type: file-changed
    paths: [protocols/track-priority.md]
  - name: tracks-priority-file-exists
    type: file-changed
    paths: [tracks/PRIORITY.md]
created_at: 2026-05-23
---

# block-074 — Track Priority Protocol

## Purpose

With multiple Tracks in a project, the executor must decide which Track to work on next. Without a principled priority system, Track work will gravitate toward the Track that is easiest or most recently thought about — not the Track where improvement delivers the most value.

This block introduces a data-driven priority system grounded in three factors:

1. **bottleneck_score** — the extent to which this Track is currently the binding constraint on user experience. Set by the human based on real performance data. This is the highest-weight factor because it is empirically grounded.
2. **stagnation_score** — how many consecutive Track Blocks have failed to improve this Track. A Track that is not improving despite effort deserves renewed attention.
3. **user_priority** — a direct override the human can use to prioritise a Track regardless of data, when business reasons require it.

The priority formula is: `total_priority = (bottleneck_score × 3) + (stagnation_score × 1) + (user_priority × 2)`

The Governor (block-075) reads `tracks/PRIORITY.md` at dispatch time to determine which Track to work on.

The deliverables are:

1. `protocols/track-priority.md` — the full priority protocol: score definitions, formula, update procedure, and the rule that the Governor always follows the priority table.
2. `tracks/PRIORITY.md` — the actual runtime priority file. Template only (no real data until project Tracks are created).
3. `tracks/_placeholder.md` — ensures the tracks/ directory is tracked by git even before any real Track files exist.

## Dependencies

- **block-073** must be complete. The priority protocol references Track Block concepts (specifically: "consecutive failed blocks" is used to compute stagnation_score).
- Read `protocols/track-generation.md` — to ensure the priority protocol is consistent with the criteria for creating Tracks.

## Files

### Read
- `protocols/track-generation.md` — to understand which systems have Tracks and how Track IDs are assigned.

### Modify
None.

### Create

**`protocols/track-priority.md`**

Must contain:

**Section 1 — Purpose**

The priority protocol determines the order in which Tracks are worked. Priority is computed from three factors and stored in `tracks/PRIORITY.md`. The Governor reads this file at dispatch time. The file must be updated by the human whenever underlying data changes (new profiling results, user feedback, Track Block outcomes).

Priority is a tool for the human to communicate intent to the Governor. The human sets scores; the formula computes the result; the Governor follows the result. The human may override the Governor's choice by setting user_priority to a high value for a specific Track.

**Section 2 — Score Definitions**

_bottleneck_score_ (integer, 0–10):
Measures whether this Track is the current binding constraint on user experience. 0 = this system is not a bottleneck at all. 10 = this system is the single most impactful constraint on user experience right now.

How to set bottleneck_score:
- Run performance profiling or user experience measurement for the system.
- Ask: "If I improve this system by 20%, how much does overall user experience improve?" If the answer is "significantly," score 7–10. If "somewhat," score 4–6. If "barely," score 1–3. If "not at all," score 0.
- Only one Track should have a score of 10 at any time (by definition, only one system can be the single top bottleneck).
- Update this score whenever new profiling data is available.

_stagnation_score_ (integer, 0–5):
Measures how long this Track has been stuck. 0 = the most recent Track Block confirmed an improvement. 1 = one consecutive Track Block was refuted. 2 = two consecutive refuted blocks. Etc. Cap at 5.

How to compute stagnation_score automatically:
- Read the Track file's Track Blocks table.
- Count the number of most recent consecutive blocks with result = "refuted" or result = "inconclusive."
- That count is the stagnation_score (capped at 5).

Rationale: a Track that is stagnating needs either a new approach (human insight) or elevated priority so the executor devotes more attention to generating better hypotheses.

_user_priority_ (integer, 0–10):
A direct override from the human. 0 = no special priority. 10 = work this Track above all others regardless of data.

Use user_priority when: a stakeholder decision, an upcoming release, or a user complaint makes a specific Track urgent in a way that is not captured by bottleneck_score or stagnation_score.

**Section 3 — Priority Formula**

```
total_priority = (bottleneck_score × 3) + (stagnation_score × 1) + (user_priority × 2)
```

Maximum possible score: (10 × 3) + (5 × 1) + (10 × 2) = 30 + 5 + 20 = 55.

**Section 4 — Priority Table**

The priority table is stored in `tracks/PRIORITY.md`. It has one row per Track. After updating any score, recompute total_priority for that row. After recomputing, update current_focus to the Track with the highest total_priority.

If two Tracks have the same total_priority, prefer the one with the higher bottleneck_score. If still tied, the human must choose and set user_priority to break the tie.

**Section 5 — Update Procedure**

When to update the priority table:
- After completing a Track Block (stagnation_score may change).
- After new performance profiling is available (bottleneck_score may change).
- After a stakeholder decision changes priorities (user_priority may change).
- At the start of each development sprint or planning session.

How to update:
1. Open `tracks/PRIORITY.md`.
2. For each Track, recompute stagnation_score from the Track's block history (automated — no manual judgment required).
3. Update bottleneck_score and user_priority based on current data (requires human input).
4. Recompute total_priority for each Track.
5. Update current_focus to the Track with the highest total_priority.
6. Update last_updated.

**Section 6 — Governor Behaviour**

When the Governor is invoked with `--track [NAME]`, it:
1. Reads `tracks/PRIORITY.md`.
2. Finds the Track with the given name (or the current_focus Track if no name is given).
3. Reads the Track file to find open (planned or wip) Track Blocks.
4. Dispatches the open Track Blocks using the existing dispatch_batch mechanism.

The Governor does NOT override the priority table. If the human asks to work a Track that is not current_focus, the Governor complies but does not update the priority table. Priority updates are the human's responsibility.

---

**`tracks/PRIORITY.md`**

Must contain:

```
---
type: track-priority
last_updated: YYYY-MM-DD
current_focus: [Track ID or "none — no Tracks created yet"]
---

# Track Priority Table

> This file is read by `sdk/governor.py --list-tracks` and `sdk/governor.py --track NAME`.
> Update scores whenever performance data changes, Track Blocks complete, or priorities shift.
> Recompute total_priority after any update.
> See `protocols/track-priority.md` for score definitions and the update procedure.

## Priority Formula

```
total_priority = (bottleneck_score × 3) + (stagnation_score × 1) + (user_priority × 2)
```

## Priority Table

| Track ID | System Name | Track File | bottleneck_score | stagnation_score | user_priority | total_priority | Status |
|----------|-------------|------------|-----------------|-----------------|---------------|----------------|--------|
| — | (no Tracks yet) | — | — | — | — | — | — |

> Add a row here for each Track created with `protocols/track-generation.md`.

## Current Focus

**current_focus**: [Track ID with highest total_priority, or "none"]

Last updated: YYYY-MM-DD

## Score Update Log

| Date | Track ID | Score Changed | Old Value | New Value | Reason |
|------|----------|---------------|-----------|-----------|--------|
| YYYY-MM-DD | — | — | — | — | Initial file creation |
```

---

**`tracks/_placeholder.md`**

Must contain:

```
---
type: placeholder
purpose: git-directory-tracking
---

# tracks/ placeholder

This file ensures the tracks/ directory is tracked by git before any Track files are created.

Delete this file once the first real Track file is added to this directory.
```

## Validation

- `protocols/track-priority.md` exists and defines all three score factors (bottleneck_score, stagnation_score, user_priority) with explicit ranges and "how to set" guidance.
- `protocols/track-priority.md` contains the exact formula: `total_priority = (bottleneck_score × 3) + (stagnation_score × 1) + (user_priority × 2)`.
- `protocols/track-priority.md` contains a Governor Behaviour section.
- `tracks/PRIORITY.md` exists and contains the priority table template and the formula.
- `tracks/PRIORITY.md` contains a current_focus field.
- `tracks/_placeholder.md` exists.

## Gates

| Gate | Type | Path(s) | Condition |
|------|------|---------|-----------|
| track-priority-protocol-exists | file-changed | protocols/track-priority.md | File must exist and define the formula |
| tracks-priority-file-exists | file-changed | tracks/PRIORITY.md | File must exist and contain priority table |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Human never updates bottleneck_score — all scores stay at 0 and current_focus is arbitrary | Medium | Medium | Governor outputs a warning when all bottleneck_scores are 0: "No bottleneck data. Update tracks/PRIORITY.md." |
| stagnation_score computation is manual — human forgets to update it | Medium | Low | Section 5 specifies that stagnation_score can be computed automatically from block history; block-075 automates this in the Governor |
| Two Tracks tied at the same total_priority — Governor cannot decide | Low | Low | Tie-breaking rule in Section 4: prefer higher bottleneck_score, then require human to set user_priority |

## Out of Scope

- Automated bottleneck detection. The protocol defines how to interpret profiling data; it does not run the profiler.
- Machine learning-based priority suggestions. Priority is deterministic and transparent; no ML involved.
- Priority decay over time (scores automatically decreasing if not updated). Scores are manually maintained.
