# Command: run (master)

Mode required: depends on sub-command (see below)

BRIEF: Master command that orchestrates other commands. Designed for less-experienced users who want one entry point.

## Usage

User says: "run" or "follow commands/run.md"

## What it does

The AI reads STATE.md and board.md to determine current context, then executes the appropriate sub-command(s). It tries to do "the right next thing" automatically.

## Decision tree

```
read STATE.md, board.md, NEXT.md
↓
if STATE.md status = bootstrap:
  → follow BOOTSTRAP.md
↓
elif there's an in-progress block in board.md for THIS agent:
  → follow commands/block-close.md (close it)
↓
elif NEXT.md points to a manifest:
  → follow commands/block-start.md
↓
elif phase status = complete in STATE.md and no next phase planned:
  → follow commands/phase-close.md
↓
elif governor role active and board.md has done+ready agents:
  → follow commands/integrate.md
↓
else:
  → run commands/status.md (show user where things stand)
```

## When to use master vs sub-commands

- **Master (this command):** when user is less familiar with the architecture; wants the AI to figure out next step
- **Sub-commands directly:** when user knows exactly what they want; wants explicit control

## Cost

Master command reads more files to figure out context. Slightly higher token cost (~2K) vs directly invoking a sub-command (~500). Worth it when user doesn't want to think.

## Sub-commands invoked

- `commands/block-start.md`
- `commands/block-close.md`
- `commands/phase-start.md`
- `commands/phase-close.md`
- `commands/integrate.md`
- `commands/audit.md`
- `commands/status.md`
- `BOOTSTRAP.md`

## Output

Whatever the invoked sub-command outputs. Always announce: "Detected state X. Running command Y."

End of run command.
