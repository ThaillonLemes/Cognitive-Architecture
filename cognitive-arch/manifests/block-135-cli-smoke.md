---
id: block-135
phase: phase-23
tier: M
kind: test
status: planned
files:
  read:
    - sdk/recommendation_engine.py
    - sdk/velocity_inference.py
  modify: []
  create:
    - sdk/tests/test_cli_smoke.py
gates:
  - name: tests-collected
    type: command
    command: python -m pytest sdk/tests/test_cli_smoke.py -q
    expect: runs (xfail allowed for known crashers pre-136)
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-29
---

# Block 135 — CLI smoke-test harness

## 1. Purpose

690 unit tests exist, but none run the tools the way the user does (`python sdk/foo.py`). That is why a crashing recommendation_engine shipped. This block adds a smoke test that executes every `sdk/*.py` as a subprocess under `PYTHONIOENCODING=cp1252` (the user's real Windows console condition) and asserts no traceback.

## 2. Scope

In scope:
- `sdk/tests/test_cli_smoke.py`: discover all `sdk/*.py` (skip `__init__`, `*_schema`, `conftest`)
- For each tool: `--help` must exit 0 with no traceback under cp1252
- Curated real-run list (read-only generators) against a fixture: assert no traceback
- The two known crashers (recommendation_engine, velocity_inference) are marked `xfail(strict=True)` so the suite is green now and the xfail flips to pass after block-136

Out of scope:
- Fixing the crashers (block-136)
- Per-tool full-arg coverage for the 14 needs-args tools (only --help here)

## 3. Gates

- tests-collected: `python -m pytest sdk/tests/test_cli_smoke.py -q` runs
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md
