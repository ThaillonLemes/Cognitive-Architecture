---
id: phase-5
status: planned
version: v2.0
prev_phase: phase-4
exit_criteria_count: 9
blocks_count: 9
estimated_duration_days: 14
created_at: 2026-05-22
last_updated: 2026-05-22
owner: implementer
---

# Phase 5 — Governor v2: Python implementation (v2.0)

BRIEF: Implement the Governor v2 spec (Phase 4) as a Python package in `sdk/`. Nine blocks deliver every module — convention snippet, task packet, dispatch, integration, main loop — plus E2E validation and resolution of the 7 open questions from `design/governor-v2.md §11`. First code phase of the project.

## 1. Purpose

Phase 4 produced a complete specification for the SDK-based Governor v2. This phase turns that spec into working Python code. The deliverable is a `sdk/` package that a user can run with `python sdk/governor.py` to orchestrate blocks automatically: the Governor reads project state, assembles task packets, spawns Claude sub-agents via the Anthropic Python SDK, awaits return packages, validates them, integrates changes, and updates all state files. The manual fallback path (governor_mode: manual) remains unchanged and fully functional. All 7 open design questions deferred from Phase 4 are resolved during implementation and documented.

## 2. Goals

- `sdk/` Python package exists with all modules: convention snippet, task packet builder, return validator, dispatch, integration, config, and main Governor loop
- `python sdk/governor.py --dry-run` reads project state and prints the next block plan without dispatching any agent
- Governor runs E2E on a test manifest, produces valid task packets, and writes correct state file updates
- All 7 open questions from `design/governor-v2.md §11` answered and written back to the design doc
- Feature flag (`governor_mode: manual | sdk`) fully wired — switching to `manual` disables SDK dispatch gracefully
- `audit.sh` passes throughout (SDK layer is additive; no existing markdown files broken)
- Every Python file carries the mandatory code header per `protocols/code-header-protocol.md`

## 3. Invariants

- `governor_mode: manual` path must remain fully functional at every point in the phase — no block may break manual operation
- `audit.sh` exit code must remain 0 after every block close
- No existing protocol or template files are deleted or renamed
- SDK code lives exclusively in `sdk/` — no Python files in `cognitive-arch/` root or other subdirectories

## 4. Dependencies

- Phase 4 complete ✅ — all 12 blocks done, 6/6 exit criteria met
- `design/governor-v2.md` final ✅ — 13 decisions confirmed, 7 open questions documented in §11
- All Phase 4 protocol files exist ✅ (`protocols/task-packet.md`, `protocols/convention-snippet-generation.md`, `protocols/governor-dispatch.md`, `protocols/governor-integration.md`, `protocols/governor-failure-handling.md`, `protocols/sub-agent-contract.md`)
- Both Phase 4 templates exist ✅ (`templates/task-packet.md`, `templates/sub-agent-return.md`)
- User has Python 3.9+ and `pip` available
- User has `ANTHROPIC_API_KEY` env var set (required only for live dispatch; dry-run and unit tests work without it)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Anthropic SDK file-passing behavior differs from spec (open question 1) | High | block-029 exploration step resolves this first; block-031 adapts design before task-packet logic is written |
| Open question 3 (crash recovery) is complex to implement safely | Med | block-035 scoped to commit governor-state.md before each state transition; full recovery deferred to v2.1 if needed |
| E2E test (block-037) requires live API key — cost and rate limits | Low | block-037 uses mock return packages for automated gate; live run is manual validation step with a minimal test manifest |
| First code phase — code-header-protocol not battle-tested on Python | Low | block-029 establishes the header pattern; all subsequent blocks inherit it |
| governor-state.md conflicts with STATE.md if Governor crashes mid-write | Med | Integration module writes state files atomically (write temp → rename); documented in block-034 |

## 6. Validation

- **Unit**: each module (blocks 030-034, 036) has at least one inline test function callable via `python -m sdk.<module> --test`
- **Integration**: block-035 wires all modules and runs with a mock Anthropic client (no API key needed)
- **E2E (manual)**: block-037 runs Governor on a real test manifest with a live API key; output verified against expected state file changes
- **Regression**: `audit.sh` run after every block close — must exit 0

## 7. Exit Criteria

