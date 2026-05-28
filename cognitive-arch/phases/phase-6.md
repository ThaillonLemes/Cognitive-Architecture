---
id: phase-6
status: complete
version: v2.0
prev_phase: phase-5
exit_criteria_count: 12
blocks_count: 13
estimated_duration_days: 5
created_at: 2026-05-22
last_updated: 2026-05-22
completed_at: 2026-05-22
owner: implementer
---

# Phase 6 — Retrofit Readiness (v2.0)

BRIEF: Fix stale files left by Phases 1–5, update RETROFIT.md and BOOTSTRAP.md for the two-tier Governor v2, create stack addenda for three common stacks, and produce a clean onboarding README. After this phase the architecture is adoptable by any new project.

## 1. Purpose

Phase 5 completed the Governor v2 Python SDK and left nine new modules working, but created technical debt: several meta-files still point at Phase 5 or earlier state, a routing bug in `governor.py` sends `--mode manual` to mock dispatch, the RETROFIT and BOOTSTRAP onboarding flows make no mention of the SDK tier, and there are no stack-specific addenda to help adopters in concrete ecosystems (Python/FastAPI, React/Next.js, Node/Express). This phase eliminates that debt and makes the architecture ready to be transplanted into other projects via the retrofit or bootstrap flows.

## 2. Goals

- All stale governance and meta files (`governor-state.md`, `PROJECT.md`, `STATE.md`, `NEXT.md`) reflect current reality
- `sdk/governor.py --mode manual` routes to the manual path (not mock); bug eliminated
- Retroactive phase docs and retrospective exist for Phase 1 and Phase 5
- `RETROFIT.md` and `BOOTSTRAP.md` document the two-tier Governor (manual + SDK) and the `governor_mode` flag
- Three stack addenda exist under `protocols/stack-addenda/` covering Python/FastAPI, React/Next.js, Node/Express
- Root `README.md` updated to reflect Governor v2 capabilities for new adopters
- `audit.sh` exits 0 throughout

## 3. Invariants

- `governor_mode: manual` path must remain fully functional after every block — no block may break manual operation
- `audit.sh` exit code remains 0 after every block close
- No existing protocol or template files deleted or renamed
- SDK code stays exclusively in `sdk/` — no new Python files elsewhere

## 4. Dependencies

- Phase 5 complete ✅ — all 9 blocks done (block-029 through block-037), all exit criteria met
- `sdk/governor.py` exists and `--mode mock --dry-run` works ✅
- `design/governor-v2.md` complete with all 7 open questions resolved ✅
- `governance/governor-state.md` exists (will be cleaned up in block-038)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| governor.py manual-mode fix breaks mock or sdk paths | Med | block-039 gate: run dry-run with all three modes; each must exit 0 |
| RETROFIT.md update creates pointer inconsistency | Low | block-045 reads current RETROFIT.md fully before editing; audit.sh gate at close |
| Stack addenda become opinionated / stale quickly | Low | Mark each addendum with `as_of:` date; scope to conventions only, not library versions |
| phase-1.md retroactive reconstruction is imprecise | Low | Acceptable — mark explicitly as "retroactive reconstruction" in BRIEF |

## 6. Validation

- **Manual inspection:** all state files have no stale Phase 5 data after block-038
- **Script gate:** `python sdk/governor.py --mode manual --dry-run` passes after block-039
- **File-existence checks:** all new files created (phase-1.md, phase-5-retro.md, stack addenda, README) exist
- **Pointer integrity:** `audit.sh` exits 0 after each block and after all 13 blocks

## 7. Exit Criteria

