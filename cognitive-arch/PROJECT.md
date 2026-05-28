---
name: "Cognitive Architecture — Self-Evolution"
type: "meta-project / framework"
stack:
  language: markdown
  framework: none
  build_cmd: "N/A"
  test_cmd: "bash audit.sh"
  lint_cmd: "N/A"
current_phase: "Phase 6 — Retrofit Readiness"
status: active
created_at: 2026-05-20
last_updated: 2026-05-22
---

# Project: Cognitive Architecture — Self-Evolution

BRIEF: identity card for this meta-project. The cognitive architecture in this repo is simultaneously the scaffold AND the object of work. We evolve it across versions (v1 → v1.1 → … → v2+).

## Vision (one paragraph)

Build, in public and over time, the best markdown-only cognitive scaffold for AI-assisted code projects. v1 already exists in `cognitive-arch/`; this project's product is the architecture itself. Each version raises measurable dimensions — token efficiency, generation precision, cross-LLM consistency, generic-ness across stacks, multi-agent coordination, audit robustness, human-developer UX, protocol completeness. The project dogfoods the architecture: where the meta-work fits cleanly into phases/blocks/manifests, we use them; where overhead exceeds value, we use lighter mechanisms (ADRs, brainstorms) and learn from the friction.

## Target users

- **Primary:** developers (solo + small teams) who use AI coding assistants (Claude Code, Cursor, GPT-based agents) and want a structured workspace the AI can navigate quickly.
- **Secondary:** AI agents themselves — every file in `cognitive-arch/` is read by an LLM at some point; the architecture is co-designed for both audiences.
- **Tertiary (eventual):** other framework authors / open-source contributors who fork or extend the scaffold.

## Key constraints

- **Markdown-only deliverables.** No runtime, no daemon, no compiled artifacts. The single executable artifact is `audit.sh` (and a Windows-portable equivalent is on the roadmap).
- **Stack-agnostic.** Must not assume language, framework, or build tool. Code-only conventions (e.g., code-header protocol) carry explicit `[code-only]` markers.
- **Slim boot.** HOT files read at every session start stay within Q2 budgets. Detail lives in WARM/COLD reachable via `INDEX.md`.
- **Multi-LLM friendly.** No reliance on Anthropic-only behaviors. Patterns should work with Claude, GPT-4, Gemini, local models.
- **Auditable.** Every change must keep `audit.sh` clean (or improve it). Drift is detected, not silently absorbed.
- **Public / open-source.** Every change is designed assuming a public repo. No private context, no internal pointers, no proprietary assumptions.

## Pointers

- `PROTOCOLS.md` — 19 axioms (P/Q/C) that govern every file and block
- `INDEX.md` — catalog of files with one-line briefs
- `sdk/` — Governor v2 Python package (Phases 5+); entry point `sdk/governor.py`
- `phases/phase-6.md` — current phase: Retrofit Readiness (blocks 038–050)
- `design/governor-v2.md` — Governor v2 architecture spec (all open questions resolved)
- `_future/` — patterns deferred to later versions (governor-loop, multi-repo)
- `phase-0/` — meta-project onboarding docs
- `decisions/` — ADRs for non-obvious design choices (empty so far)
- `_brainstorm/` — questionnaires and drafts (per `protocols/brainstorm-pattern.md`)

## Status transitions

- `bootstrap` — Phase 0 incomplete; PROJECT.md placeholders unfilled
- `active` — Phase 0 complete; project in improvement mode (current state)
- `complete` — N/A for this project (open-ended improvement; no terminal state planned)
