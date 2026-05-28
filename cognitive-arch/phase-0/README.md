# phase-0 — onboarding templates

BRIEF: Templates filled during the project's first session (BOOTSTRAP). After Phase 0 is complete, the project moves to Phase 1.

## What lives here

| File | Purpose |
|------|---------|
| `00-project-overview.md` | Expanded project description (beyond PROJECT.md) |
| `01-stack-and-tools.md` | Stack details, environment setup, tools |
| `02-domain-overview.md` | Gateway to `design/` folder; high-level domain |
| `03-roadmap-draft.md` | Envisioned phases (high-level outline) |
| `discovery/` | Placeholder for product-discovery work (filled by separate "discovery AI" if used) |

## How it's filled

Run BOOTSTRAP.md interactive flow. The AI walks the user through filling these files one section at a time.

After Phase 0:
- PROJECT.md is filled (the headline identity)
- These 4 files have substance (the elaboration)
- `phases/phase-1.md` is generated
- STATE.md flips from `bootstrap` to `active`

## Status

`status:bootstrap` in STATE.md → Phase 0 incomplete; run BOOTSTRAP
`status:active` → Phase 0 complete; proceed to Phase 1+

## Discovery subfolder

`discovery/` is for the PRE-project work — what problem, who for, why this stack. It's a placeholder in v1; another AI (or a separate session) can fill it before the main project starts. The cognitive architecture doesn't FORCE discovery; it ALLOWS it.
