---
id: block-034
tier: M
kind: feature
phase: phase-5
status: wip
files:
  read:
    - protocols/governor-integration.md
    - protocols/governor-dispatch.md
    - sdk/return_validator.py
    - _syntax.md
  modify: []
  create:
    - sdk/integration.py
gates:
  - name: integration-test
    type: cmd
    cmd: "python cognitive-arch/sdk/integration.py --test"
    expect: "exit 0, state files updated correctly in temp dir"
  - name: files-created
    type: file-changed
    paths: [sdk/integration.py]
created_at: 2026-05-22
---

# Block 034 — Module: state integration

- **Tier:** M
- **Kind:** feature
- **Status:** wip

## 1. Purpose

Implement `sdk/integration.py` — after a parallel group of sub-agents returns, Governor calls this module to update STATE.md, NEXT.md, BLOCK_LOG.md, board.md, and optionally commit via git. Handles conflict detection (fmod disjoint check) and atomic file writes.

## 2. Files

- **Read:** `protocols/governor-integration.md`, `protocols/governor-dispatch.md`, `sdk/return_validator.py`, `_syntax.md`
- **Modify:** none
- **Create:** `sdk/integration.py`

## 3. Validation

- `python sdk/integration.py --test` exits 0
- Test verifies: STATE.md updated correctly, BLOCK_LOG.md appended, fmod disjoint check fires on conflict

## 4. Out of scope

- Git commit execution (no git repo in this project — logged as no-op)
- governor-state.md group tracking (block-035)
- Crash recovery (block-035)
