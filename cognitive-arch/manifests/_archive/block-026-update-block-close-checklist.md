---
id: block-026
tier: S
kind: refactor
phase: phase-4
status: planned
dependencies: [block-018, block-019, block-021]
files:
  read:
    - protocols/block-close-checklist.md
    - design/governor-v2.md
    - protocols/governor-dispatch.md
    - protocols/sub-agent-contract.md
  modify:
    - protocols/block-close-checklist.md
  create: []
gates:
  - name: ownership-annotated
    type: manual
    description: every step in block-close-checklist.md is labeled with either "sub-agent" or "Governor" as owner
  - name: no-steps-removed
    type: manual
    description: all original 8 steps remain; annotations are additions only
  - name: files-updated
    type: file-changed
    paths: [protocols/block-close-checklist.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 026 — Update: block-close-checklist (annotate ownership)

- **Tier:** S
- **Kind:** refactor
- **Status:** planned
- **Dependencies:** block-018, block-019, block-021

## 1. Purpose

Annotate `protocols/block-close-checklist.md` so that each of the 8 close steps is labeled with its owner in the Governor v2 model: either **sub-agent** (step performed by the executing sub-agent) or **Governor** (step performed by the orchestrator). Makes the division of responsibility explicit without changing the steps themselves.

## 2. Files

- **Read:** protocols/block-close-checklist.md, design/governor-v2.md, protocols/governor-dispatch.md, protocols/sub-agent-contract.md
- **Modify:** protocols/block-close-checklist.md (add ownership annotations to each step)
- **Create:** none

## 3. Spec

For each of the 8 steps in block-close-checklist.md, add an ownership tag:

| Step | Title | Owner |
|------|-------|-------|
| 1 | validate_gates | sub-agent |
| 2 | write_state | Governor |
| 3 | write_next | Governor |
| 4 | append_block_log | sub-agent |
| 5 | write_retrospective | sub-agent |
| 6 | update_board | Governor |
| 7 | commit | sub-agent (or Governor, per integration protocol) |
| 8 | emit_next_instruction | Governor |

**Annotation format** — add after each step heading:
```markdown
### Step N — step_name
**Owner (Governor v2): sub-agent**
```

Also add a preamble note at the top of the checklist:
> "In Governor v2 mode, steps are performed by sub-agents or the Governor as indicated. In manual mode, the implementing AI performs all steps."

## 4. Validation

- All 8 steps have an `Owner (Governor v2):` annotation
- No step content is changed — only annotations added
- The preamble note is present

## 5. Out of scope

- Changing how the steps work
- Adding new steps
- Removing steps
