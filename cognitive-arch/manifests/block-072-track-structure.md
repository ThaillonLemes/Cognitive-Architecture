---
id: block-072
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
    - tracks/README.md
    - templates/track.md
    - protocols/track-generation.md
gates:
  - name: tracks-readme-exists
    type: file-changed
    paths: [tracks/README.md]
  - name: track-template-exists
    type: file-changed
    paths: [templates/track.md]
  - name: track-generation-protocol-exists
    type: file-changed
    paths: [protocols/track-generation.md]
created_at: 2026-05-23
---

# block-072 — Track Structure & Template

## Purpose

Certain categories of software have no terminal "done" state. An MMORPG's combat system must feel tighter with every major release. A trading platform's order matching engine must reduce latency as volume grows. A simulation engine's physics must become more accurate as hardware improves. For these systems, conventional phase-based delivery — build it, ship it, move on — produces software that ossifies.

This block introduces the Track System: a structural distinction between delivery work (Phases) and perpetual improvement work (Tracks).

**Phases** build software. They are linear (have a defined start and end), have exit criteria (you can be done with a phase), and map to design/ concepts that were designed upfront.

**Tracks** improve software. They are perpetual (no terminal state), have benchmark targets (you are never done, but you can measure progress), and correspond to systems that need ongoing investment rather than one-time construction.

The deliverables are:

1. `tracks/README.md` — explains the Track concept to anyone reading the project for the first time, and documents the conventions for Track files.
2. `templates/track.md` — the canonical template for a Track document. Includes benchmark target, priority score, improvement history, and open hypotheses.
3. `protocols/track-generation.md` — the protocol for identifying which systems in a project need Tracks, and the criteria for creating one.

This block is independent of the 9A roadmap stream. It can execute in parallel with blocks 067–071.

## Dependencies

None. This is the first block of the 9B Track sub-stream. It has no upstream dependencies within Phase 9. The only prerequisite is that Phase 8 is complete (phase-level dependency).

## Files

### Read
None.

### Modify
None.

### Create

**`tracks/README.md`**

Must contain:

```
# Track System

## What is a Track?

A Track is a perpetual domain improvement stream. Unlike a Phase, a Track has no exit criteria and is never "done." Instead, a Track has a **benchmark target** — a measurable performance or quality threshold that the system should approach over time.

Tracks exist for systems where improvement is continuous and the cost of stagnation is real. A combat system that felt great at launch but hasn't been tuned in two years is stale. An AI opponent that played at a specific Elo when shipped but has never been improved falls behind player expectations. Tracks make this maintenance obligation explicit and measurable.

## Phases vs Tracks

| Dimension | Phase | Track |
|-----------|-------|-------|
| Purpose | Build the system | Improve the system |
| Lifecycle | Linear: planned → wip → complete | Cyclical: measured → hypothesis → wip → measured |
| Completion | Has exit criteria — can be done | Has benchmark targets — never done |
| Blocks | Phase Blocks (one-time execution) | Track Blocks (reopenable, iterative) |
| Priority | Determined by phase dependency order | Determined by bottleneck scores (see tracks/PRIORITY.md) |
| Design basis | design/ concept | Ongoing measurement + hypothesis |

## When to Create a Track

Create a Track when a system meets any of the following criteria:

1. The system's quality directly affects user retention or engagement (e.g., game-feel systems, latency-sensitive APIs).
2. The system has a measurable performance dimension that degrades without attention (e.g., query latency, frame time, AI difficulty).
3. The project's domain is explicitly "forever software" — no planned end-of-life.
4. The system is listed as perpetual in its design/ file.

Do NOT create a Track for:
- Feature systems that are purely additive (each release adds features, nothing needs tuning).
- Systems that are fully automated and self-correcting (their own feedback loops handle improvement).
- Systems that are scheduled for deprecation.

## Track File Conventions

- Track files live in `tracks/`.
- Track filenames are `tracks/[system-slug].md` (e.g., `tracks/combat-system.md`).
- Special files in `tracks/` are: README.md (this file), PRIORITY.md (priority table), and _placeholder.md (git placeholder).
- Track files use the template at `templates/track.md`.
- Track Blocks are stored alongside the Track file or in `tracks/blocks/[system-slug]-block-NNN.md`.

## Track File Index

| Track ID | System | File | Current Benchmark Target | Priority Score |
|----------|--------|------|--------------------------|----------------|
| [TRK-001] | [system name] | tracks/[slug].md | [metric @ value] | [N] |

> Update this table whenever a new Track is created or a benchmark target changes.
```

---

**`templates/track.md`**

Must contain:

