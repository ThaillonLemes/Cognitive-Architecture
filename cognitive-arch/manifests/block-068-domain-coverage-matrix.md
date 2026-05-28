---
id: block-068
tier: S
kind: protocol
phase: phase-9
scope: phase-bound
status: planned
dependencies:
  - block-067
files:
  read:
    - templates/roadmap.md
  modify: []
  create:
    - protocols/domain-coverage-matrix.md
    - commands/coverage-check.md
gates:
  - name: coverage-matrix-protocol-exists
    type: file-changed
    paths: [protocols/domain-coverage-matrix.md]
  - name: coverage-check-command-exists
    type: file-changed
    paths: [commands/coverage-check.md]
created_at: 2026-05-23
---

# block-068 — Domain Coverage Matrix

## Purpose

A ROADMAP.md is only useful if its coverage data is accurate and up to date. As a project evolves, design/ files are added, phases are created, and some phases quietly fall out of alignment with the design concepts they were supposed to implement. Without a systematic audit mechanism, these gaps accumulate invisibly.

This block defines the Coverage Matrix and the command that builds it.

The **Coverage Matrix** is a formal data structure — a table cross-referencing design/ concepts against phases/ entries — with three precisely defined gap types:

- **UNCOVERED**: a concept documented in design/ has no phase assigned to implement it. The system exists in the design space but not in the execution plan.
- **DRIFT**: a phase exists in phases/ but the design/ concept it was originally based on no longer exists or has been renamed. The execution plan references a concept the design space has abandoned.
- **STALE**: a phase exists and its corresponding design/ concept exists, but the design/ file has been updated more recently than the phase. The execution plan may be based on outdated requirements.

The deliverables are:

1. `protocols/domain-coverage-matrix.md` — the formal definition of the Coverage Matrix: what it is, how the three gap types are determined, and the rules for resolving each.
2. `commands/coverage-check.md` — a command an AI executor can run to build the Coverage Matrix from scratch for any project.

## Dependencies

- **block-067** must be complete. The Coverage Matrix protocol must reference the ROADMAP.md structure defined in `templates/roadmap.md`, specifically the Phase Coverage Matrix section and the Domain Coverage Summary section.

## Files

### Read
- `templates/roadmap.md` — to understand the Phase Coverage Matrix and Domain Coverage Summary structure that the coverage check command populates.

### Modify
None.

### Create

**`protocols/domain-coverage-matrix.md`**

Must contain the following sections:

**Section 1 — Definition**

The Coverage Matrix is a table with one row per design/ system and one column per coverage dimension. It is always derived from the live state of design/ and phases/ — it is never manually edited.

Structure:
```
| System ID | System Name | design/ File | Phase Assigned | Phase Status | Gap Type |
```

Gap Type values: OK, UNCOVERED, DRIFT, STALE, UNKNOWN.

**Section 2 — Gap Type Definitions**

_UNCOVERED_: The system appears in design/ but no phase in phases/ lists this system in its Purpose, Goals, or Dependencies sections. Resolution: generate a new phase for this system, or explicitly mark the system as out-of-scope in ROADMAP.md.

_DRIFT_: A phase in phases/ references a design concept (by name or system ID) that does not exist in any current design/ file. This indicates scope drift — the phase was written for a concept that no longer exists. Resolution: either re-anchor the phase to an existing concept, or retire the phase.

_STALE_: A phase in phases/ is assigned to a system, but the system's design/ file has a `last_updated` value more recent than the phase's `last_updated` value. The design has evolved past the phase definition. Resolution: re-read the design/ file and update the phase to reflect current requirements.

_UNKNOWN_: The system or phase is missing `last_updated` frontmatter. Cannot determine staleness. Resolution: add `last_updated` to the affected file.

**Section 3 — Detection Rules**

UNCOVERED detection algorithm:
1. Collect all system IDs from design/ files (from frontmatter field `id` or inferred from filename).
2. For each system ID, search all phases/ files for any reference to that ID or the system's name.
3. If no phase references the system, mark UNCOVERED.

DRIFT detection algorithm:
1. For each phase in phases/, extract all design/ concept references from the Purpose and Dependencies sections.
2. For each referenced concept, check whether a corresponding design/ file exists.
3. If no design/ file matches, mark that phase row as DRIFT.

