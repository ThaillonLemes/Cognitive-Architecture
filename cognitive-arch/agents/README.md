# agents — AGENT.md per active agent

BRIEF: One file per agent. Identity card the agent reads at every session start. Created by Governor or user during multi-agent setup.

## What lives here

| Path | Purpose |
|------|---------|
| `agent-<name>.md` | Implementer agent (e.g., agent-1a, agent-1b) |
| `governor.md` | The Governor agent (one per project) |
| `agent-reviewer.md` | Reviewer agent (optional) |
| `agent-doc-keeper.md` | Doc-keeper agent (optional) |

## Creation

When you spawn an agent:

1. Read `templates/AGENT.md` (the template)
2. Read `templates/agent-roles/<role>.md` (the role definition)
3. Copy template + customize frontmatter for this specific agent
4. Save to `agents/agent-<name>.md`

See `protocols/agents.md` for the full lifecycle.

## Naming

- Implementer for parallel group: `agent-<group>` (e.g., `agent-1a`)
- Implementer for specific feature: `agent-<feature>` (e.g., `agent-auth`)
- Governor: `governor` (singular)
- Reviewer: `agent-reviewer`
- Doc-keeper: `agent-doc-keeper`
- Project-specific: `agent-<role>`

## Why these files persist

AGENT.md is the only thing that survives `/clear`. After clearing a session, when the user pastes "you are agent-1a, read AGENT.md", the new session re-discovers its identity from disk.

Without AGENT.md, identity has to be re-pasted manually every session.

## Retiring an agent

When an agent has completed its assigned work:
- Update its row in board.md: `status:retired`
- Optionally remove its worktree
- Keep `agent-<name>.md` for history (don't delete)

## Multi-agent reminder

For SINGLE-agent projects, you may not need any files here. The default implementer behavior (per `templates/agent-roles/implementer.md`) suffices.

For MULTI-agent projects, an AGENT.md per implementer is the cleanest way to manage identity across sessions.