```
---
id: TRK-[NNN]
system: [System Name]
system_id: [SYS-NNN]
design_ref: design/[file].md
description: [One sentence: what does this Track improve?]
current_benchmark_target: [metric] @ [value] [unit]
benchmark_unit: [unit of measurement, e.g., ms, fps, elo, req/s]
priority_score: 0
bottleneck_score: 0
stagnation_score: 0
user_priority: 0
created_at: YYYY-MM-DD
last_improved_at: YYYY-MM-DD
owner: implementer
perpetual: true
---

# Track: [System Name]

## System

[2–4 sentences describing the system this Track improves. What does the system do? Why does it need perpetual improvement?]

## Benchmark Target

The current benchmark target is: **[metric] @ [value] [unit]**

This target was set on [DATE] based on [rationale: user feedback / competitive analysis / performance profiling / etc.].

When this target is achieved, the target will be raised to [next target] and a new Track Block will be planned.

## Benchmark Unit

[Explain what is being measured and how. E.g.: "Frame time measured in milliseconds, averaged over a 60-second gameplay session with 50 simultaneous entities on screen."]

## Priority Score

Current priority score: **[N]** (as of [DATE])

Formula: `(bottleneck_score × 3) + (stagnation_score × 1) + (user_priority × 2)`

| Factor | Value | Weight | Contribution |
|--------|-------|--------|--------------|
| bottleneck_score | [N] | ×3 | [N] |
| stagnation_score | [N] | ×1 | [N] |
| user_priority | [N] | ×2 | [N] |
| **Total** | | | **[N]** |

See `tracks/PRIORITY.md` for how to update scores.

## Improvement History

| Date | Track Block | Benchmark Before | Benchmark After | Delta | Notes |
|------|-------------|-----------------|-----------------|-------|-------|
| YYYY-MM-DD | TRK-[NNN]-BLK-001 | [value] | [value] | [+/-N%] | [notes] |

## Open Hypotheses

[List of hypotheses for why performance is not at target yet, and what changes might improve it.]

1. Hypothesis: [What we think is causing the gap.] Confidence: [Low/Medium/High]. Next action: [What Track Block to run to test this.]
2. [Additional hypotheses as discovered.]

## Track Blocks

| Block ID | Status | Hypothesis | Result |
|----------|--------|------------|--------|
| TRK-[NNN]-BLK-001 | [planned|wip|measured] | [brief hypothesis] | [brief result or pending] |

## Notes

[Any additional context about this Track: constraints, known dead ends, external factors affecting the benchmark.]
```

---

**`protocols/track-generation.md`**

Must contain:

**Purpose**: Define which systems in a project need Tracks, and the procedure for creating a Track file from the template.

**Section 1 — Identification Criteria**

A system qualifies for a Track if it meets at least one of the following:

- The system's design/ file contains `perpetual: true` in frontmatter.
- The system's design/ file description uses any of the phrases: "performance-sensitive", "scalability-sensitive", "core game-feel", "perpetual improvement", "ongoing tuning", "never finished."
- The system's domain is inherently improvement-driven: AI/ML models, physics simulations, matchmaking algorithms, audio mixing engines, rendering pipelines, network synchronisation.
- The project is classified as "forever software" in PROJECT.md (e.g., field `software_lifecycle: forever` or similar).

A system does NOT qualify if:
- It is purely a feature container (adding new abilities/items/screens is not improvement of an existing system).
- It is scheduled for deprecation or replacement within 2 major versions.
- Its quality is self-correcting (automated tuning loops handle it).

**Section 2 — Generation Procedure**

Step 1: Identify candidate systems. Read all design/ files. Apply identification criteria. Build a candidate list.

Step 2: For each candidate, determine the benchmark unit. Ask: "What is the one number that best represents how well this system is performing right now?" Common choices: latency (ms), throughput (req/s), frame time (ms), AI difficulty rating (elo), user retention rate (%), error rate (%).

Step 3: Determine the initial benchmark target. The target should be: current measured value × 1.20 (20% improvement) if no specific target exists, or the specific value from the design/ file or product requirements.

Step 4: Create the Track file. Copy `templates/track.md`, fill all frontmatter fields, write the System section, set benchmark target and unit, set all priority scores to 0 (initial state), leave Improvement History empty, write at least one Open Hypothesis.

Step 5: Add the Track to `tracks/README.md`'s Track File Index table.

Step 6: Add the Track to `tracks/PRIORITY.md`'s priority table with all scores at 0.

Step 7: Report: "Track created: TRK-[NNN] for [system name]. Benchmark target: [metric @ value]. Priority score: 0 (not yet prioritised — update bottleneck_score in tracks/PRIORITY.md)."

**Section 3 — Track ID Assignment**

Track IDs are assigned sequentially: TRK-001, TRK-002, etc. The ID is global across all tracks/ files. Check existing Track files to determine the next available ID.

## Validation

- `tracks/README.md` exists and contains the Phases vs Tracks comparison table.
- `tracks/README.md` contains "When to Create a Track" section with at least 4 criteria.
- `templates/track.md` exists and contains the `benchmark_target` field in frontmatter.
- `templates/track.md` contains Improvement History table, Open Hypotheses section, and Priority Score section.
- `protocols/track-generation.md` exists and contains identification criteria and a generation procedure with at least 7 steps.

## Gates

| Gate | Type | Path(s) | Condition |
|------|------|---------|-----------|
| tracks-readme-exists | file-changed | tracks/README.md | File must exist and be non-empty |
| track-template-exists | file-changed | templates/track.md | File must exist and contain benchmark_target field |
| track-generation-protocol-exists | file-changed | protocols/track-generation.md | File must exist and be non-empty |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Track concept is confused with Phase concept by future AI executors | Medium | Medium | tracks/README.md contains explicit Phases vs Tracks comparison table with 6 dimensions |
| benchmark_unit is set inconsistently across Track files | Medium | Low | protocols/track-generation.md Step 2 requires explicit benchmark unit definition before creating the file |
| Too many Tracks are created for systems that don't need them | Medium | Low | Identification criteria include explicit "does NOT qualify" list to limit scope |

## Out of Scope

- Automated measurement infrastructure. Tracks define what to measure; instrumentation is outside this block.
- Track dashboards or visualisation. All Track data is in markdown files.
- Cross-project Track sharing. Tracks are project-local.
