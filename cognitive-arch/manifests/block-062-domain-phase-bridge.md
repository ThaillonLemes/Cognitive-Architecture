---
id: block-062
tier: S
kind: protocol
phase: phase-8
scope: phase-bound
status: planned
dependencies:
  - block-061
files:
  read:
    - protocols/phase-quality-rubric.md
    - design/02-domain-overview.md
  create:
    - protocols/domain-phase-bridge.md
gates:
  - name: bridge-file-exists
    type: file-changed
    paths: [protocols/domain-phase-bridge.md]
  - name: bridge-references-design
    cmd: grep -qi "design/" protocols/domain-phase-bridge.md
    expect: "exit 0"
  - name: bridge-references-rubric
    cmd: grep -qi "phase-quality-rubric" protocols/domain-phase-bridge.md
    expect: "exit 0"
created_at: 2026-05-23
---

# Block 062 — Domain→Phase Bridge

- **Tier:** S
- **Kind:** protocol
- **Status:** planned

---

## 1. Purpose

Create `protocols/domain-phase-bridge.md`, an explicit step-by-step protocol for translating domain knowledge from `design/` into well-structured phases. Without a bridge protocol, the AI jumps directly from a vague feature request to generating a phase, skipping the structured analysis of what systems exist, what users need, and what order things must be built. The result is phases that do not align with the domain model or that skip prerequisite work.

**Target file to create:** `protocols/domain-phase-bridge.md`

**The protocol must define the following 7 steps:**

**Step 1 — Readiness Precondition Check**
Before invoking the bridge, verify that `design/02-domain-overview.md` exists and contains at least one documented system. If the file does not exist or contains only placeholder text, halt and request that the design be populated first. The bridge is not useful with no domain knowledge.

**Step 2 — Enumerate All Systems**
Read `design/02-domain-overview.md` and list every system, subsystem, or major component documented there. Record each as a bullet: `- [system name]: [one-line description]`. This list becomes the raw input for phase planning.

**Step 3 — Identify User-Visible Features per System**
For each system identified in Step 2, list the features that a user or developer would directly observe or interact with. Internal wiring (database migrations, refactors, config changes) may be necessary but are not themselves user-visible features. Record each feature as: `- [system] / [feature]: [what the user can do after this exists]`.

**Step 4 — Group Features into Vertical Slices**
A vertical slice is a coherent set of features that together produce one observable user outcome. Group the features from Step 3 into slices. A slice becomes a candidate phase. Slices should be narrow enough to complete in ≤5 days and broad enough to produce something demonstrably working. If a slice cannot be experienced by a user after completion, it is not a valid slice — split or merge accordingly.

**Step 5 — Order Slices by Dependency**
Determine which slices depend on other slices. A slice depends on another if it requires a file, module, schema, or protocol that the other slice creates. Record dependencies explicitly: `phase-N depends on phase-M because [reason]`. Build a DAG. If cycles exist, they indicate a design flaw — resolve by splitting a slice or identifying the minimal shared precondition as its own earlier phase.

**Step 6 — Verify Each Phase Produces an Observable Outcome**
For each ordered slice, write a one-sentence "user can experience X" statement. This statement becomes the seed for the phase BRIEF and the "user-visible outcome" criterion in the Phase Quality Rubric. If no such statement can be written, the slice is not a valid phase — merge it with an adjacent slice or mark it as infrastructure and track it separately.

**Step 7 — Run Phase Quality Rubric on Each Generated Phase**
After drafting each phase file, score it against `protocols/phase-quality-rubric.md`. Record the score. If a phase scores below 8/10, do not proceed to block work. Instead, refine the phase: narrow scope, add measurable exit criteria, split large blocks, or add test gates. Re-score until ≥8/10 or owner sign-off is documented.

**The protocol must also define:**

- **Readiness precondition:** `design/02-domain-overview.md` must exist with at least one documented system before the bridge is invoked. If it does not exist, run the bridge only after documenting at least one system in `design/`.
- **When to invoke:** The bridge is invoked at the start of planning a new phase, before generating any phase draft. It may also be invoked mid-project when the domain model changes significantly.
- **Anti-patterns to avoid:**
  - Generating a phase from a single user request without consulting `design/`.
  - Creating phases that span more than one vertical slice (produces over-scoped phases).
  - Ordering phases by "what feels natural" rather than dependency analysis.

---

## 2. Dependencies

- **block-061** — `protocols/phase-quality-rubric.md` must exist before this protocol can reference it in Step 7.

---

## 3. Files

**Read:**
- `protocols/phase-quality-rubric.md` — to reference the rubric correctly in Step 7 of the bridge protocol.
- `design/02-domain-overview.md` — to validate that the readiness precondition is met and to understand the format of domain documentation the protocol will reference.

**Create:**
- `protocols/domain-phase-bridge.md` — the full 7-step bridge protocol with preconditions, anti-patterns, and invocation guidance.

---

## 4. Validation

- `protocols/domain-phase-bridge.md` exists on disk.
- File contains all 7 steps (numbered 1–7) with explicit action instructions.
- File references `design/` at least once (for the readiness precondition).
- File references `phase-quality-rubric` at least once (for Step 7).
- Each step has a concrete action verb, not just a description.

---

## 5. Gates

| Gate | Type | Check |
|---|---|---|
| `bridge-file-exists` | file-changed | `protocols/domain-phase-bridge.md` modified/created |
| `bridge-references-design` | content | file contains "design/" |
| `bridge-references-rubric` | content | file contains "phase-quality-rubric" |

---

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `design/02-domain-overview.md` does not exist or is sparse | Medium | Low | Protocol's readiness precondition explicitly handles this case |
| Bridge steps are too abstract to follow | Low | Medium | Each step includes a concrete output format (bullet lists, DAG, one-sentence outcome) |
| Protocol is bypassed when planning feels urgent | Medium | Medium | `commands/phase-start.md` will reference the bridge after block-066; bypass requires explicit owner decision |

---

## 7. Out of scope

- Automating the bridge steps as a script.
- Modifying any `design/` files.
- Modifying any command files (that is block-066's responsibility).
- Defining the format of `design/02-domain-overview.md` (that belongs to design-layer blocks).