1. `sdk/` directory exists with files: `__init__.py`, `requirements.txt`, `governor.py`, `convention_snippet.py`, `task_packet.py`, `return_validator.py`, `dispatch.py`, `integration.py`, `config.py`
2. `pip install -r sdk/requirements.txt` exits 0 (anthropic SDK + standard-lib-only deps)
3. `python sdk/governor.py --help` exits 0 and lists `--dry-run`, `--block`, `--mode` flags
4. `python sdk/governor.py --dry-run` exits 0 and prints next block summary without dispatching any agent (reads STATE.md + NEXT.md)
5. Convention snippet generator (`sdk/convention_snippet.py --test`) produces non-empty, distinct output for each of the 4 block kinds: `doc`, `refactor`, `implementation`, `gate`
6. Return package validator (`sdk/return_validator.py --test`) accepts a valid sample package and rejects 3 malformed variants (missing field, wrong status, invalid gate format)
7. Governor integration test (`python sdk/governor.py --test-integration`) runs with a mock Anthropic client and a sample manifest, writes correct updates to a temp copy of STATE.md and BLOCK_LOG.md
8. All 7 open questions from `design/governor-v2.md §11` have documented answers in `design/governor-v2.md §11` (each item marked `resolved:` with one-line answer)
9. `bash audit.sh` exits 0 after block-037 closes

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-029 | Python project setup (`sdk/` skeleton + feature flag) | S | planned | `manifests/block-029-sdk-setup.md` |
| block-030 | Module: convention snippet generator | M | planned | `manifests/block-030-convention-snippet-module.md` |
| block-031 | Module: task packet builder | M | planned | `manifests/block-031-task-packet-module.md` |
| block-032 | Module: return package validator | S | planned | `manifests/block-032-return-validator-module.md` |
| block-033 | Module: sub-agent dispatch (Anthropic SDK) | M | planned | `manifests/block-033-dispatch-module.md` |
| block-034 | Module: state integration | M | planned | `manifests/block-034-integration-module.md` |
| block-035 | Governor main loop + crash recovery | L | planned | `manifests/block-035-governor-main-loop.md` |
| block-036 | Config + user interruption signal | S | planned | `manifests/block-036-config-interruption.md` |
| block-037 | E2E validation + open questions resolved | M | planned | `manifests/block-037-e2e-validation.md` |

## 9. Dependency Graph & Parallel Execution Plan

Module dependency graph (imports):
```
029 (setup)
  ↓
030 (convention_snippet)  ←─ no sdk imports
032 (return_validator)    ←─ no sdk imports
036 (config)              ←─ no sdk imports
  ↓
031 (task_packet)         ← imports convention_snippet (030)
034 (integration)         ← imports return_validator (032)
  ↓
033 (dispatch)            ← imports task_packet (031), config (036)
  ↓
035 (governor main)       ← imports all modules
  ↓
037 (E2E + docs)
```

```yaml
parallel_execution_plan:
  total_blocks: 9
  recommended_agents: 3
  groups:
    - id: 5A
      blocks: [block-029]
      type: sequential
      depends_on: []
      note: creates sdk/ structure; all other blocks depend on it
    - id: 5B
      blocks: [block-030, block-032, block-036]
      type: parallel
      depends_on: [5A]
      note: three independent leaf modules — no imports between them; disjoint files
    - id: 5C
      blocks: [block-031, block-034]
      type: parallel
      depends_on: [5B]
      note: block-031 needs convention_snippet (030); block-034 needs return_validator (032); no conflict
    - id: 5D
      blocks: [block-033]
      type: sequential
      depends_on: [5C]
      note: dispatch needs task_packet (031) and config (036) — both ready after 5B+5C
    - id: 5E
      blocks: [block-035]
      type: sequential
      depends_on: [5D]
      note: governor main wires all modules; must run after everything else
    - id: 5F
      blocks: [block-037]
      type: sequential
      depends_on: [5E]
      note: E2E test and protocol updates — final gate for the phase
```

## 10. Out of Scope

- Multi-repo Governor support (v3.0+)
- Cross-phase parallelism (v3.0+)
- Web UI or dashboard for Governor state (not planned)
- Governor as a persistent daemon / service (event-driven only, per Decision 6)
- Full crash recovery with transaction log (block-035 covers commit-before-transition only; full recovery is v2.1)
- Stack-specific addenda (originally roadmap Phase 5 — deferred; Governor implementation took priority)
- Security scan, perf scan, deploy command (originally roadmap Phase 5 — deferred to Phase 6 or later)
- Governor packaging for PyPI (out of scope for v2.0)
- Tests via pytest / CI pipeline (unit tests are inline `--test` flags; pytest setup is Phase 6+)
