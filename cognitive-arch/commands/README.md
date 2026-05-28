# commands — operational commands for the AI to follow

BRIEF: Each file describes a single command. The AI reads the relevant command file and follows it step-by-step. Commands are not executed; they are READ AND APPLIED.

## Files

| Command | Purpose | Mode |
|---------|---------|------|
| `run.md` | Master command — decides next step automatically | depends on sub-command |
| `audit.md` | Run audit checks | checklist |
| `integrate.md` | Governor: merge completed worktrees into main | checklist |
| `status.md` | Display project status | checklist (presentation) |
| `block-start.md` | Start a new block | guardrails → guidance |
| `block-close.md` | Close a block (8-step protocol) | checklist |
| `phase-start.md` | Open a new phase | guardrails |
| `phase-close.md` | Close a phase | checklist |
| `governor.md` | Governor agent session script | guardrails / checklist |
| `scan-quality.md` | One-off code quality scan | guardrails |
| `scan-deps.md` | One-off dependency scan | guardrails |

## How to invoke a command

User says one of:
- "run audit"
- "follow commands/audit.md"
- "audit"

The AI reads the command file, switches to the required mode, executes the steps.

## Master vs sub-commands

- `run.md` is the master — figures out what to do based on state
- Sub-commands are explicit — user knows what they want

For beginners: prefer `run`. For power users: invoke sub-commands directly.

## Adding project-specific commands

Project-specific commands (e.g., `scan-rust-bugs.md`, `deploy-staging.md`) go in the project's own `commands/` folder if it has one, OR you can add them here and version them with the architecture.

For commands that should be GENERIC across all projects: propose via ADR and add to this folder.

## Mode discipline

Every command declares its required mode at the top. The AI switches to that mode when starting the command, switches back to default when done.