STALE detection algorithm:
1. For each phase–system pair where gap type is OK, read the `last_updated` field from the design/ file and from the phase file.
2. If design/ last_updated > phase last_updated, mark STALE.
3. If either file lacks `last_updated`, mark UNKNOWN.

**Section 4 — Resolution Guidance**

Each gap type has a prescribed resolution path:
- UNCOVERED → run `commands/roadmap-refresh.md` to propose a new phase.
- DRIFT → run `commands/roadmap-refresh.md` to propose retiring or re-anchoring the phase.
- STALE → re-read the design/ file; if requirements have materially changed, update the phase; if the design change was cosmetic, update the phase's `last_updated` and add a note.
- UNKNOWN → add `last_updated` frontmatter to the affected file.

**`commands/coverage-check.md`**

Must contain:

**Command name**: `coverage-check`

**Trigger phrase**: "Run coverage check" or "Build the coverage matrix."

**Step-by-step procedure**:

Step 1 — Collect design/ systems.
Read every file in design/. For each file extract: system name (from frontmatter field `system` or from the H1 heading), system ID (from frontmatter field `id` or derive as SYS-NNN in alphabetical order), design/ file path, and `last_updated` date.

Step 2 — Collect phases.
Read every file in phases/. For each file extract: phase id, phase title, phase `last_updated` date, and all design/ concept references (scan Purpose, Goals, and Dependencies sections for system names and IDs).

Step 3 — Build the raw matrix.
For each design/ system, find the phase(s) that reference it. If multiple phases reference the same system, list the most recent one as the assigned phase and note duplicates.

Step 4 — Classify each row.
Apply UNCOVERED, DRIFT, STALE, and UNKNOWN rules from `protocols/domain-coverage-matrix.md`.

Step 5 — Build reverse index for DRIFT.
For each phase that references design/ concepts, check that each referenced concept exists in design/. Add DRIFT rows for concepts that cannot be found.

Step 6 — Compute summary counts.
Count rows by gap type: OK, UNCOVERED, DRIFT, STALE, UNKNOWN.

Step 7 — Output.
Print the full Coverage Matrix table. Then print the summary:
```
Coverage Matrix — [date]
Total systems: N
OK: N
UNCOVERED: N
DRIFT: N
STALE: N
UNKNOWN: N
```

Step 8 — Update ROADMAP.md.
If a ROADMAP.md exists at the project root, update the "Domain Coverage Summary" section with the counts from step 6. Do not modify any other section of ROADMAP.md. If ROADMAP.md does not exist, append a note: "No ROADMAP.md found. Run roadmap-generation protocol to create one."

## Validation

- `protocols/domain-coverage-matrix.md` exists and defines all three gap types (UNCOVERED, DRIFT, STALE) with detection algorithms.
- `protocols/domain-coverage-matrix.md` contains a Resolution Guidance section.
- `commands/coverage-check.md` exists and contains all 8 steps.
- `commands/coverage-check.md` references `protocols/domain-coverage-matrix.md` by path.

## Gates

| Gate | Type | Path(s) | Condition |
|------|------|---------|-----------|
| coverage-matrix-protocol-exists | file-changed | protocols/domain-coverage-matrix.md | File must exist and be non-empty |
| coverage-check-command-exists | file-changed | commands/coverage-check.md | File must exist and be non-empty |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Design/ files use inconsistent naming, making system ID detection unreliable | Medium | Medium | Detection algorithm uses both frontmatter `id` field and H1 heading as fallback |
| A phase references design/ concepts by paraphrase, not by exact name, causing false DRIFT flags | Medium | Low | DRIFT detection is advisory; human review is required before acting on any gap |
| Coverage check modifies ROADMAP.md incorrectly if the file has custom sections between standard sections | Low | Medium | Step 8 scopes update to the Domain Coverage Summary section only; all other content is untouched |

## Out of Scope

- Automated resolution of any gap type. The coverage check reports gaps; resolution requires human decision via roadmap-refresh.
- Coverage of non-phase artefacts (e.g., SDK modules that are not governed by phases).
- Historical coverage tracking (comparing coverage matrices across time). This block produces a point-in-time matrix only.
