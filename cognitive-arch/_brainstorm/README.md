# _brainstorm — scratchpad for questionnaires and drafts

BRIEF: Working artifacts. Not part of the canonical project state. Used during design exploration via `protocols/brainstorm-pattern.md`.

## What lives here

| Path | Purpose |
|------|---------|
| `<topic>-questionnaire.md` | Large questionnaire for design exploration |
| `<topic>-draft.md` | Working draft of a design doc before it goes to `design/` |
| `<topic>-notes.md` | Loose notes / iteration logs |

## Naming

Use descriptive lowercase-with-hyphens. Examples:
- `combat-questionnaire.md`
- `pricing-tiers-questionnaire.md`
- `auth-flow-draft.md`

## Underscore prefix

The `_brainstorm/` folder uses underscore prefix to:
- Sort below main folders alphabetically
- Visually indicate "scratch / WIP"
- Audit may treat differently (less strict validation)

## Lifecycle

1. **Create:** when starting a brainstorm or draft
2. **Iterate:** add content over multiple sessions
3. **Synthesize:** when ready, move/copy synthesis to `design/<topic>.md`
4. **Retain or delete:**
   - Retain if useful for audit trail
   - Delete if synthesis captures everything important

## Audit behavior

Audit does NOT validate `_brainstorm/` content strictly. It's allowed to be:
- Long
- Non-canonical
- Question-heavy
- Half-finished

This is the play space.

## Pointers

Designs in `design/` may reference brainstorm files for audit trail:
```markdown
Source: [_brainstorm/combat-questionnaire.md] (2026-05-19 session)
```

But `design/` files should be SELF-CONTAINED — readers shouldn't NEED to go to `_brainstorm/` to understand.
