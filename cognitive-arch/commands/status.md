# Command: status

Mode required: checklist (presentation, but data-driven)

BRIEF: Output a human-readable status report from STATE.md, NEXT.md, board.md, and recent BLOCK_LOG entries.

## Usage

- Manual: "status" or "follow commands/status.md"
- After major events (block close, integration)

## What to read

1. STATE.md
2. NEXT.md
3. board.md
4. BLOCK_LOG.md (last 10 entries)
5. Current phase doc (if exists)

## Output format

```
=== PROJECT STATUS ===

Project: <name from PROJECT.md>
Phase: <current phase> (<phase status>)
Last integrated block: <id> at <ts>
Next planned block: <id>

=== AGENTS ===

| Agent | Block | Status | Lock | Updated |
|-------|-------|--------|------|---------|
| (rows from board.md)

=== RECENT BLOCKS ===

(last 5 entries from BLOCK_LOG.md)

=== ATTENTION ===

(any items requiring user attention:
- Failed gates not yet resolved
- Stale locks
- Pending Governor reviews
- Pending integration
)

=== NEXT ACTION ===

(suggested next action — read NEXT.md and infer)
```

## When to use

- After `/clear` to remind yourself where things stand
- Daily / per-session check-in
- Before deciding which command to run

## Cost

~500 tokens (mostly read).

End of status command.
