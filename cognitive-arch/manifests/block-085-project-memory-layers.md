---
id: block-085
tier: S
kind: protocol
phase: phase-11
scope: cross-phase
status: planned
dependencies:
  - block-083
  - block-084
files:
  read:
    - CLAUDE.md
    - protocols/block-close-checklist.md
  modify:
    - CLAUDE.md
    - protocols/block-close-checklist.md
  create:
    - protocols/project-memory-layers.md
gates:
  - name: memory-layers-file-exists
    type: file-changed
    paths:
      - protocols/project-memory-layers.md
      - CLAUDE.md
      - protocols/block-close-checklist.md
  - name: claude-md-references-layers
    type: command
    command: grep -q "project-memory-layers" CLAUDE.md
    expect: exit 0
created_at: 2026-05-23
---

# block-085 — Hierarchical Project Memory

## Purpose

Formally define the three layers of project memory (Developer Experience, User Experience, Agent Experience), document which files belong to each layer and who updates them, wire the layer concept into `CLAUDE.md` and `protocols/block-close-checklist.md`, and create `protocols/project-memory-layers.md` as the canonical reference. This is the Phase 11 capstone: it synthesizes the measurement infrastructure from blocks 081–083 and the benchmark structure from block-084 into a coherent picture of what the AI agent knows, what the user needs, and what the codebase represents.

## Background

The architecture accumulates information in many files: STATE.md, BLOCK_LOG.md, NEXT.md, retros, design files, PROJECT.md, CLAUDE.md, phase files, protocols. Currently these are undifferentiated — any file could be "important." In practice, three distinct audiences exist and need different things:

- The **AI agent** needs to know what work has been done and what comes next (operational state).
- The **user/product owner** needs to know what the system does and where it is going (product vision).
- The **developer** needs to know how the system is built and why decisions were made (technical architecture).

Conflating these three audiences into a flat file list makes it hard to answer: "what does the agent need to re-read when resuming?" or "what files change when we pivot the product?" Separating them makes each category of update intentional.

## Prerequisites

- block-083 complete (health report makes all three layers visible in aggregate)
- block-084 complete (benchmark fields in Track Blocks belong to the DX layer; this block should reflect that)

## Implementation Steps

### Step 1 — Read `CLAUDE.md` and `protocols/block-close-checklist.md`

Read both files in full before making any changes. Note the exact location in `CLAUDE.md` where the HOT read order section is (the list of files the agent should read first when resuming). Note the final step of the block-close-checklist.

### Step 2 — Create `protocols/project-memory-layers.md`

Create the protocol with the following content:

---

# Protocol: Project Memory Layers

## Overview

The architecture maintains three distinct layers of project memory, each serving a different audience and updated on a different cadence. Understanding these layers helps the implementer decide which files to read when resuming work and which files are affected by a given type of change.

---

## Layer 1: Developer Experience (DX)

**What it represents:** What the codebase IS — the technical architecture, design decisions, module structure, protocols, and constraints that define how the system is built.

**Primary audience:** Developers reading the code for the first time, or any agent/human reasoning about implementation options.

**Files in this layer:**
- `design/` — all design concept files, threat models, architecture diagrams
- `protocols/` — all protocol files (block execution, track execution, governance, this file)
- `sdk/` — SDK scripts (represent implemented architecture decisions)
- `templates/` — block, retro, and track-block templates
- `decisions/` — architecture decision records

**Updated when:**
- A block changes the system architecture (new module, new protocol, modified SDK script)
- A Track Block changes how a quality dimension is measured or targeted
- A design decision is made or reversed

**Updated by:** The implementer, as part of block execution. DX files are not updated by routine operational work.

**Cadence:** Per-block, but only when architecture changes. Most blocks do not update DX files.

---

## Layer 2: User Experience (UX)

**What it represents:** What users WANT — the product vision, user-facing goals, threat model from the user's perspective, and the direction the project is heading.

**Primary audience:** Product owners, stakeholders, and any agent reasoning about priorities or scope.

**Files in this layer:**
- `PROJECT.md` — the canonical product vision and goals
- `phase-0/` — all phase-0 discovery and scoping files
- `design/threat-model.md` — user-facing risk and trust model (if present)
- `board.md` — current strategic priorities (if used as a product board)

