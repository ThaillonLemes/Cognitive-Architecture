---
id: block-060
tier: M
kind: implementation
phase: phase-7
scope: phase-bound
status: done
dependencies:
  - block-057
  - block-058
  - block-059
files:
  read:
    - sdk/dispatch.py
    - sdk/governor.py
    - sdk/config.py
    - sdk/integration.py
  modify:
    - sdk/dispatch.py
    - sdk/governor.py
  create:
    - sdk/tests/test_parallel_dispatch.py
gates:
  - name: parallel-dry-run
    cmd: python sdk/governor.py --parallel 2 --dry-run
    expect: "parallel mode"
  - name: full-test-suite
    cmd: python -m pytest sdk/tests/ -q
    expect: "passed"
  - name: integration-test-still-passes
    cmd: python sdk/governor.py --test-integration
    expect: "PASS"
  - name: final-audit
    cmd: bash audit.sh
    expect: "exit 0"
  - name: file-updated
    type: file-changed
    paths: [sdk/dispatch.py, sdk/governor.py, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 060 — Parallel batch dispatch + phase gate

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Add `dispatch_batch(packets, mode, ...)` to `dispatch.py` using `concurrent.futures.ThreadPoolExecutor`. Add `--parallel N` flag to `governor.py` CLI: when set, reads N pending block manifests from the phase and dispatches them concurrently (integration stays sequential). Also serves as the Phase 7 regression gate: runs full pytest suite, `--test-integration`, and `audit.sh`.

## 2. Dependencies

`block-057` (audit.sh 7+8), `block-058` (tok_in/tok_out), `block-059` (include_content). All SDK capability additions must be in place for this final regression pass.

## 3. Files

- **Read:** `sdk/dispatch.py`, `sdk/governor.py`, `sdk/config.py`, `sdk/integration.py`
- **Modify:** `sdk/dispatch.py` (add `dispatch_batch()`), `sdk/governor.py` (add `--parallel` arg)
- **Create:** `sdk/tests/test_parallel_dispatch.py`

## 4. Validation

- `python sdk/governor.py --parallel 2 --dry-run` exits 0, prints "parallel mode: 2 workers"
- `dispatch_batch([p1, p2], mode="mock")` returns list of 2 DispatchResults
- `pytest sdk/tests/ -q` — all tests pass (regression)
- `python sdk/governor.py --test-integration` — PASS (regression)
- `bash audit.sh` — exits 0, all 8 checks reported

## 5. Gates

Four gates — all must pass.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ThreadPoolExecutor timeout per worker | Med | Use `GovConfig.timeout_sec` per thread; failed threads return error DispatchResult |
| Integration sequential after parallel dispatch | Low | `integrate_group` is not thread-safe by design; call sequentially after all threads complete |

## 7. Out of scope

- asyncio (ThreadPoolExecutor is sufficient for blocking HTTP)
- Auto-selection of parallel group from phase manifest (manual `--block-range` only for now)
- Phase 7 retrospective (generated at phase close, not in this block)
