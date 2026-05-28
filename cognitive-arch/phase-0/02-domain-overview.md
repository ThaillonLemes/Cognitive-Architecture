## 02 — Domain overview

BRIEF: The "domain" of this meta-project IS the cognitive architecture itself. Entities, flows, and rules below describe the v1 scaffold; future phases evolve them.

## Core entities

| Entity | Description | Source of truth |
|--------|-------------|-----------------|
| **HOT file** | A markdown file read by the AI at every session start (CLAUDE, PROTOCOLS, STATE, NEXT, INDEX, board, _syntax, PROJECT). Size-budgeted. | `INDEX.md` HOT section |
| **WARM file** | A markdown file read when relevant (BOOTSTRAP, RETROFIT, PROJECT, phase-0/, design/, phases/, manifests/, blocks/, agents/, governance/). | `INDEX.md` WARM section |
| **COLD file** | A markdown file read on-demand (templates/, protocols/, commands/, decisions/, _brainstorm/, _future/). | `INDEX.md` COLD section |
| **Axiom** | Universal rule. Categorized P (principles), Q (quality, testable), C (charter, doc rules). 19 total in v1. | `PROTOCOLS.md` |
| **Phase** | A coherent chunk of project work with an exit criterion. | `templates/phase.md`, `protocols/phase-generation.md` |
| **Block** | A single unit of work. Has a manifest (contract), implementation, gates, retrospective. | `manifests/`, `blocks/` |
| **Manifest** | The contract for a block. Tier S / M / L based on size and risk. | `templates/manifest-{S,M,L}.md` |
| **Gate** | An evidence-producing check a block must pass to close (tests-pass, lint-pass, build-pass, files-updated, dependencies-met, plus custom). | manifest `gates:` field |
| **Retrospective** | Facts-only record of what was built, written at block close or phase close. | `templates/{block,phase}-retrospective.md` |
| **Agent role** | A behavioral profile: implementer, governor, reviewer, doc-keeper. Identity persisted in `AGENT.md`. | `templates/agent-roles/`, `templates/AGENT.md` |
| **Mode** | Behavioral state: guidance (conversational) / guardrails (drift-check) / checklist (strict yes/no). Triggered by file/command being followed. | `protocols/modes.md` |
| **ADR** | Architectural Decision Record. One per non-obvious decision. | `decisions/`, `templates/ADR.md` |
| **Audit** | Validation pass over the architecture (existence, sizes, pointers, format, schema, deps, conflicts, drift). | `audit.sh`, `commands/audit.md` |

## Core flows

