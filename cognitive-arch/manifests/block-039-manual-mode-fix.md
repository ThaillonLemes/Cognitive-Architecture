---
id: block-039
tier: S
kind: small-fix
phase: phase-6
status: done
dependencies:
  - block-038
files:
  read:
    - sdk/governor.py
  modify:
    - sdk/governor.py
  create: []
gates:
  - name: manual-mode-routes-correctly
    cmd: python sdk/governor.py --mode manual --dry-run
    expect: "manual mode"
  - name: mock-mode-still-works
    cmd: python sdk/governor.py --mode mock --dry-run
    expect: "exit 0"
  - name: file-updated
    type: file-changed
    paths: [sdk/governor.py, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 039 — Fix manual-mode routing bug in governor.py

- **Tier:** S
- **Kind:** small-fix
- **Status:** planned

## 1. Purpose

Fix the bug in `sdk/governor.py` where `--mode manual` incorrectly sets `dispatch_mode = "mock"`. The line `dispatch_mode = "mock" if args.mode != "sdk"` collapses both `manual` and `mock` into mock dispatch. After this fix, `manual` must route to the manual path (print instructions, do not dispatch) and `mock` must route to `MockAnthropicClient`.

## 2. Files

- **Read:** `sdk/governor.py` (focus on `cmd_block` and the `dispatch_mode` assignment)
- **Modify:** `sdk/governor.py`
- **Create:** none

## 3. Validation

- `python sdk/governor.py --mode manual --dry-run` exits 0 and output contains "manual" (not "mock dispatch")
- `python sdk/governor.py --mode mock --dry-run` still works
- `python sdk/governor.py --mode sdk --dry-run` still works (no key needed for dry-run)
- Fix: change dispatch logic to `if args.mode == "sdk": dispatch_mode = "sdk" elif args.mode == "mock": dispatch_mode = "mock" else: dispatch_mode = "manual"`

## 4. Out of scope

- Changing the `--mode` flag interface or adding new modes
- Wiring real SDK dispatch end-to-end (block-037 already handles that)
- Updating documentation for the fix (INDEX.md will be updated in block-044)
