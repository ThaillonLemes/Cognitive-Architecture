# protocols — generation rules and behavior protocols

BRIEF: Rules for HOW the AI generates files and behaves in specific contexts. Read the relevant protocol BEFORE performing the action it describes.

## Files in this folder

| File | What |
|------|------|
| `modes.md` | guidance / guardrails / checklist mode definitions |
| `phase-generation.md` | how to generate a phase doc |
| `manifest-small-generation.md` | how to generate a Tier S manifest |
| `manifest-medium-generation.md` | how to generate a Tier M manifest |
| `manifest-large-generation.md` | how to generate a Tier L manifest |
| `block-retrospective-generation.md` | how to write a block retrospective |
| `phase-retrospective-generation.md` | how to write a phase retrospective |
| `block-close-checklist.md` | exact 8-step protocol at block close |
| `file-reading-protocol.md` | when and how to use partial reads |
| `code-header-protocol.md` | mandatory header on every code file |
| `pointer-integrity.md` | audit rule for cross-file references |
| `parallelism.md` | identifying and coordinating parallel blocks |
| `agents.md` | agent lifecycle, naming, spawn workflow |
| `brainstorm-pattern.md` | large-questionnaire pattern for design docs |

## When to read

| Action | Protocol to read first |
|--------|------------------------|
| Generating a phase doc | `phase-generation.md` |
| Generating a block manifest | `manifest-{small,medium,large}-generation.md` |
| Closing a block | `block-close-checklist.md` |
| Writing a retrospective | `block-retrospective-generation.md` or `phase-retrospective-generation.md` |
| Spawning agents | `agents.md` + `parallelism.md` |
| Reading lots of files | `file-reading-protocol.md` |
| Creating/modifying code file | `code-header-protocol.md` |
| Running audit | `pointer-integrity.md` |
| Filling a design doc with many decisions | `brainstorm-pattern.md` |
| Switching agent behavior | `modes.md` |

## Conventions

- Each protocol declares its required mode at the top
- Protocols are stable (don't update except via ADR)
- Project-specific protocol additions go in project's `design/` folder, not here

## How protocols are applied

Protocols are READ, not executed. The AI reads the protocol, understands the rules, then applies them when generating files or behaving. The Governor or audit.sh validates that the OUTPUTS of protocol-following match expectations.