1. **Bootstrap (new project).** User drops `cognitive-arch/` → says "oi" → AI reads `BOOTSTRAP.md` → interactive Phase 0 → fills PROJECT.md, phase-0/* → generates `phases/phase-1.md` → STATE flips to `active`. Detail: `BOOTSTRAP.md`.
2. **Retrofit (existing project).** Same drop, but AI reads `RETROFIT.md` → inspects existing code (read-only) → asks code-can't-tell questions → fills PROJECT/phase-0 with `(inferred — confirm)` markers. Detail: `RETROFIT.md`.
3. **Block lifecycle.** `planned` → manifest written → `pending` → agent starts (`wip`, `lock:in-progress`) → implementation → `commands/block-close.md` (8-step) → `done` → Governor integrates → `integrated` → manifest archived.
4. **Phase lifecycle.** `planned` (in roadmap-draft) → `active` (phase doc generated, blocks in progress) → `complete` (all blocks integrated, exit criteria met, retro written).
5. **Multi-agent flow.** Phase doc identifies parallel groups → Governor (or user) spawns AGENT.md per group → worktrees per agent → blocks run in parallel → Governor integrates atomically at sync points. Detail: `protocols/parallelism.md` + `protocols/agents.md`.
6. **Audit cycle.** Manual trigger OR auto-trigger (every 30 blocks, every phase close) → `audit.sh` runs structural checks → Governor extends with semantic checks → report written to `governance/`.
7. **Brainstorm pattern.** Large design questions → questionnaire generated in `_brainstorm/` → user responds in batch → synthesis written to `design/`. Detail: `protocols/brainstorm-pattern.md`.

## Key business rules

- **P3 — Single source of truth.** Each fact lives in exactly one file. Others point to it; they do not restate. Source: `PROTOCOLS.md`.
- **P4 — Pointer integrity.** Every cross-file reference must resolve. Broken pointers are audit errors. Source: `protocols/pointer-integrity.md`.
- **P5 — Slim boot.** HOT files small enough that boot cost stays low. Detail moves to WARM/COLD reached via `INDEX.md`. Source: `PROTOCOLS.md`.
- **Q1 — Rule of Three.** No shared abstraction on the first or second occurrence; evaluate on the third. Source: `PROTOCOLS.md`.
- **Q3 — Manifests precede work.** No work artifact exists before its manifest. Source: `PROTOCOLS.md`.
- **Q4 — Gates pass before commit.** Block does not close unless gates pass OR `forced_pass` flag is applied with rationale. Source: `PROTOCOLS.md`.
- **C5 — ADR for non-obvious decisions.** Architectural decisions go in `decisions/`. The code/doc references the ADR ID. Source: `PROTOCOLS.md`.
- **Axiom override protocol.** A block may override a single axiom with `axiom_override:` in manifest YAML. Accumulation > 5 in 30 days = drift signal.

## Domain vocabulary

| Term | Meaning in this project |
|------|------------------------|
| HOT / WARM / COLD | Reading frequency tier (every session / when relevant / on demand) |
| Tier S / M / L | Manifest size tier (small ≤2 files / medium 3–8 / large 8+ or cross-repo or gate) |
| Slim boot | Reading only HOT files at session start (target ~3K tokens) |
| AI-only file | File written in dense key:value vocab from `_syntax.md` (STATE, NEXT, board, AGENT, INDEX) |
| Charter | The C-axioms (documentation rules). Canonical name per `PROTOCOLS.md` line 47. See ADR-002. |
| Block close | The 8-step protocol at `protocols/block-close-checklist.md` |
| Forced pass | User-authorized override when a gate fails. Audit-logged. |
| Sync point | Moment when a parallel group's blocks all finish and Governor integrates them |
| Lock | Per-agent state in `board.md`: `in-progress` while working, `ready` when done |
| Drift signal | Pattern indicating the architecture is decaying (forced > 3 / month, overrides > 5 / month, stale locks, broken pointers) |

## Relationship to other systems

- **Git.** The architecture lives in git and assumes git for worktrees, branches, commits. Stack-agnostic for the project's own code but git-assumed for the meta-process. (Open question: handle non-git scenarios? Low priority — git is universal in target market.)
- **LLM client.** Reads files at session start; writes files during work. The architecture does not depend on a specific client's API.
- **Audit script ecosystem.** `audit.sh` is the v1 implementation; alternative shells / a Python equivalent could coexist.

## Pointers to design/

`design/` is empty at this Phase 0. Future design docs for the meta-project:
- `design/audit-script.md` (TBD — formal spec of all audit checks; portability strategy)
- `design/metrics-and-benchmarks.md` (TBD — how each version is measured against the last)
- `design/multi-llm-consistency.md` (TBD — how we test cross-LLM behavior)

## Open domain questions

- ~~Is "Comment Charter" the right name for C-axioms?~~ Resolved: canonical name is "Charter". See ADR-002 + block-003.
- Should `phase-0/discovery/` remain a placeholder, or be removed (since this is a meta-project and discovery is implicit)? (proposed by the AI — confirm)
- Do we need a `tier:XS` (extra small) for "single typo fix" work, or is Tier S already light enough? (Open — proposed by the AI for v1.x discussion)
- ~~How to formally count axioms (INDEX.md said "14")?~~ Resolved: 19 axioms (P1-6, Q1-7, C1-6). See block-001.
