---
id: block-018
tier: S
kind: doc-only
phase: phase-4
status: planned
dependencies: [block-017]
files:
  read:
    - design/governor-v2.md
    - _syntax.md
  modify: []
  create:
    - protocols/task-packet.md
gates:
  - name: protocol-exists
    type: file-exists
    paths: [protocols/task-packet.md]
  - name: format-spec-complete
    type: manual
    description: protocol defines the exact key:value format for task packets, all required fields, optional fields, and a complete example
  - name: references-syntax
    type: manual
    description: protocol references _syntax.md as the vocabulary source for all keys
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 018 — Protocol: task-packet

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Dependencies:** block-017

## 1. Purpose

Create `protocols/task-packet.md` — the full specification for the task packet format that the Governor sends to each sub-agent. A task packet is the minimal context bundle that a sub-agent needs to execute one block in isolation.

## 2. Files

- **Read:** design/governor-v2.md (Section 3), _syntax.md
- **Modify:** none
- **Create:** protocols/task-packet.md

## 3. Spec

`protocols/task-packet.md` must cover:

### What is a task packet
- A compressed _syntax.md key:value block sent as the first message to a sub-agent
- Contains everything the sub-agent needs; Governor does not send full project context

### Required fields
```
b:NNN               # block ID
kind:TYPE           # block kind (doc-only|refactor|enhancement|bugfix|feature)
phase:PHASE-N       # phase this block belongs to
gov:g-NNN           # governor session ID
ts:ISO8601          # timestamp Governor dispatched this
axioms:KEY,KEY,...  # relevant axioms (convention snippet) from PROTOCOLS.md
scope:closed|open   # closed = do exactly what manifest says; open = may discover scope
retro_req:yes|no    # must sub-agent write a retrospective?
tok_track:yes|no    # must sub-agent report token usage?
fread:FILE,...      # files sub-agent should read (comma-separated)
fmod:FILE,...       # files sub-agent will modify or create
```

### Optional fields
```
deps:block-NNN,...  # dependencies (already completed blocks)
notes:TEXT          # Governor notes to sub-agent
deadline_ts:ISO8601 # soft deadline
```

### What is NOT in a task packet
- Full file contents (sub-agent reads files itself)
- Full PROTOCOLS.md (axioms snippet covers what's needed)
- History of other blocks in this phase

### Complete example
```
b:018 kind:doc-only phase:phase-4 gov:g-001 ts:2026-05-21T10:00Z
axioms:Q1,Q3,Q5,C2 scope:closed retro_req:yes tok_track:yes
fread:design/governor-v2.md,_syntax.md fmod:protocols/task-packet.md
```

## 4. Out of scope

- Return package format (→ block-019 / sub-agent-contract)
- Governor dispatch logic (→ block-021)
- Template for task packets (→ block-024)
