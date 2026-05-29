---
id: block-136
phase: phase-23
tier: M
kind: code
status: done
files:
  read:
    - sdk/recommendation_engine.py
    - sdk/velocity_inference.py
  modify:
    - sdk/recommendation_engine.py
    - sdk/velocity_inference.py
    - sdk/tests/test_cli_smoke.py
  create:
    - sdk/safe_io.py
    - sdk/tests/test_safe_io.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: exit-zero
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-29
---

# Block 136 — Fix crashers (UTF-8 + PermissionError)

## 1. Purpose

Fix the two CLI crashers found in block-135 so the smoke test goes fully green, and prevent the entire class of stdout-encoding crash from recurring.

## 2. Scope

In scope:
- `sdk/safe_io.py`: shared `force_utf8()` guard (errors='replace' → flush can never raise)
- recommendation_engine.py: apply guard + replace `→` with `->`
- velocity_inference.py: apply guard; add missing `import re`; fix `_find_git_root` return-inside-loop bug
- Remove both tools from smoke-test `_KNOWN_CRASHERS`

Out of scope: sweeping all 39 tools (smoke test enforces non-recurrence).

## 3. Gates

- tests-pass: 743 passed
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md