**Updated when:**
- The product direction changes (major pivot)
- A new user-facing goal is added or removed
- The threat model is revised

**Updated by:** The product owner or implementer after a deliberate decision. UX layer updates are rare and consequential — they should always be accompanied by a decision record in `decisions/`.

**Cadence:** Rarely. Most phases do not update UX files. If a phase is updating `PROJECT.md`, that is a signal to check whether a decision record is needed.

---

## Layer 3: Agent Experience (AX)

**What it represents:** What the AI has DONE — the operational history, current state, next actions, and block-level retrospectives that allow the agent to resume accurately after a session boundary.

**Primary audience:** The AI agent resuming work; also the implementer reviewing project history.

**Files in this layer:**
- `STATE.md` — current phase, current block, last action, blockers
- `NEXT.md` — the single next action the agent should take
- `BLOCK_LOG.md` — the canonical record of all blocks and their status
- `blocks/*/` — all block retro files and working notes
- `governance/` — audit outputs, health reports (generated artifacts)

**Updated when:**
- A block is opened, progressed, or closed
- The health report is generated
- The agent completes any significant action that changes project state

**Updated by:** The agent, at every block transition. AX files are the most frequently updated layer.

**Cadence:** Every block close (mandatory). Also updated mid-block when STATE.md or NEXT.md changes.

---

## Layer Interaction Rules

1. **AX never implies DX.** Completing a block does not automatically update design files. Only update DX files if the block explicitly changed the architecture.
2. **UX changes require a decision record.** Any update to `PROJECT.md` or `phase-0/` must be accompanied by a new file in `decisions/` explaining why.
3. **DX changes should be reflected in AX.** If a block updates `protocols/` or `design/`, the retro should note "DX updated: <file>" so the layer update is traceable.
4. **The health report (block-083) spans all three layers.** It reads AX (BLOCK_LOG, retros), DX (design/, protocols/), and produces a new AX artifact (governance/health-report).

---

## Quick Reference

| Layer | Mnemonic | Key Files | Update Frequency |
|-------|----------|-----------|-----------------|
| DX | What the code IS | design/, protocols/, sdk/, templates/ | Per architecture change |
| UX | What users WANT | PROJECT.md, phase-0/, decisions/ | Rarely (major pivots) |
| AX | What the agent DID | STATE.md, NEXT.md, BLOCK_LOG, blocks/ | Every block close |

---

## See Also

- `protocols/block-close-checklist.md` — includes a layer-check step
- `CLAUDE.md` — HOT read order lists AX files first, then DX
- `commands/health-report.md` — health report reads all three layers

---

### Step 3 — Modify `CLAUDE.md`

Read the HOT read order section. Add the following line at the end of the HOT read order list (or as a note directly after the list):

```
Memory layers: DX=design/, UX=PROJECT.md, AX=STATE.md+BLOCK_LOG — see protocols/project-memory-layers.md.
```

This gives the agent a one-line orientation on the three layers immediately when it reads CLAUDE.md.

### Step 4 — Modify `protocols/block-close-checklist.md`

Read the current final step of the checklist. Append the following as the last step (or second-to-last if there is already a "commit" or "push" final step):

```markdown
## Layer Check

Which memory layer(s) did this block update?

- [ ] **AX only** (normal block close — no architecture or product changes): proceed to commit.
- [ ] **DX updated** (protocols/, design/, sdk/, or templates/ changed): verify the modified DX file accurately reflects the new architecture. Add a note in the retro: "DX updated: <filename>."
- [ ] **UX updated** (PROJECT.md, phase-0/, or decisions/ changed): confirm a decision record exists in decisions/ explaining the change. This is unusual — if unexpected, pause and verify the change was intentional.
```

## Verification

After completing all steps:

```
grep -q "project-memory-layers" CLAUDE.md && echo "CLAUDE.md PASS" || echo "CLAUDE.md FAIL"
```

Also confirm:
- `protocols/project-memory-layers.md` exists and is non-empty
- `protocols/block-close-checklist.md` contains the phrase "memory layer" or "Layer Check"
- `CLAUDE.md` contains the phrase "project-memory-layers"
