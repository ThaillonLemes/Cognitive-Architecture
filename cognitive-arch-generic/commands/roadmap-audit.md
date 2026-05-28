# Command: roadmap-audit

Mode required: checklist

BRIEF: Audit the project's macro health across 4 dimensions: Coverage, Sequencing, Completeness, and Forever Tracks. Outputs a markdown report with OK/WARN/ERROR per dimension. Run periodically or when design/ changes significantly.

## Usage

- Manual: "run roadmap audit" or "follow roadmap-audit"
- Recommended: after adding new design/ files, after completing a phase, before generating new phases
- Required: as part of `commands/roadmap-refresh.md` (Step 1)

## Pre-flight

Read `phases/ROADMAP.md`. If it does not exist:
- HALT. Output: "ROADMAP.md not found. Run `commands/roadmap-refresh.md` to generate it first."
- Do NOT proceed with audit.

---

## Dimension 1 — Coverage

**What it checks:** Are all domain systems covered by phases or Tracks?

**Steps:**
1. Run `commands/coverage-check.md` (Steps 1–7).
2. Count UNCOVERED, DRIFT, STALE items.

**Scoring:**
- UNCOVERED = 0 → OK
- UNCOVERED ≥ 1 → ERROR: "N system(s) in design/ have no phase or track"
- DRIFT ≥ 1 → WARN: "N phase(s) reference no documented design concept"
- STALE ≥ 1 → WARN: "N phase(s) may be out of date with design/ changes"

**Output section:**
```
## Dimension 1 — Coverage
Status: OK | WARN | ERROR
UNCOVERED: N  DRIFT: N  STALE: N
[list of gaps if any]
```

---

## Dimension 2 — Sequencing

**What it checks:** Does the phase order form a valid execution plan?

**Steps:**
1. Read all `phases/phase-N.md` files.
2. For each phase, extract its `dependencies:` list (which prior phases must be complete).
3. Check for cycles: if Phase A depends on Phase B which depends on Phase A → ERROR.
4. Check forward references: if Phase 3 depends on Phase 5 (not yet done) → WARN.
5. Check dependency completeness: if Phase N says it requires "auth system" but the phase that builds auth (Phase 2) has no exit criterion about auth → WARN.

**Scoring:**
- No cycles, no forward references → OK
- Forward references only → WARN
- Cycle detected → ERROR

**Output section:**
```
## Dimension 2 — Sequencing
Status: OK | WARN | ERROR
[issues list if any]
```

---

## Dimension 3 — Completeness

**What it checks:** Does the roadmap cover all user journeys declared in PROJECT.md?

**Steps:**
1. Read PROJECT.md. Extract the target users and the project description.
2. Identify 3–5 core user journeys implicit in the description (what must a user be able to do?).
3. For each user journey: find the phase(s) that deliver it.
4. If a user journey has no corresponding phase → WARN.

**Note:** This check requires AI judgment. The AI reads the project description and reasons about what "done" looks like for each user type.

**Scoring:**
- All journeys covered → OK
- 1–2 journeys uncovered → WARN
- 3+ journeys uncovered → ERROR

**Output section:**
```
## Dimension 3 — Completeness
Status: OK | WARN | ERROR
User journeys: [list of journeys and their covering phase]
Uncovered journeys: [list if any]
```

---

## Dimension 4 — Forever Tracks

**What it checks:** Are all perpetual-improvement systems properly tracked?

**Steps:**
1. Read `tracks/PRIORITY.md`. List all Tracks.
2. For each system in design/ classified as TRACK or BOTH: verify a `tracks/*.md` file exists.
3. For each Track: check `last_improved_at` — if more than 90 days ago → WARN (stagnant).
4. Check that `tracks/PRIORITY.md` has been updated in the last 30 days (if any Track Blocks have been done) → WARN if stale.

**Scoring:**
- All TRACK systems have Track files, no stagnant Tracks → OK
- 1+ stagnant Tracks (>90 days) → WARN
- TRACK system with no Track file → ERROR

**Output section:**
```
## Dimension 4 — Forever Tracks
Status: OK | WARN | ERROR
Active tracks: N  Stagnant: N  Missing: N
[issues list if any]
```

---

## Final Summary and Report

After all 4 dimensions:

```
## Roadmap Audit Summary
Date: YYYY-MM-DD

| Dimension | Status |
|-----------|--------|
| 1 — Coverage | OK/WARN/ERROR |
| 2 — Sequencing | OK/WARN/ERROR |
| 3 — Completeness | OK/WARN/ERROR |
| 4 — Forever Tracks | OK/WARN/ERROR |

Overall: PASS | PASS WITH WARNINGS | FAIL

Errors: N  Warnings: N

Recommended action:
[If FAIL: list specific errors to fix before generating new phases]
[If PASS WITH WARNINGS: list warnings for review]
[If PASS: "Roadmap is healthy. Proceed with next phase."]
```

Save report to `governance/roadmap-audit-YYYY-MM-DD.md`.

## Exit behavior

- 0 errors → PASS (exit 0 conceptually)
- ≥ 1 error → FAIL — do NOT generate new phases until errors are resolved
- Warnings alone → PASS WITH WARNINGS — may proceed but review warnings

## Cost

~5K–10K tokens depending on project size and number of phases.

End of roadmap-audit command.