1. `governance/governor-state.md` contains a clean idle state (no stale `dispatched:` or Phase 5 data)
2. `python sdk/governor.py --mode manual --dry-run` exits 0 and output does NOT contain "mock dispatch"
3. `PROJECT.md` frontmatter `current_phase` is `Phase 6` and `last_updated` is 2026-05-22 or later
4. `phases/phase-1.md` exists with all 6 REQUIRED sections (§1 §2 §4 §7 §8 §10) filled (no placeholders)
5. `phases/phase-5-retro.md` exists with complete retrospective (summary, wins, pain points, lessons, metrics)
6. Roadmap doc (`phase-0/03-roadmap-draft.md`) updated: Phases 1–5 marked complete, Phases 6–7 marked planned
7. `INDEX.md` contains brief entries for all 7 `sdk/` modules (`governor.py`, `convention_snippet.py`, `task_packet.py`, `return_validator.py`, `dispatch.py`, `integration.py`, `config.py`) and all Phase 6 new files
8. `RETROFIT.md` contains a section documenting `governor_mode` selection (manual vs sdk) and SDK installation step
9. `BOOTSTRAP.md` Phase 0 or equivalent section documents Governor v2 SDK installation and `governor_mode` flag
10. `protocols/stack-addenda/` directory contains exactly 3 files: `python-fastapi.md`, `react-nextjs.md`, `node-express.md`
11. Root `README.md` updated: ≤ 130 lines, covers what-it-is, quick-start, and Governor v2 capabilities
12. `audit.sh` exits 0 with no warnings after all 13 blocks are closed

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-038 | Reset governor-state.md to idle | S | planned | `manifests/block-038-governor-state-reset.md` |
| block-039 | Fix manual-mode routing bug in governor.py | S | planned | `manifests/block-039-manual-mode-fix.md` |
| block-040 | PROJECT.md freshness update | S | planned | `manifests/block-040-project-md-update.md` |
| block-041 | Create phases/phase-1.md (retroactive) | S | planned | `manifests/block-041-phase-1-doc.md` |
| block-042 | Create phases/phase-5-retro.md | S | planned | `manifests/block-042-phase-5-retro.md` |
| block-043 | Update roadmap to reflect phases 1–7 | S | planned | `manifests/block-043-roadmap-update.md` |
| block-044 | Sweep INDEX.md for SDK + Phase 6 entries | S | planned | `manifests/block-044-index-sweep.md` |
| block-045 | RETROFIT.md: add Governor v2 two-tier section | M | planned | `manifests/block-045-retrofit-v2.md` |
| block-046 | BOOTSTRAP.md: add SDK install + governor_mode | M | planned | `manifests/block-046-bootstrap-v2.md` |
| block-047 | Stack addendum: Python / FastAPI | S | planned | `manifests/block-047-stack-python-fastapi.md` |
| block-048 | Stack addendum: React / Next.js | S | planned | `manifests/block-048-stack-react-nextjs.md` |
| block-049 | Stack addendum: Node / Express | S | planned | `manifests/block-049-stack-node-express.md` |
| block-050 | Update README.md for new adopters (v2.0) | M | planned | `manifests/block-050-readme-update.md` |

## 9. Dependency Graph & Parallel Execution Plan

Sequential execution chosen (single implementer agent, no parallelism).

```yaml
parallel_execution_plan:
  total_blocks: 13
  recommended_agents: 1
  execution_mode: sequential
  groups:
    - id: 6A
      blocks: [block-038, block-039, block-040]
      type: sequential
      depends_on: []
      note: "State cleanup and bug fix — must be done first"
    - id: 6B
      blocks: [block-041, block-042, block-043]
      type: sequential
      depends_on: [6A]
      note: "Missing doc creation — retroactive phase docs and roadmap"
    - id: 6C
      blocks: [block-044]
      type: sequential
      depends_on: [6B]
      note: "INDEX.md sweep — needs new files from 6B to exist first"
    - id: 6D
      blocks: [block-045, block-046]
      type: sequential
      depends_on: [6C]
      note: "Onboarding flow updates"
    - id: 6E
      blocks: [block-047, block-048, block-049]
      type: sequential
      depends_on: [6D]
      note: "Stack addenda — logically parallel but run sequentially per user choice"
    - id: 6F
      blocks: [block-050]
      type: sequential
      depends_on: [6E]
      note: "README synthesis — reads all Phase 6 outputs"
```

## 10. Out of Scope

- Async/parallel SDK dispatch (deferred to Phase 7)
- File content passing to sub-agents (deferred to Phase 7)
- `pytest` test suite for SDK modules (deferred to Phase 7)
- `audit.sh` checks 5–8 implementation (deferred to Phase 7)
- Token metrics / cost dashboard (deferred to Phase 7)
- Additional stack addenda beyond the three named (Python/FastAPI, React/Next.js, Node/Express)
- Multi-repo support (deferred to v3.0+)
- Windows `audit.ps1` equivalent (deferred — was Phase 2 scope, remains open)

---

End of phase-6.md.
