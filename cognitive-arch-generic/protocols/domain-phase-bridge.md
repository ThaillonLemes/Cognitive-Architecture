# Domain→Phase Bridge Protocol

BRIEF: Explicit step-by-step protocol for translating domain knowledge from `design/` into well-structured phases. Run this protocol before invoking `protocols/phase-generation.md`. If the readiness precondition fails, generate a questionnaire instead of a phase.

---

## Readiness Precondition

Before starting the bridge, verify:

1. `design/02-domain-overview.md` exists and is not a placeholder (at least 3 named systems documented with descriptions).
2. `PROJECT.md` is fully filled (no `[TBD]`, no unfilled placeholders).
3. At least one additional `design/` file beyond the overview exists (shows domain has depth).

**If any condition fails:** do NOT generate phases. Generate `_brainstorm/domain-questionnaire-YYYY-MM-DD.md` and ask the user to fill it. The AI never generates phases from incomplete domain knowledge.

---

## Step 1 — Enumerate domain systems

Read `design/02-domain-overview.md` and all other `design/` files. Build a list of all named systems:

```
Systems identified:
- [System Name]: [one-line description] | Owner: [who interacts with it] | Depends on: [other systems]
```

If fewer than 3 systems are identified: stop — readiness precondition failed.

---

## Step 2 — Identify user-visible features per system

For each system, identify what a user (player, developer, admin) can experience when that system is functioning. This is the "observable outcome" anchor for phases.

```
System: Combat
  Feature: player can attack an enemy and see health change
  Feature: player dies when health reaches 0
  Feature: abilities have cooldowns that are enforced

System: Inventory
  Feature: player can pick up and drop items
  Feature: items persist across sessions
```

If a system has no user-visible feature: it is infrastructure and must be paired with a system that does have one.

---

## Step 3 — Group into vertical slices

A vertical slice = a set of features that together produce one observable user experience. Each slice becomes one phase (or one phase group if large).

Rules:
- A slice must be deliverable end-to-end (front-end to back-end to persistence).
- A slice should not span more than 2-3 systems.
- A slice must have a "done" moment — when can the user try it?

```
Slice 1: First Connection
  Systems: Auth, Network
  User can: connect to server, authenticate, see other players
  Phases: Phase 1 (Foundation) + Phase 2 (First Connection)

Slice 2: First Combat
  Systems: Combat, Health, World
  User can: fight an enemy in a playable zone
  Phase: Phase 3
```

---

## Step 4 — Order slices by dependency

Some slices cannot start until others exist. Map the dependency order:

```
Slice 1 (Auth + Network) → required before all others
Slice 2 (World loading) → required before Combat
Slice 3 (Combat) → requires World
Slice 4 (Inventory) → independent of Combat, requires World
```

The dependency order determines phase sequence. Earlier slices = earlier phases.

---

## Step 5 — Verify each phase has an observable user outcome

For each phase derived from a slice, write one sentence: "After this phase, a user/developer can ___."

This sentence becomes the anchor for the phase BRIEF and exit criteria. If you cannot write the sentence, the slice is not well-defined — go back to Step 3 and refine.

---

## Step 6 — Run Phase Quality Rubric on each generated phase

Before finalizing any phase, score it against `protocols/phase-quality-rubric.md`.

- Score ≥ 8/10 → accept.
- Score 6–7 → conditional: document failures, get owner sign-off.
- Score ≤ 5 → reject, refine the slice and regenerate.

Do not move to Step 7 until all phases score ≥ 6/10.

---

## Step 7 — Identify systems that need Tracks (not Phases)

Some systems will never be "done" — they need perpetual improvement. These become Tracks, not Phases. Criteria for a Track (from `protocols/track-generation.md`):
- System directly affects performance, latency, or scalability.
- System benefits from iterative benchmarking (not one-time implementation).
- System will receive improvements in every major version.

Separate these systems from the phase list. They will be managed via `tracks/`.

---

## Output

At the end of this protocol, you have:

1. A list of phases (ordered slices), each with:
   - Name and one-paragraph purpose
   - User-visible outcome sentence
   - Systems it implements
   - Dependencies on prior phases

2. A list of systems destined for Tracks.

3. A Phase Quality Rubric score for each proposed phase.

Hand off to `protocols/phase-generation.md` with this structured input to generate the actual phase files.

---

## Out of scope

- Deciding how many blocks each phase has (that is `protocols/phase-generation.md`'s job).
- Defining Track benchmarks (that is `protocols/track-generation.md`'s job).
- Writing block manifests (that is `commands/block-start.md`'s job).

End of domain-phase-bridge.md.
