# blocks — block retrospectives + BLOCK_LOG

BRIEF: One retrospective file per block + the append-only BLOCK_LOG.md history.

## What lives here

| Path | Purpose |
|------|---------|
| `BLOCK_LOG.md` | Append-only block history (one line per block close + integration) |
| `block-<NNN>-<slug>.md` | Block retrospective (per `templates/block-retrospective.md`) |

## BLOCK_LOG format

One line per event. Each line is:

```
<block-id> <event> <commit-hash> <timestamp>
```

Events:
- `done` — block closed by implementer (gates passed)
- `integrated` — block merged to main by Governor
- `forced` — gate failed but user overrode
- `reverted` — rolled back after integration

Example:
```
block-001 done 3fbc1a3 2026-05-19T14:22Z
block-001 integrated abc1234 2026-05-19T14:45Z
block-002 done 9def567 2026-05-19T15:10Z
```

This file is NEVER edited (only appended). Audit verifies append-only.

## Retrospective format

See `templates/block-retrospective.md`. Each block has its own file.

## Naming

`block-<NNN>-<slug>.md` (matches the manifest slug exactly).

## Pointers

- Block retrospective `manifest:` field → must reference the (possibly archived) manifest
- `commands/block-close.md` step 5 writes the retrospective
- `commands/integrate.md` does NOT touch the retrospective (it's the implementer's job)
