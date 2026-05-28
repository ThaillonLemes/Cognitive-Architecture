# Track Generation Protocol

BRIEF: 7-step protocol for identifying which systems need Tracks and creating their Track documents. Run after Phase delivery begins — Tracks are created for systems after (or during) their initial phase, not before.

---

## When to create a Track

Create a Track for a system when:
1. The system has been implemented (or is being implemented in the current phase).
2. The system affects performance, latency, scalability, or consistency in ways users can observe.
3. The system has a measurable benchmark — something you can test and get a number from.
4. You expect to improve the system over multiple iterations across the project's lifetime.

Do NOT create a Track for:
- UI-only features that are not performance-critical
- One-time configuration or setup
- Systems that "work or don't" with no meaningful optimization gradient
- Systems that are completely stable and have no foreseeable improvement path

---

## Step 1 — Identify candidate systems

Read `phases/ROADMAP.md §2 Domain Systems`. Look for systems with status TRACK or BOTH.

Also review any system that:
- Appears in a phase with performance-related exit criteria
- Has been mentioned in any retrospective as a bottleneck
- Is referenced in PROJECT.md constraints (performance, latency, scalability)

---

## Step 2 — Evaluate each candidate

For each candidate system, answer:
1. Can I state a measurable benchmark? (e.g., "p99 latency < 5ms") — if no: not a Track yet.
2. Do I have (or can I build) tooling to measure it? — if no: not a Track yet.
3. Will this be a meaningful bottleneck to optimize beyond the initial implementation? — if no: not a Track.

If all 3 answers are yes: proceed to create the Track.

---

## Step 3 — Define the initial benchmark target

The benchmark target is realistic, not aspirational. Use:
- Industry standards for the system type (e.g., <10ms round-trip for real-time game networking)
- Current measured performance as baseline × 0.7 (30% improvement as first target)
- User experience threshold (e.g., "users notice lag above 100ms")

Set the target conservatively — it will be tightened as the system improves.

---

## Step 4 — Set initial priority score

Default: `priority_score: 5` (neutral).

Adjust based on:
- **bottleneck_score:** Is this the current bottleneck? 8-10 = yes, critical. 3-5 = moderate. 0-2 = not currently a bottleneck.
- **stagnation_score:** 0 for a new Track (no failed attempts yet).
- **user_priority:** How much does this affect user experience? 8-10 = core gameplay. 3-5 = noticeable but not critical. 0-2 = internal only.

See `protocols/track-priority.md` for the full formula.

---

## Step 5 — Fill the Track document

Copy `templates/track.md`. Fill all fields:
- `system:` — exact system name (match design/ file naming)
- `description:` — one-line description
- `benchmark_target:` — from Step 3
- `benchmark_unit:` — the unit of the metric
- `priority_score:` — initial total from Step 4
- Technical Context section — include file locations, data structures, benchmark tools

Save to `tracks/[system-name].md`.

---

## Step 6 — Update ROADMAP.md §4

Add the new Track to `phases/ROADMAP.md §4 Forever Tracks` table.

Update the system's status in §2 Domain Systems from COVERED to COVERED+TRACK or from UNCOVERED to TRACK.

---

## Step 7 — Update tracks/PRIORITY.md

Add a row for the new Track. Use the initial priority score from Step 4. See `tracks/PRIORITY.md` template.

---

## Out of scope

- Executing Track Blocks (that is `protocols/track-block-execution.md`).
- Deciding which Track to work on next (that is `protocols/track-priority.md`).
- Creating benchmark tooling (that is the Track Block's job — document existing tooling, or create it in the first Track Block).

End of track-generation.md.
