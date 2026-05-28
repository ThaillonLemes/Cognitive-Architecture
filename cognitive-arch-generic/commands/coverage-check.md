# Command: coverage-check

Mode required: checklist

BRIEF: Build the Domain Coverage Matrix for this project. Identifies UNCOVERED systems, DRIFT phases, and STALE phases. Output is a markdown coverage report. See `protocols/domain-coverage-matrix.md` for definitions.

## Usage

- Manual: "run coverage check" or "follow coverage-check"
- Auto-triggered by `commands/roadmap-audit.md` (Step 1)
- Recommended: run whenever new design/ files are added or phases are generated

## Steps

### Step 1 — Enumerate domain systems

Read all files in `design/`:
- Skip: `_placeholder.md`, `README.md`, `governor-v2.md` (architecture files, not domain)
- For each remaining file: extract system name and one-line description
- Output: flat list `[system_name, file_path]`

If fewer than 3 systems found: emit WARN "fewer than 3 systems documented in design/ — coverage matrix may be incomplete."

### Step 2 — Enumerate phases

Read all `phases/phase-N.md` files (exclude retros, ROADMAP.md).
For each phase: extract name, BRIEF, Goals section, Block Index descriptions.
Collect: all system names and concepts mentioned in those sections.

### Step 3 — Enumerate Tracks

Read all `tracks/*.md` files (exclude `README.md`, `PRIORITY.md`, `_placeholder.md`).
For each Track: extract the system name from the track file's `system:` field or filename.

### Step 4 — Detect UNCOVERED systems

For each system from Step 1:
- Search phase text (Step 2) for the system name (case-insensitive exact word match)
- Search track files (Step 3) for the system name
- If found in neither: mark UNCOVERED

### Step 5 — Detect DRIFT phases

For each phase from Step 2:
- Take the system names/concepts extracted from the phase
- Search design/ files for those names
- If no design/ file matches any concept: mark phase as DRIFT

### Step 6 — Detect STALE phases

For each (phase, system) pair where coverage exists:
- Identify the design/ file for that system
- Check if the design/ file's content has changed significantly since the phase was last updated
  - Heuristic: if design/ file has sections that introduce new subsystems not mentioned in the phase, flag as STALE
- Mark STALE if applicable

### Step 7 — Build matrix table

Assemble the coverage matrix in the format from `protocols/domain-coverage-matrix.md`.

### Step 8 — Output report

Print the matrix. If running inside a roadmap-audit, return structured data. If running standalone, save output to `governance/coverage-check-YYYY-MM-DD.md`.

Summary line format:
```
Coverage: X/Y systems covered (Z%)
UNCOVERED: N  DRIFT: N  STALE: N
```

## Exit codes (when run as script)

- Exit 0: no UNCOVERED gaps (DRIFT and STALE are warnings, not errors)
- Exit 1: at least one UNCOVERED system

## Cost

~3K–6K tokens depending on project size.

End of coverage-check command.
