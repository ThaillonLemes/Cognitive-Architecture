# design — domain logic

BRIEF: Project-specific domain docs. YOU fill this over time. The AI reads these for context when implementing blocks that touch the domain.

## What goes here

Project-specific knowledge:
- Business rules
- Domain entities and relationships
- Algorithms and formulas
- Game design (for games)
- API contracts (for services)
- UX flows
- Pricing/billing logic
- Permissions and access models
- Domain-specific protocols

## What does NOT go here

- Code (lives in your project's source folder)
- Build/test configuration (PROJECT.md and `phase-0/01-stack-and-tools.md`)
- Project meta (PROJECT.md, `phase-0/00-project-overview.md`)
- Decisions (`decisions/` — though design docs can REFERENCE ADRs)
- Architecture diagrams (project's own `docs/` or `design/architecture.md` is fine)

## Naming

Use descriptive lowercase-with-hyphens:
- `combat-rules.md`
- `pricing-tiers.md`
- `auth-flow.md`
- `user-permissions.md`
- `api-contract.md`

## Structure of a design doc

Recommended structure for each doc:

```markdown
# <Topic>

BRIEF: <one-line summary of what this doc covers>

## Why this doc exists

<1-2 sentences>

## Vision (one paragraph)

<what does this system feel like / accomplish>

## Decisions made

<numbered list of decisions; reference ADRs where applicable>

## Mechanics / details

<the actual content>

## Open questions

<unresolved items; each becomes work later>

## Cross-system dependencies

<which other design docs this touches>

## Acceptance criteria (testable conditions)

<how we know this is implemented correctly>

## References / inspirations

<external links, prior art, citations>
```

## How docs evolve

- Start with skeleton (sections present, content TBD)
- Fill via `protocols/brainstorm-pattern.md` for large topics
- Iterate over the project's lifetime
- When a decision changes meaningfully, create an ADR

## Pointers to/from design

- Block manifests with domain implications cite `design/<doc>.md` in their `files.read`
- ADRs in `decisions/` reference the design doc that the decision affects
- INDEX.md catalogs design docs as they're added
