---
id: block-059
tier: S
kind: implementation
phase: phase-7
status: done
dependencies:
  - block-055
files:
  read:
    - sdk/task_packet.py
    - sdk/tests/test_task_packet.py
  modify:
    - sdk/task_packet.py
    - sdk/tests/test_task_packet.py
  create: []
gates:
  - name: include-content-param-works
    cmd: python -c "from sdk.task_packet import build_packet; print('OK')"
    expect: "OK"
  - name: tests-pass
    cmd: python -m pytest sdk/tests/test_task_packet.py -v
    expect: "passed"
  - name: file-updated
    type: file-changed
    paths: [sdk/task_packet.py, sdk/tests/test_task_packet.py, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 059 — File content snippets in task packets

- **Tier:** S
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Extend `task_packet.build_packet()` with an optional `include_content: bool = False` parameter. When `True`, for each path in `files.read`, append the first 30 lines of that file to the packet under a `--- file content ---` section. Sub-agents then have the context inline without extra reads. Gracefully skip files that don't exist or can't be read.

## 2. Files

- **Read:** `sdk/task_packet.py`, `sdk/tests/test_task_packet.py`
- **Modify:** `sdk/task_packet.py` (add `include_content` param), `sdk/tests/test_task_packet.py` (add test for new param)
- **Create:** none

## 3. Validation

- `build_packet(..., include_content=True)` includes `--- file content ---` section when fread files exist
- `build_packet(..., include_content=False)` (default) behavior unchanged
- Missing fread file is skipped with a `# (not found: path)` comment
- `pytest sdk/tests/test_task_packet.py -v` passes (including new test)

## 4. Out of scope

- Configuring the 30-line limit per-file (hardcoded for now)
- Binary file support
- Streaming large files
