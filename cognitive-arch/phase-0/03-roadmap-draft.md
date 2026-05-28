## 03 — Roadmap draft

BRIEF: Envisioned version roadmap for the cognitive architecture. Each version is a phase. High-level only — each phase doc fleshes out scope when generated.

## Phase / version outline

_Last updated: 2026-05-22 (Phase 6 active). Status column reflects actual outcomes, not predictions._

| Phase | Version | Theme (actual) | Blocks | Duration (actual) | Status |
|-------|---------|----------------|--------|-------------------|--------|
| 1 | v1.1 | Consistency — axiom count, CLAUDE.md budget, Charter naming, audit parity, step counts, `_syntax.md` | 6 | 1 day | ✅ complete |
| 2 | v1.2 | Token metering — HOT file token estimates, `/token-audit` command, retrospective token fields | 4 | 1 day | ✅ complete |
| 3 | v1.3 | Schema validation — Tier S/M/L manifest schemas, `validate-manifest` command, pointer-integrity phase 2 | 6 | 1 day | ✅ complete |
| 4 | v1.4 | Governor v2 design — master spec, 6 protocols, 2 templates, 13 decisions, 7 open questions | 12 | 1 day | ✅ complete |
| 5 | v2.0 | Governor v2 Python SDK — 7 modules, mock client, crash recovery, all 7 open questions resolved | 9 | 1 day | ✅ complete |
| 6 | v2.0 | Retrofit Readiness — bug fixes, RETROFIT/BOOTSTRAP v2.0, stack addenda (Python/FastAPI, React, Node) | 13 | 1 day | 🔄 active (block-043/050) |
| 7 | v2.1 | SDK Depth — async parallel dispatch, file I/O in packets, pytest suite, audit.sh checks 5–8, token metrics | ~10 | TBD | 📋 planned |
| … | v3.0+ | Multi-repo (activate `_future/multi-repo.md`); domain-specific arch flavors; public OSS registry | open | open | 💭 future |

_Note: Phases 2–5 themes diverged significantly from original predictions (see below). The project prioritised Governor v2 spec + implementation over Windows portability and metrics — a better sequencing given that governance is the highest-leverage lever for AI-assisted projects._

## Phase 1 detail (v1.1 — Consistency)

Focus: low-risk, high-confidence improvements that eliminate inconsistencies discovered while reading v1 end-to-end. Each improvement should be ≤ Tier M (or Tier S where possible). Sample candidate blocks:

- **block-001 — Fix axiom-count inconsistency.** PROTOCOLS.md BRIEF says "19 axioms" but `INDEX.md` says "14 axioms". Pick one source of truth and align. (Tier S, doc-only.)
- **block-002 — Bring CLAUDE.md within Q2 budget.** Currently 108 lines vs 60-line budget. Refactor: move trigger-phrase tables and detection logic to a sub-protocol; keep CLAUDE.md as the slim entry only. (Tier S, refactor.)
- **block-003 — Disambiguate Charter vs Comment Charter naming.** CLAUDE.md + INDEX.md call it "Comment Charter"; PROTOCOLS.md just "Charter". ADR + rename. (Tier S.)
- **block-004 — Audit.sh ↔ audit-protocol parity check.** `audit.sh` implements 5 checks; `commands/audit.md` declares 8. Either extend script OR clarify which are script vs Governor-only. (Tier M.)
- **block-005 — Step-count audit pass.** Survey all references to numbered protocols (8-step block-close, 9-step retrofit, etc.) for consistent counts across files. (Tier S, doc-only.)
- **block-006 — `_syntax.md` completeness sweep.** Some keys appear in examples but not in the canonical alphabetical list. Reconcile. (Tier S.)

Estimated blocks: 5–8. Parallelism possible (doc edits to different files are disjoint). Recommended agents: 1–2.

## Phase 2 detail (v1.2 — Portability)

Focus: Make the architecture usable on Windows without WSL. Likely blocks:
- PowerShell port of `audit.sh` (`audit.ps1`) with byte-for-byte equivalent behavior.
- README install instructions per-OS.
- CI sample (Github Actions) running both scripts.

## Long-term direction

- **v1.x** — polish, portability, audit depth, metrics, coverage.
- **v2.x** — multi-agent maturation; opt-in always-on Governor; brainstorm-driven redesigns of pain points.
- **v3.x** — multi-repo and stack-specific flavors; possibly a public registry of reusable design docs.

## Milestones

| Milestone | Phase | Description | Status |
|-----------|-------|-------------|--------|
| v1.1 | Phase 1 | All v1 inconsistencies resolved; audit clean | ✅ 2026-05-20 |
| v1.2 | Phase 2 | Token estimates visible; retrospectives track cost | ✅ 2026-05-21 |
| v1.3 | Phase 3 | Manifest schema validation; pointer-integrity phase 2 | ✅ 2026-05-21 |
| v1.4 | Phase 4 | Governor v2 fully specified; 13 decisions locked | ✅ 2026-05-21 |
| v2.0 | Phase 5 | Governor v2 SDK working; mock E2E passes | ✅ 2026-05-22 |
| v2.0 (hardened) | Phase 6 | Retrofit-ready; 3 stack addenda; RETROFIT/BOOTSTRAP updated | 🔄 in progress |
| v2.1 | Phase 7 | Async dispatch; pytest; audit checks 5–8; token metrics | 📋 planned |
| v3.0 | Phase 8+ | Multi-repo; public registry | 💭 future |

## Sequencing notes

- v1.1 (consistency) MUST precede v1.4 (metrics) — you can't measure a moving target.
- v1.2 (portability) before v1.5 (coverage) — otherwise stack addenda assume an environment the user can't run.
- v1.3 (audit depth) and v1.4 (metrics) can run in parallel if separate authors / sessions.
- v2.0 (multi-agent maturation) depends on v1.x being trustworthy — do not activate governor-loop until v1.x audit is rock-solid.

## How this evolves

This is a DRAFT. Every phase-close retrospective updates this roadmap with what we learned. The shape after v1.5 is intentionally less specified — we let evidence from earlier phases shape the later ones.

(proposed by the AI — confirm. The exact version sequence and the parallelization choices are recommendations; user should validate before phase-1 starts.)
