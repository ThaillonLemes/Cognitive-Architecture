---
id: block-033
tier: M
kind: feature
phase: phase-5
status: wip
files:
  read:
    - protocols/governor-dispatch.md
    - protocols/governor-failure-handling.md
    - design/governor-v2.md
    - sdk/task_packet.py
    - sdk/return_validator.py
  modify: []
  create:
    - sdk/dispatch.py
gates:
  - name: dispatch-test
    type: cmd
    cmd: "python cognitive-arch/sdk/dispatch.py --test"
    expect: "exit 0, mock dispatch returns valid return package"
  - name: files-created
    type: file-changed
    paths: [sdk/dispatch.py]
created_at: 2026-05-22
---

# Block 033 — Module: sub-agent dispatch (Anthropic SDK)

- **Tier:** M
- **Kind:** feature
- **Status:** wip

## 1. Purpose

Implement `sdk/dispatch.py` — sends a task packet to a Claude sub-agent via the Anthropic Python SDK and collects the return package. Includes a mock client for testing without an API key, a fallback timer, and a manual-mode path that prints the packet instead of dispatching.

## 2. Files

- **Read:** `protocols/governor-dispatch.md`, `protocols/governor-failure-handling.md`, `design/governor-v2.md`, `sdk/task_packet.py`, `sdk/return_validator.py`
- **Modify:** none
- **Create:** `sdk/dispatch.py`

## 3. Validation

- `python sdk/dispatch.py --test` exits 0
- Mock dispatch returns a valid return package that passes `validate_package()`

## 4. Out of scope

- Two-phase scope negotiation full loop (block-035)
- Crash recovery / governor-state.md write (block-035)
- Actual multi-agent parallelism (block-035 orchestrates; dispatch handles one block at a time)
