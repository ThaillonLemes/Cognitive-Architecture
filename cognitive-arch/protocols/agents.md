# Protocol: Agent lifecycle

BRIEF: Naming, spawn, lifecycle, and coordination rules for agents in Governor v2 and manual modes. Read when creating a new agent OR onboarding a session. Updated for task-packet model (Phase 4).

See: `protocols/task-packet.md` · `protocols/sub-agent-contract.md` · `protocols/convention-snippet-generation.md`

---

## Agent roles

| Role | Identity | Purpose |
|------|----------|---------|
| **Governor** | `governor` | Orchestrates a phase; builds task packets; dispatches sub-agents; integrates returns; owns shared state |
| **Sub-agent (implementer)** | `agent-<group>` or ephemeral | Executes one block; receives task packet; emits return package; never touches shared state |
| **Reviewer** | `agent-reviewer` | Audits block output; gate-check focus |
| **Doc-keeper** | `agent-doc-keeper` | Maintains documentation accuracy |

In Governor v2 mode, sub-agents are often ephemeral (Governor tracks via `sid:` in return package). In manual mode, sub-agents are human-run Claude sessions identified by group.

---

## Sub-agent operating model (Governor v2)

Sub-agents receive **task packets** — not full project context. This is the core design change from v1.x.

| v1.x (full context) | v2.0 (task packet) |
|--------------------|-------------------|
| Sub-agent reads all HOT files at session start | Sub-agent reads task packet header only |
| Sub-agent navigates full cognitive-arch | Sub-agent reads only `fread:` files from task packet |
| Sub-agent writes STATE.md, board.md, NEXT.md | Sub-agent NEVER touches shared state files |
| Sub-agent commits to git | Governor commits after integration |
| Multi-turn conversation | Single task-packet in → single return package out |

Task packet spec: `protocols/task-packet.md`
Template: `templates/task-packet.md`

---

## Sub-agent lifecycle (Governor v2)

```
1. Receive task packet (first message from Governor)
2. Parse header: b, kind, phase, axioms, scope, fread, fmod
3. Read ONLY files listed in fread: (scope discipline)
4. Apply convention snippet (axioms listed in axioms: field)
5. Execute block per manifest
6. Run gates declared in manifest; capture results
7. Write retrospective if retro_req:yes (blocks/block-NNN-slug.md)
8. Emit return package as FINAL message (templates/sub-agent-return.md)
```

Sub-agent NEVER reads: STATE.md, NEXT.md, board.md, BLOCK_LOG.md
Sub-agent NEVER writes: STATE.md, NEXT.md, board.md, BLOCK_LOG.md
Sub-agent NEVER commits to git in Governor v2 mode.

---

## Convention snippets

Sub-agents apply ONLY the axioms listed in the `axioms:` field of the task packet. No need to read full PROTOCOLS.md — Governor pre-selects the relevant axioms per block kind.

Axiom selection: `protocols/convention-snippet-generation.md`
Format: `axioms:Q2,Q3,C2,C3,C6` (comma-separated; sent as part of task packet header)

---

## Governor lifecycle (Governor v2)

```
Session start:
  1. Read STATE.md + NEXT.md → identify current phase and next group
  2. Read phase doc → extract parallel_execution_plan
  3. Initialize governance/governor-state.md

Per parallel group:
  4. Build task packets for each block in group
  5. Dispatch sub-agents simultaneously (SDK parallelism)
  6. Collect return packages
  7. Validate returns (gates, scope, schema)
  8. Integrate modified files (protocols/governor-integration.md)
  9. Update STATE.md, BLOCK_LOG.md, board.md
  10. Commit

Phase complete:
  11. Trigger phase-close flow
```

Governor is stateless between sessions — reads governor-state.md + STATE.md to reconstruct context.
Governor lifecycle detail: `protocols/governor-dispatch.md`

---

## Agent spawn workflow

### Manual mode (governor_mode: manual)

1. User reads phase doc → identifies next group
2. User creates task packet using `templates/task-packet.md`
3. User opens new Claude session (= sub-agent)
4. User pastes task packet as first message
5. Sub-agent executes block, writes retro, emits return package
6. User reads return package, validates gates
7. User updates STATE.md, BLOCK_LOG.md, board.md manually
8. Repeat for next block

No AGENT.md files required in Governor v2 mode. Task packet is the sub-agent's identity document.

### Automated mode (governor_mode: sdk)

Governor handles steps 2-7 via SDK. User monitors board.md and intervenes on `needs-decision` events only. See `protocols/governor-dispatch.md`.

---

## Board.md rows

Each active agent has a row in `board.md`. Governor writes board rows; sub-agents do not.

```
agent:<id> b:<block> group:<group> status:<status> lock:<lock> deps:<deps> ts:<ts>
```

Status transitions (Governor manages):
```
idle → wip (dispatch)
wip → done (return received + all gates pass)
done → integrated (Governor merges to main)
integrated → idle (ready for next block)
```

---

## Agent retirement

An agent retires when assigned blocks are complete and no follow-on blocks remain.

In manual mode: mark board.md row `status:retired`.
In SDK mode: Governor removes the row after integration.
Sub-agent sessions are ephemeral and do not require retirement steps.

---

## Naming conventions

- Governor: `governor` (singular)
- Sub-agents in manual mode: `agent-<group>` (e.g., `agent-4a`, `agent-4b`)
- Sub-agents in SDK mode: ephemeral; Governor assigns `sid:` in task packet
- Reviewer: `agent-reviewer`
- Doc-keeper: `agent-doc-keeper`

---

## When to use fewer sub-agents than possible

Parallelism pays off when a phase has ≥ 5 parallel blocks AND the user can manage N sessions (manual mode). For phases with < 4 parallel blocks or simple doc-only work, sequential execution is often faster due to reduced coordination overhead.

See `protocols/parallelism.md` for phase design rules.

End of agents protocol.
