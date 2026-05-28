---
id: block-053
tier: S
kind: implementation
phase: phase-7
status: done
dependencies:
  - block-051
files:
  read:
    - sdk/task_packet.py
    - sdk/tests/conftest.py
  modify: []
  create:
    - sdk/tests/test_task_packet.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/test_task_packet.py -v
    expect: "passed"
  - name: file-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 053 — pytest: task_packet tests

- **Tier:** S
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Write `sdk/tests/test_task_packet.py` covering `build_packet()`: valid packet header fields, fread/fmod parsing from manifest frontmatter, scope assignment, error on missing manifest.

## 2. Files

- **Read:** `sdk/task_packet.py`, `sdk/tests/conftest.py`
- **Modify:** none
- **Create:** `sdk/tests/test_task_packet.py`

## 3. Validation

- `pytest sdk/tests/test_task_packet.py -v` exits 0
- Tests: packet contains `b:` field, `gov:` field, `fread:` field, missing-manifest raises exception

## 4. Out of scope

- Testing `include_content` parameter (added in block-059)
