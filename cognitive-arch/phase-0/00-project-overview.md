## 00 — Project overview

BRIEF: Expanded description of the Cognitive Architecture self-evolution meta-project. PROJECT.md has the identity card; this file adds context.

## What is this project?

The Cognitive Architecture is a markdown-only scaffold (`cognitive-arch/`) that AI agents and human developers share as a navigable workspace. v1 exists today: HOT files (CLAUDE.md, PROTOCOLS.md, STATE.md, NEXT.md, INDEX.md, board.md, _syntax.md, PROJECT.md), 13 protocols, 12 operational commands, 9 templates, 4 agent roles, 2 deferred patterns, and a lightweight bash audit script.

This meta-project's deliverable IS the architecture — not a separate codebase that uses it. We iterate v1 → v1.1 → v1.2 → … → v2 → v3 by improving measurable dimensions of the scaffold itself.

## What problem does it solve?

Existing AI-coding tools (Cursor, Claude Code, GitHub Copilot, agentic SDKs) focus on the **chat-loop layer**: tokenization, context windows, function calling, conversational UX. They do not address the **knowledge structure** the AI navigates inside a project. The result: every conversation rebuilds context from scratch, every multi-agent workflow drifts, every long project leaks consistency. This scaffold fills that gap with a predictable, auditable file system the AI reads in a known order and writes back to.

## What success looks like

- Each version measurably improves boot token cost, generation precision, audit cleanliness, or human-dev UX (see Phase-1 metrics).
- External users can drop `cognitive-arch/` into any project and get value in ≤ 5 minutes.
- Multi-LLM tests (Claude, GPT-4, Gemini) produce structurally equivalent outputs for the same protocol.
- The architecture survives its own evolution: every change to `cognitive-arch/` keeps `audit.sh` clean.
- The repo is open-source, forkable, and useful to someone other than the original author.

## What's in scope

- Iterating on every HOT file, protocol, command, template, agent role.
- Adding new protocols/commands/templates where v1 has gaps (security, perf, deploy, etc.).
- Strengthening `audit.sh` (more checks, Windows portability).
- Adding metrics + a baseline → trend tracking mechanism.
- Activating `_future/` patterns when they earn their cost.
- Documenting decisions in `decisions/` as we go.

## What's NOT in scope

- Building applications that *use* the architecture (those are separate projects).
- Replacing existing LLM clients or IDE plugins.
- Becoming a runtime / daemon / server (architecture stays markdown-only).
- Reinventing version control, build systems, or test runners (we sit on top of them, stack-agnostic).
- Productizing as a paid SaaS in v1-v3 (open source first).

## Constraints

- **Markdown-only.** No compiled artifacts. `audit.sh` is the sole executable script in v1.
- **Cross-platform.** Must be usable from Windows, macOS, Linux. (v1 has a portability gap — `audit.sh` is bash-only; address in early v1.x.)
- **Stack-agnostic.** No `package.json`, `Cargo.toml`, language compiler assumed. Project-using-the-arch can be any stack.
- **AI-readable + human-skimmable.** Density without opacity. BRIEFs at the top of large files.
- **No dependency creep.** Architecture must not pull in npm/pip/cargo packages.

## Risks (project-level)

- **Bikeshedding.** The architecture is the product; everything looks like a candidate for refactor. Mitigation: gate every change with a metric improvement OR an ADR + retrospective.
- **Drift from real use.** If we evolve the arch without using it on real projects, we miss real friction. Mitigation: the meta-project itself uses (some of) the arch; periodically test on a real side-project too.
- **Over-engineering for v2+ before v1 is solid.** Mitigation: `_future/` stays a parking lot; activation requires explicit ADR.
- **Single-author bias.** Mitigation: every change considers "would this confuse someone forking this?" — public-OSS perspective baked in (PROJECT.md constraint).

## Open questions to resolve in early phases

- How do we measure "AI generation precision" objectively, across multiple LLMs, without a runtime? (proposed pilot: deterministic prompt → generated file diff against gold standard)
- Is `audit.sh` the right form factor, or should it be a portable script (Python? Node? PowerShell+bash sibling)?
- Should the meta-project itself spawn agent roles (governor, reviewer) on its own architecture, or stay solo-driven until v2?
- What's the right tension between "use the arch on itself" (dogfood, slow) and "edit the arch directly" (fast, but loses the validation)?
