---
id: block-028
tier: S
kind: refactor
phase: phase-4
status: planned
dependencies: [block-021, block-022]
files:
  read:
    - protocols/parallelism.md
    - design/governor-v2.md
    - protocols/governor-dispatch.md
    - phases/phase-4.md
  modify:
    - protocols/parallelism.md
  create: []
gates:
  - name: phase-design-rules
    type: manual
    description: protocols/parallelism.md includes a section on phase design rules (intra-phase only, merge themes, maximize parallel groups)
  - name: parallel-group-format
    type: manual
    description: protocol documents the parallel_execution_plan YAML format used in phase docs
  - name: no-cross-phase
    type: manual
    description: protocol explicitly states that cross-phase parallelism is out of scope (v3.0+) and explains why
  - name: files-updated
    type: file-changed
    paths: [protocols/parallelism.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 028 — Update: protocols/parallelism.md (phase design rules)

- **Tier:** S
- **Kind:** refactor
- **Status:** planned
- **Dependencies:** block-021, block-022

## 1. Purpose

Update `protocols/parallelism.md` to include phase design rules — specifically: (1) intra-phase parallelism only, (2) how to design phases to maximize parallel groups, and (3) the parallel_execution_plan YAML format. These rules were established in the Governor v2 brainstorm (Decision 10) and need to be codified in the protocols.

## 2. Files

- **Read:** protocols/parallelism.md (current), design/governor-v2.md (Decision 10), protocols/governor-dispatch.md, phases/phase-4.md (as example of parallel_execution_plan)
- **Modify:** protocols/parallelism.md (add new section on phase design rules)
- **Create:** none

## 3. Spec

**Add a new section to protocols/parallelism.md:**

### Phase design rules (new section)

**Principle:** Maximize intra-phase parallelism; avoid cross-phase parallelism.

**Why not cross-phase parallelism?**
- Cross-phase dependencies are complex to manage without distributed state
- The cognitive architecture's parallelism machinery (board.md, governor-state.md) is designed for intra-phase scope
- Cross-phase parallelism deferred to v3.0+

**Instead — merge themes:**
If two independent themes have no conflicts, merge them into one larger phase with parallel groups.
Example: Token metering + schema validation could be one phase if they don't conflict.
(In practice, kept as separate phases for narrative clarity — but merged phases are valid.)

**Phase design decision tree:**
```
New theme to add?
├── Does it conflict with any current phase? → separate phase
├── Does it depend on a current phase? → depends_on that phase
└── Fully independent? → merge into next phase as additional parallel group
```

**parallel_execution_plan YAML format:**
```yaml
parallel_execution_plan:
  total_blocks: N
  recommended_agents: N
  groups:
    - id: PHASE-LETTER        # e.g., 4A, 4B, 4C
      blocks: [block-NNN, ...] # list of block IDs in this group
      type: sequential|parallel
      depends_on: []           # group IDs this group depends on
      note: human description
```

**Group execution rules:**
- All blocks in a `parallel` group dispatch simultaneously
- A group does not start until all groups in its `depends_on:` list are complete
- A `sequential` group has one block; still listed as a group for uniformity

**File conflict detection:**
- Two blocks in the same parallel group must not share any path in their `fmod:` lists
- Governor validates this before dispatch; conflict = re-sequence or split

## 4. Validation

- protocols/parallelism.md has "phase design rules" section (or equivalent heading)
- parallel_execution_plan YAML format is documented
- Cross-phase parallelism explicitly noted as deferred (v3.0+)
- File conflict detection rule stated

## 5. Out of scope

- Cross-phase parallelism implementation
- Automated conflict detection tooling (Phase 5)
- Block scheduling algorithms
