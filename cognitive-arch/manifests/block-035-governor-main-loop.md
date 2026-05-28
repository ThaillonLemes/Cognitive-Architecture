---
id: block-035
tier: L
kind: feature
phase: phase-5
status: wip
files:
  read:
    - sdk/governor.py
    - sdk/convention_snippet.py
    - sdk/task_packet.py
    - sdk/return_validator.py
    - sdk/dispatch.py
    - sdk/integration.py
    - protocols/governor-dispatch.md
    - protocols/governor-failure-handling.md
    - design/governor-v2.md
    - governance/governor-state.md
  modify:
    - sdk/governor.py
    - governance/governor-state.md
  create:
    - sdk/config.py
gates:
  - name: integration-test
    type: cmd
    cmd: "python cognitive-arch/sdk/governor.py --test-integration"
    expect: "exit 0, mock run completes, state files updated"
  - name: dry-run-still-works
    type: cmd
    cmd: "python cognitive-arch/sdk/governor.py --dry-run"
    expect: "exit 0"
created_at: 2026-05-22
---

# Block 035 — Governor main loop + crash recovery

- **Tier:** L
- **Kind:** feature
- **Status:** wip

## 1. Purpose

Wire all SDK modules into `governor.py`'s main orchestration loop. Implement `--test-integration` (full mock run through dispatch → validate → integrate cycle). Write governor-state.md before each state transition (crash recovery). Add `sdk/config.py` for max_parallel_agents and pause signal.

## 2. Files

- **Read:** all sdk/ modules, protocols/governor-dispatch.md, protocols/governor-failure-handling.md, design/governor-v2.md, governance/governor-state.md
- **Modify:** `sdk/governor.py` (wire loop), `governance/governor-state.md` (template update)
- **Create:** `sdk/config.py`

## 3. Validation

- `python sdk/governor.py --test-integration` exits 0 and prints state update summary
- `python sdk/governor.py --dry-run` still exits 0 (regression)

## 4. Out of scope

- Live API key run (block-037)
- Full phase close trigger (block-037)
- User interruption signal (.pause file) — implemented in block-036
