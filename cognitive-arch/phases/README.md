# phases — phase roadmap docs

BRIEF: One file per phase. Created at phase-start, finalized at phase-close. Optional `phase-<N>-retro.md` written at phase close.

## What lives here

| File | Purpose |
|------|---------|
| `phase-<N>.md` | Phase roadmap (planned → active → complete) |
| `phase-<N>-retro.md` | Phase retrospective (written at phase close) |
| `MASTER.md` | OPTIONAL — cross-phase plan if project has >5 phases |

## Lifecycle

1. **planned:** declared in `phase-0/03-roadmap-draft.md` outline
2. **active:** phase doc exists; blocks in progress
3. **complete:** all blocks integrated; exit criteria met; retro written

## Generation

Use `templates/phase.md` + `protocols/phase-generation.md`.

## Naming

- `phase-1.md`, `phase-2.md`, ... — sequential
- `phase-1-retro.md`, `phase-2-retro.md`, ... — match number

## Status tracking

Phase status lives in:
- Phase doc YAML frontmatter (canonical)
- STATE.md `p:` field (current phase only)
- INDEX.md brief

These three must agree.
