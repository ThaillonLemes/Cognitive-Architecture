# manifests — block manifests

BRIEF: One file per block. Contract for the block (files touched, gates, deps, validation). Created at block-start; archived to `_archive/` after integration.

## What lives here

| Path | Purpose |
|------|---------|
| `block-<NNN>-<slug>.md` | Active manifest (planned, pending, wip, done) |
| `_archive/block-<NNN>-<slug>.md` | Integrated manifest (moved here by `commands/integrate.md`) |

## Naming

`block-<NNN>-<slug>.md`

Where:
- `<NNN>` is the sequential block number (zero-padded to 3 digits min)
- `<slug>` is a short kebab-case description

Examples: `block-001-bootstrap-project.md`, `block-094-server-auth-movement.md`

## Lifecycle

```
planned → pending → wip → done → integrated → (archived)
```

- **planned:** declared in phase doc, no manifest yet
- **pending:** manifest written, work not started
- **wip:** work in progress (an agent has lock:in-progress in board.md)
- **done:** all gates passed; ready for integration
- **forced:** gate failed but user overrode; flag preserved
- **failed:** gate failed; awaiting user decision (rare — most halt before this)
- **integrated:** merged to main by Governor
- **reverted:** rolled back after integration (rare)

## Tier

Each manifest declares its tier:
- **S (small):** investigation, doc-only, ≤2 files modify, no abstraction
- **M (medium):** default implementation, 3-8 files
- **L (large):** cross-repo, gate, activation criteria, rollout

See `templates/manifest-{small,medium,large}.md` and matching protocols in `protocols/`.

## Generation

Use `templates/manifest-{small,medium,large}.md` + `protocols/manifest-{small,medium,large}-generation.md`.

## Validation

`audit.sh` validates:
- YAML frontmatter parseable
- Required fields per tier present
- `files.read/modify/create` paths resolve (or marked planned)
- `dependencies:` block IDs exist
