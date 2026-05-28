---
id: block-067
tier: S
kind: protocol
phase: phase-9
scope: phase-bound
status: planned
dependencies: []
files:
  read: []
  modify: []
  create:
    - templates/roadmap.md
    - protocols/roadmap-generation.md
gates:
  - name: roadmap-template-exists
    type: file-changed
    paths: [templates/roadmap.md]
  - name: roadmap-generation-protocol-exists
    type: file-changed
    paths: [protocols/roadmap-generation.md]
created_at: 2026-05-23
---

# block-067 — Roadmap Structure & Template

## Purpose

Every project using this architecture needs a single authoritative document that maps the entire design space to its execution plan. Today, phases are generated one at a time with no macro view of what the full project looks like, what has been built, and what remains. This block establishes that macro view.

The deliverable is two files:

1. `templates/roadmap.md` — the canonical template every project fills when generating its ROADMAP.md. The template is structured so that a reader can answer three questions at a glance: what systems does this project have, which phases build which systems, and which systems are earmarked for perpetual improvement.

2. `protocols/roadmap-generation.md` — a deterministic protocol an AI executor follows to produce a ROADMAP.md from scratch for a new project. The protocol enumerates design/ systems, maps each to a phase, identifies uncovered systems (gaps), identifies phases with no design concept (drift), and outputs the coverage matrix.

This block is the foundation of the 9A sub-stream. No other 9A block can begin until this block is complete, because later blocks (coverage matrix, readiness gate, audit, refresh) all operate on the ROADMAP.md structure defined here.

## Dependencies

None. This is the first block of Phase 9 and the first block of the 9A roadmap sub-stream. It has no upstream dependencies within Phase 9. The only prerequisite is that Phase 8 is complete (phase-level dependency, not block-level).

## Files

### Read
None.

### Modify
None.

### Create

**`templates/roadmap.md`**

The template must contain the following sections in order:

```
---
project: [PROJECT NAME]
version: v1.0
created_at: YYYY-MM-DD
last_updated: YYYY-MM-DD
owner: implementer
---

# ROADMAP — [PROJECT NAME]

## 1. Project Vision

[One sentence. What does this project do and for whom.]

## 2. Domain Systems

[Enumerate every major system identified in design/. One row per system.]

| System ID | System Name | design/ Reference | Description |
|-----------|-------------|-------------------|-------------|
| SYS-001   | [name]      | design/[file].md  | [one line]  |

## 3. Phase Coverage Matrix

[Cross-reference every system against the phase that builds it. Status values: planned / wip / complete / none]

| System ID | System Name | Phase | Phase Status | Notes |
|-----------|-------------|-------|--------------|-------|
| SYS-001   | [name]      | phase-N | planned    |       |

## 4. Domain Coverage Summary

- Total systems: [N]
- Covered by a phase: [N]
- UNCOVERED (no phase assigned): [N]
- DRIFT (phase exists, no design concept): [N]
- STALE (design/ updated after phase last_updated): [N]

## 5. Forever Tracks

[Systems that require perpetual improvement, not one-time delivery.]

| System ID | System Name | Track File | Current Benchmark Target |
|-----------|-------------|------------|--------------------------|
| SYS-XXX   | [name]      | tracks/[name].md | [metric @ value]    |

## 6. Backlog

[Phases planned but not yet started, in intended execution order.]

| Phase | Title | Depends On | Estimated Duration |
|-------|-------|------------|--------------------|
| phase-N | [title] | phase-N-1 | [N days]           |

## 7. Archive

[Phases that are complete.]

| Phase | Title | Completed At | Notes |
|-------|-------|--------------|-------|
| phase-N | [title] | YYYY-MM-DD | |
```

The template must include a comment block at the top of the domain-coverage section that reads:
> Coverage is computed by the `commands/coverage-check.md` command. Run it to refresh this section. Do not edit this section by hand.

**`protocols/roadmap-generation.md`**

The protocol must define the following numbered steps:

1. **Read PROJECT.md.** Extract project name, vision statement, and target users.
2. **Enumerate design/ systems.** Read every file in design/. For each file, extract the system name and a one-line description. Assign a System ID (SYS-001, SYS-002, …). Build the Domain Systems table.
3. **Enumerate existing phases.** Read every file in phases/. For each phase, extract its id, title, and the design/ concepts it addresses (from the phase's Dependencies and Purpose sections). Build a phase→system mapping.
4. **Build the Phase Coverage Matrix.** For each system from step 2, find the phase that builds it (if any). Mark uncovered systems with status "none".
5. **Identify DRIFT.** For each phase from step 3, check whether its claimed design concepts exist in design/. Phases that claim concepts not present in design/ are DRIFT candidates.
6. **Identify STALE.** For each covered system, compare the design/ file's last_updated frontmatter against the phase's last_updated frontmatter. If design/ is newer, mark STALE.
7. **Populate Domain Coverage Summary.** Count totals for each category.
8. **Identify Forever Tracks candidates.** Systems in design/ tagged as perpetual: true (or described as performance-sensitive, scalability-sensitive, or core game-feel) are candidates for Forever Tracks. List them in section 5 with placeholder track file paths.
9. **Write ROADMAP.md.** Output the filled template to the project root as ROADMAP.md.
10. **Report.** After writing, output a summary: "ROADMAP.md generated. N systems covered, N uncovered, N drift, N stale, N track candidates."

## Validation

- `templates/roadmap.md` exists and contains all 7 sections (Vision, Domain Systems, Phase Coverage Matrix, Domain Coverage Summary, Forever Tracks, Backlog, Archive).
- `templates/roadmap.md` contains the "Coverage is computed by" comment in the domain-coverage section.
- `protocols/roadmap-generation.md` exists and contains all 10 numbered steps.
- Both files contain no placeholder text such as "[TBD]" or "[TODO]".

## Gates

| Gate | Type | Path(s) | Condition |
|------|------|---------|-----------|
| roadmap-template-exists | file-changed | templates/roadmap.md | File must exist and be non-empty |
| roadmap-generation-protocol-exists | file-changed | protocols/roadmap-generation.md | File must exist and be non-empty |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Template too rigid — projects with unusual structures cannot fill it | Medium | Medium | Section 2 (Domain Systems) is freeform; only the table headers are required, not a fixed row count |
| Protocol step 6 (STALE detection) fails if frontmatter lacks last_updated | Low | Low | Protocol step 6 includes a fallback: "if last_updated is absent, mark as unknown, not STALE" |
| ROADMAP.md is mistaken for a generated artefact and deleted | Low | Medium | protocols/roadmap-generation.md includes a note that ROADMAP.md is a living document and must be committed to version control |

## Out of Scope

- Auto-filling the roadmap template with project-specific data. The template is a scaffold; filling it is done by the roadmap-generation protocol, not by this block.
- Validation that the ROADMAP.md a project generates is correct. That is the job of commands/coverage-check.md (block-068) and commands/roadmap-audit.md (block-070).
- Tooling to compare two ROADMAP.md versions. Roadmap diffing is not part of Phase 9.
