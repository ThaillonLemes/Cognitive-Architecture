# decisions — Architectural Decision Records (ADRs)

BRIEF: One file per significant decision. Numbered sequentially. The code/docs reference the ADR ID; the ADR carries the rationale.

## What lives here

- `ADR-<NNN>-<slug>.md` — one decision per file

## Naming

`ADR-<NNN>-<slug>.md`

Where:
- `<NNN>` is sequential (001, 002, ..., 042)
- `<slug>` is kebab-case descriptor

Examples:
- `ADR-001-choose-postgres-over-mysql.md`
- `ADR-014-flag-naming-convention.md`
- `ADR-042-deprecate-legacy-auth.md`

## When to create an ADR

When a decision is:
- **Non-obvious** — future readers will wonder "why this way?"
- **Hard to reverse** — significant cost to change later
- **Cross-cutting** — affects multiple files / phases / modules
- **Disputed** — multiple alternatives existed with real trade-offs

DON'T create an ADR for:
- Style choices that the linter enforces
- Tiny decisions visible from the code itself
- Decisions explicit in a manifest or phase doc

## ADR lifecycle

```
proposed → accepted → (superseded by ADR-<NNN>)
            ↓
         rejected (never accepted)
```

## Template

See `templates/ADR.md`.

## How code/docs reference an ADR

In code:
```rust
// PURPOSE: Auth middleware (see ADR-014)
```

In docs:
```markdown
We chose Postgres over MySQL per [ADR-001](decisions/ADR-001-choose-postgres-over-mysql.md).
```

In manifests:
```yaml
# axiom_override: "P-5 — see ADR-023"
```

## Status changes

- New ADR starts `proposed`
- After deciders agree: `accepted` (timestamp filled)
- If later replaced: `superseded` (link to new ADR)
- Old ADRs stay in the folder — they're history
