# Protocol: Project Memory Layers

BRIEF: Three distinct memory layers (DX/UX/AX) serve different audiences and update at different cadences. Knowing which layer a file belongs to clarifies who reads it and when it should change.

**Health report:** `commands/health-report.md` reads all three layers.
**Block close layer check:** `protocols/block-close-checklist.md § Layer Check`

---

## Overview

The architecture maintains three distinct layers of project memory, each serving a different audience and updated on a different cadence. Understanding these layers helps the implementer decide which files to read when resuming work and which files are affected by a given type of change.

| Layer | Mnemonic | Key Files | Update Frequency |
|-------|----------|-----------|-----------------|
| DX | What the code IS | design/, protocols/, sdk/, templates/ | Per architecture change |
| UX | What users WANT | PROJECT.md, phase-0/, decisions/ | Rarely (major pivots) |
| AX | What the agent DID | STATE.md, NEXT.md, BLOCK_LOG, blocks/ | Every block close |

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
- `design/threat-model-*.md` — user-facing risk and trust model (when present)
- `phases/ROADMAP.md` — the macro-level delivery plan (if it exists)

**Updated when:**
- The product direction changes (major pivot)
- A new user-facing goal is added or removed
- The threat model is revised
- The roadmap is refreshed after a `commands/roadmap-refresh.md` run

**Updated by:** The product owner or implementer after a deliberate decision. UX layer updates are rare and consequential — they should always be accompanied by a decision record in `decisions/`.

**Cadence:** Rarely. Most phases do not update UX files. If a phase is updating `PROJECT.md`, that is a signal to check whether a decision record is needed.

---

## Layer 3: Agent Experience (AX)

**What it represents:** What the AI has DONE — the operational history, current state, next actions, and block-level retrospectives that allow the agent to resume accurately after a session boundary.

**Primary audience:** The AI agent resuming work; also the implementer reviewing project history.

**Files in this layer:**
- `STATE.md` — current phase, current block, last action, blockers
- `NEXT.md` — the single next action the agent should take
- `blocks/BLOCK_LOG.md` — the canonical record of all blocks and their status
- `blocks/block-NNN-*.md` — all block retrospective files
- `governance/` — audit outputs, health reports (generated artifacts)
- `tracks/PRIORITY.md` — current Track priorities and stagnation state

**Updated when:**
- A block is opened, progressed, or closed
- The health report is generated
- The Governor updates state after dispatching a sub-agent
- Track priority scores change

**Updated by:** The agent, at every block transition. AX files are the most frequently updated layer.

**Cadence:** Every block close (mandatory). Also updated mid-block when STATE.md or NEXT.md changes.

---

## Layer Interaction Rules

1. **AX never implies DX.** Completing a block does not automatically update design files. Only update DX files if the block explicitly changed the architecture.
2. **UX changes require a decision record.** Any update to `PROJECT.md` or `phase-0/` should be accompanied by a new file in `decisions/` explaining why.
3. **DX changes should be reflected in AX.** If a block updates `protocols/` or `design/`, the retro should note "DX updated: `<filename>`" so the layer update is traceable.
4. **The health report spans all three layers.** It reads AX (BLOCK_LOG, retros, PRIORITY.md), DX (design/, protocols/), and produces a new AX artifact (`governance/health-report-YYYY-MM-DD.md`).
5. **HOT read order prioritizes AX first.** When an agent resumes, it reads STATE.md, NEXT.md (AX) before reading PROTOCOLS.md, INDEX.md (DX) or PROJECT.md (UX).

---

## Session Resume Guide

When resuming work after a context clear, read in this order:

| Priority | Files | Layer | Why |
|----------|-------|-------|-----|
| First | STATE.md, NEXT.md | AX | Immediate operational context |
| Second | PROTOCOLS.md, CLAUDE.md | DX | How to behave |
| Third | INDEX.md | DX | File catalog |
| On demand | design/, protocols/ | DX | Only when block work requires it |
| On demand | PROJECT.md | UX | Only when clarifying goals |

This order minimizes token cost while ensuring the agent can resume correctly.

---

## See Also

- `protocols/block-close-checklist.md § Layer Check` — step at every block close
- `CLAUDE.md § HOT read order` — implements the AX-first session resume guide
- `commands/health-report.md` — health report reads all three layers and generates a new AX artifact

End of project-memory-layers.md.
