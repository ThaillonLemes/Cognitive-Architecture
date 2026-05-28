# Protocol: Task packet

BRIEF: Spec for the task packet the Governor sends to each sub-agent. A task packet is the minimal context bundle needed to execute one block in isolation. All keys use `_syntax.md` vocabulary.

Design authority: `design/governor-v2.md §4`

---

## What is a task packet

A compressed `_syntax.md` key:value block that is the FIRST message sent to a sub-agent when Governor dispatches it. It contains everything the sub-agent needs to start. Governor does NOT send the full project context.

Contents:
1. **Compressed header** — required + optional fields (key:value)
2. **Convention snippet** — 10-15 line axiom selection from PROTOCOLS.md (see `protocols/convention-snippet-generation.md`)
3. **Manifest** — full verbatim content of `manifests/block-NNN-slug.md`

Sub-agent reads additional files itself using `fread:` list.

---

## Required fields

```
b:NNN               block ID (e.g., b:018)
kind:TYPE           doc-only | refactor | implementation | gate | discovery
phase:phase-N       phase this block belongs to (e.g., phase:phase-4)
gov:g-ID            Governor session ID (e.g., gov:g-001)
ts:ISO8601          timestamp Governor dispatched (e.g., ts:2026-05-21T10:00Z)
axioms:K,K,...      comma-separated axiom IDs — the convention snippet reference
scope:MODE          closed | open | two-phase  (see Scope modes below)
retro_req:yes|no    sub-agent must write a retrospective
tok_track:yes|no    sub-agent must report token usage in return package
fread:path,...      files sub-agent reads for context (comma-separated paths)
fmod:path,...       files sub-agent will modify or create (comma-separated paths)
```

---

## Optional fields

```
deps:block-NNN,...  blocks already integrated (informational only; not an action trigger)
notes:TEXT          Governor freetext note to sub-agent (rare; use sparingly)
deadline_ts:ISO8601 soft completion deadline (Governor uses for fallback-timer logic)
sid:s-ID            SDK sub-agent session ID assigned by Governor before dispatch
```

---

## What is NOT in a task packet

| Excluded | Reason |
|----------|--------|
| Full file contents | Sub-agent reads files directly via `fread:` |
| Full PROTOCOLS.md | Convention snippet contains only relevant axioms |
| History of other blocks in this phase | Sub-agent is stateless; doesn't need cross-block context |
| STATE.md / NEXT.md | Sub-agent never reads or writes these |
| Board.md | Governor-only; sub-agent has no orchestration visibility |

---

## Scope modes

| `scope:` | Behavior | Used for |
|----------|----------|---------|
| `closed` | Sub-agent reads and writes ONLY declared files | Gates, simple doc blocks |
| `open` | Sub-agent may read any project file (read-only beyond fmod) | Doc, refactor, simple implementation |
| `two-phase` | Discovery pass first → Governor approves scope → execution pass | Complex implementation blocks |

Sub-agent reports all files actually read in return package `fread:` field. Governor uses this to improve future task packets.

---

## Axiom selection (convention snippet)

`axioms:` field lists the axiom IDs relevant to this block's `kind`. Governor generates this per `protocols/convention-snippet-generation.md`.

| `kind:` | Typical axioms |
|---------|---------------|
| `doc-only` | C2, C6 |
| `refactor` | C2, C3, C6, Q4, Q6 |
| `implementation` | Q1, Q3, Q4, Q5, Q6, C1, C5 |
| `gate` | Q4 |
| `discovery` | Q4, Q6, C2 |

Governor embeds the axiom text (10-15 lines) after the header.

---

## Full example

```
b:018 kind:doc-only phase:phase-4 gov:g-001 ts:2026-05-21T10:00Z
axioms:C2,C6 scope:closed retro_req:yes tok_track:yes
fread:design/governor-v2.md,_syntax.md fmod:protocols/task-packet.md

--- convention snippet ---
C2: Do not speculate. If you are uncertain, halt and ask.
C6: Retrospective entries are facts only. No narrative.

--- manifest ---
[full content of manifests/block-018-protocol-task-packet.md]
```

---

## Validation checklist (Governor, before dispatch)

- [ ] All required fields present
- [ ] `fmod:` matches manifest `files.modify` + `files.create`
- [ ] `fread:` matches manifest `files.read`
- [ ] `scope:` matches block kind (see table above)
- [ ] `axioms:` generated per `protocols/convention-snippet-generation.md`
- [ ] Convention snippet appended after header
- [ ] Manifest appended after convention snippet

End of task-packet protocol.
