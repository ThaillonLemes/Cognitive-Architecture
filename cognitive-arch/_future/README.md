# _future — patterns deferred to later versions

BRIEF: Concepts and patterns we've designed but NOT included in v1. Documented here for when they become priority.

## What lives here

| File | Topic |
|------|-------|
| `governor-loop.md` | Adaptive Governor polling (always-on) |
| `multi-repo.md` | How to evolve to multi-repo structure |

## Why these are deferred

Each pattern in this folder has been considered for v1 but excluded because:
- Cost (token, complexity, build) exceeded benefit at v1 scope
- Pattern depends on infrastructure not yet available (Claude Agent SDK programmatic spawn, MCP integrations, etc.)
- Scope creep risk — v1 stays focused

## How to activate a pattern

When ready to adopt a deferred pattern:
1. Read its file in this folder
2. Decide if it's a clean drop-in OR requires version bump (v2)
3. Generate the necessary files in their proper homes (likely a new `protocols/*.md` or `commands/*.md`)
4. Move the file from `_future/` to its proper home
5. Update INDEX.md and CLAUDE.md if needed

## Add new patterns

If during v1 use you identify a desired pattern that's too big for v1:
- Write it as `_future/<pattern>.md`
- Reference it from where it would be activated (e.g., a comment in CLAUDE.md or a command)
- Mature the design over time before activation

## Underscore prefix

`_future/` uses underscore to:
- Sort below main folders
- Visually indicate "not yet active"
- Audit treats as non-canonical (less strict validation)
