---
id: phase-7
status: complete
version: v2.1
prev_phase: phase-6
exit_criteria_count: 10
blocks_count: 10
estimated_duration_days: 5
created_at: 2026-05-22
last_updated: 2026-05-22
owner: implementer
---

# Phase 7 — SDK Depth (v2.1)

BRIEF: Adds the four capabilities deferred from Phase 5/6: a full pytest suite for all SDK modules, bash-executable versions of audit.sh checks 5–8, actual token metric capture from API responses, file content snippets in task packets, and parallel batch dispatch via ThreadPoolExecutor. After this phase the SDK is production-grade.

## 1. Purpose

Phase 6 left the SDK working but undertested and incompletely wired: no pytest suite, audit checks 5–8 are "Governor-only" stubs, token metrics are estimated proxies (not real API numbers), task packets contain file paths but not file content, and dispatch is strictly sequential. Phase 7 closes all four gaps in a focused 10-block pass. The deliverable is a SDK where every module has tests, the audit script runs all 8 checks, the Governor tracks real token usage, packets carry file snippets so sub-agents have context without extra reads, and a `--parallel N` flag enables batch dispatch.

## 2. Goals

- `pytest sdk/tests/` runs with 0 failures covering all 7 SDK modules
- `audit.sh` runs checks 5–8 (manifest schema, dependency validation, drift detection, conflict detection) and outputs results in the same format as checks 1–4
- `DispatchResult` captures real `tok_in` / `tok_out` from Anthropic API responses (not chars÷4 proxies)
- Task packets include truncated file content snippets for all `files.read` entries (first 30 lines each)
- `python sdk/governor.py --parallel N --block-range X-Y` dispatches N blocks concurrently via `ThreadPoolExecutor`
- `audit.sh` exits 0 (no new errors or warnings introduced by Phase 7)

## 3. Invariants

- All Phase 5/6 SDK behavior preserved — no breaking changes to existing module APIs
- `governor_mode: manual` path must remain fully functional at every block
- `audit.sh` exit code remains 0 after every block close
- pytest suite is additive — no production code renamed or deleted

## 4. Dependencies

- Phase 6 complete ✅ — all 13 blocks done, all 12 exit criteria met
- `sdk/` package with 7 modules exists ✅
- `sdk/requirements.txt` has `anthropic>=0.25.0` and `pyyaml>=6.0` ✅
- `pytest` available (`pip install pytest`) — added to `sdk/requirements.txt` in block-051

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| pytest import errors (sibling import pattern) | Med | conftest.py adds sdk/ to sys.path; block-051 resolves this first |
| audit.sh check 7 (conflict detection) complex in bash | Med | block-058 uses a Python helper script called from bash |
| Parallel dispatch race on state files | Med | block-060 uses ThreadPoolExecutor for dispatch only; integration stays sequential |
| Anthropic API not available for token metric test | Low | tok_in/tok_out extracted from mock response in test mode; real values only in sdk mode |

## 6. Validation

- **Unit:** `pytest sdk/tests/` — 0 failures
- **Script:** `bash audit.sh` — exits 0, all 8 checks reported
- **CLI:** `python sdk/governor.py --parallel 2 --dry-run` exits 0
- **Integration:** `python sdk/governor.py --test-integration` still passes after all changes

## 7. Exit Criteria

1. `sdk/tests/` directory exists with `conftest.py` and at least 5 test files
2. `pytest sdk/tests/ -q` exits 0 with 0 failures (≥15 test cases total)
3. `audit.sh` reports `[5/8]`, `[6/8]`, `[7/8]`, `[8/8]` checks (no longer says "not implemented")
4. `audit.sh` exits 0 after Phase 7 (same or fewer warnings than Phase 6 baseline)
5. `DispatchResult` has fields `tok_in: int` and `tok_out: int`; mock client returns non-zero values
6. `dispatch.py` docstring documents tok_in/tok_out source (API response vs mock)
7. `task_packet.build_packet()` accepts optional `include_content: bool` param; when True, first 30 lines of each fread file are appended to packet
8. `python sdk/governor.py --parallel 2 --dry-run` exits 0 and prints "parallel mode: 2 workers"
9. `python sdk/governor.py --test-integration` still passes (regression gate)
10. `sdk/requirements.txt` lists `pytest>=7.0` and all existing deps

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-051 | pytest: infrastructure + conftest | S | planned | `manifests/block-051-pytest-infra.md` |
| block-052 | pytest: convention_snippet tests | S | planned | `manifests/block-052-test-convention-snippet.md` |
| block-053 | pytest: task_packet tests | S | planned | `manifests/block-053-test-task-packet.md` |
| block-054 | pytest: return_validator tests | S | planned | `manifests/block-054-test-return-validator.md` |
| block-055 | pytest: dispatch + integration tests | M | planned | `manifests/block-055-test-dispatch-integration.md` |
| block-056 | audit.sh checks 5+6: schema + dep validation | M | planned | `manifests/block-056-audit-checks-56.md` |
| block-057 | audit.sh checks 7+8: conflict + drift | M | planned | `manifests/block-057-audit-checks-78.md` |
| block-058 | Token metrics: real tok_in/tok_out from API | S | planned | `manifests/block-058-token-metrics.md` |
| block-059 | File content snippets in task packets | S | planned | `manifests/block-059-file-content-packets.md` |
| block-060 | Parallel batch dispatch + phase gate | M | planned | `manifests/block-060-parallel-dispatch.md` |

## 9. Dependency Graph & Parallel Execution Plan

Sequential execution (single implementer agent).

```yaml
parallel_execution_plan:
  total_blocks: 10
  recommended_agents: 1
  execution_mode: sequential
  groups:
    - id: 7A
      blocks: [block-051]
      type: sequential
      depends_on: []
      note: "pytest infra must exist before test files"
    - id: 7B
      blocks: [block-052, block-053, block-054]
      type: sequential
      depends_on: [7A]
      note: "Unit tests per module (could be parallel but sequential per user choice)"
    - id: 7C
      blocks: [block-055]
      type: sequential
      depends_on: [7B]
      note: "Integration tests depend on unit test fixtures"
    - id: 7D
      blocks: [block-056, block-057]
      type: sequential
      depends_on: [7A]
      note: "audit.sh extensions (independent of pytest)"
    - id: 7E
      blocks: [block-058, block-059]
      type: sequential
      depends_on: [7C]
      note: "SDK capability additions — build on tested modules"
    - id: 7F
      blocks: [block-060]
      type: sequential
      depends_on: [7D, 7E]
      note: "Parallel dispatch + full regression gate — last block"
```

## 10. Out of Scope

- Async/asyncio dispatch (ThreadPoolExecutor threads are sufficient; asyncio adds complexity without benefit for blocking HTTP calls)
- pytest coverage reporting (can be added per-user with `--cov` flag; not required by gates)
- `audit.sh` checks for stack addenda completeness (out of scope for this version)
- Django, NestJS, or additional stack addenda
- Phase 7 retrospective / `phases/phase-7-retro.md` — generated at phase close, not in scope here

---

End of phase-7.md.
