# agent-roles — pre-built agent role definitions

BRIEF: Reusable role templates. When creating an `AGENT.md` for a new agent, copy the role file as the basis, then customize via `templates/AGENT.md` frontmatter.

## Roles in v1

| Role | File | Purpose |
|------|------|---------|
| Implementer | `implementer.md` | Default block worker (writes code per manifest) |
| Governor | `governor.md` | Integrator + auditor (never implements) |
| Reviewer | `reviewer.md` | Quality findings (no code changes) |
| Doc-keeper | `doc-keeper.md` | Documentation consistency maintenance |

## How to use

1. Open `templates/AGENT.md`.
2. Read the role file matching your desired agent role.
3. Copy `templates/AGENT.md` to `agents/agent-<name>.md`.
4. In the `role:` frontmatter field, set to one of: `implementer`, `governor`, `reviewer`, `doc-keeper`.
5. Customize scope (group, blocks, worktree, branch).
6. The AGENT.md references this role's file for behavior details.

## Role characteristics (quick reference)

| Role | Default mode | Implements? | Integrates? | Audits? |
|------|--------------|-------------|-------------|---------|
| Implementer | guidance | ✓ | ✗ | ✗ |
| Governor | guardrails | ✗ | ✓ | ✓ |
| Reviewer | guardrails | ✗ | ✗ | partial (findings only) |
| Doc-keeper | guardrails | doc-only | ✗ | doc-only |

## Adding a new role (post-v1)

Project-specific roles (e.g., `bug-hunter-rust`, `security-auditor-web`) belong in the project's own `agents/` folder. They follow the same structure as roles here but live in the project, not in the cognitive architecture.

For roles that should be GENERIC across all projects, propose them via ADR and add to this folder.

## Pointers

- `templates/AGENT.md` — the AGENT.md template that references these roles
- `protocols/modes.md` — guidance/guardrails/checklist mode definitions
- `protocols/agents.md` — agent lifecycle, naming, spawn workflow
