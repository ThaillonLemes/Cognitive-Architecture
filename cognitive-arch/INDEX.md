# INDEX — navigation map

BRIEF: Folder-level map. Per-file briefs in `CATALOG.md` (cold). Partial-read large files: `Read(file, limit:30)` — see `protocols/file-reading-protocol.md`.

## HOT (every session start)

| File | Brief |
|------|-------|
| CLAUDE.md | AI entry point; reading order; flow pointers |
| PROTOCOLS.md | 24 axioms (P/Q/C/S) + Charter; S1-S5 security axioms |
| STATE.md | Current project state — AI-only, dense |
| NEXT.md | Pointer to next work — AI-only, dense |
| INDEX.md | This navigation map |
| board.md | Multi-agent status dashboard — AI-only |

## WARM (read when relevant — folders; per-file briefs in CATALOG.md)

| Path | Brief |
|------|-------|
| PROJECT.md | Project identity (name, type, stack) |
| BOOTSTRAP.md | Interactive first-session flow (NEW projects); v2.0 |
| RETROFIT.md | First-session flow for EXISTING projects; v2.0 |
| phase-0/ | Phase 0 onboarding templates |
| design/ | Domain logic + design docs (governor-v2, arch-v3) |
| phases/ | Phase roadmap docs + retros (per-phase briefs → CATALOG.md) |
| sdk/ | Governor v2 Python package + all SDK tools (per-file briefs → CATALOG.md) |
| protocols/stack-addenda/ | Stack-specific convention overlays (Python/FastAPI, React, Node) |
| manifests/ | Block manifests (created per block) |
| blocks/ | Block retrospectives + BLOCK_LOG.md |
| agents/ | AGENT.md per active agent |
| governance/ | Governor state, audit/health reports, patterns, proposals |
| _future/ | Deferred designs (e.g. token-based-modes) |
| _syntax.md | Vocabulary for AI-only files — read on-demand when writing STATE/NEXT/board (not a boot read) |

## COLD (templates, protocols, commands — large)

| Folder | Brief |
|--------|-------|
| templates/ | File templates (phase, manifest, retrospective, AGENT, ADR) |
| templates/agent-roles/ | Pre-built agent role templates |
| protocols/ | Generation rules + behavior protocols |
| commands/ | Operational commands for the AI to follow |
| decisions/ | ADRs (Architectural Decision Records) |
| _brainstorm/ | Scratchpad for questionnaires |

---

**Full per-file catalog** (every sdk/protocol/command/phase file + briefs) → `CATALOG.md`
