---
id: block-027
manifest: manifests/block-027-update-agents-protocol.md
status: done
gates_passed: 5/5
completed_at: 2026-05-21
agent: implementer
commit: -
duration_actual_days: 1
tok_estimated: ~5000
tok_src: estimated
---

# Block 027 Retrospective — Update: protocols/agents.md (task-packet model)

## 1. What was built

- Rewrote `protocols/agents.md` for Governor v2 task-packet model
- v1.x vs v2.0 operating model comparison table
- Updated sub-agent lifecycle (8 steps: receive packet → parse → read fread → apply axioms → execute → gates → retro → return)
- Convention snippets section (references protocols/convention-snippet-generation.md)
- Updated Governor lifecycle (11 steps)
- Agent spawn workflow for manual mode (8 steps) and automated mode
- Board.md row state transitions table (Governor manages)
- Updated naming conventions (ephemeral sub-agents in SDK mode)
- Preserved: role definitions, board.md integration, manual mode instructions

## 2. Tests added

None. Refactor block.

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| task-packet-model | ✓ | Operating model table + "task packets, not full context" stated explicitly |
| lifecycle-updated | ✓ | 8-step lifecycle matches sub-agent-contract.md |
| backward-compatible | ✓ | Manual mode spawn workflow (8 steps) preserved |
| references-new-protocols | ✓ | Links to task-packet.md, sub-agent-contract.md, convention-snippet-generation.md, templates |
| files-updated | ✓ | protocols/agents.md, STATE.md, NEXT.md, BLOCK_LOG.md updated |

## 4. Decisions made

Removed AGENT.md section — Governor v2 sub-agents are ephemeral and use task packets as identity documents; AGENT.md per sub-agent is deprecated per brainstorm §file-inventory.

## 5. Deferred to future blocks

None.

## 6. Token estimate

```
tok_estimated: ~5000  tok_src:estimated
```

## 7. Issues / surprises

None.

## 8. Files actually touched

- Modified: `protocols/agents.md` (full rewrite)
- As manifest otherwise.

---

End of retrospective.
