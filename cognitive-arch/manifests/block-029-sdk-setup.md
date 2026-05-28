---
id: block-029
tier: S
kind: small-fix
phase: phase-5
status: wip
files:
  read:
    - design/governor-v2.md
    - _syntax.md
    - protocols/governor-dispatch.md
  modify:
    - _syntax.md
  create:
    - sdk/__init__.py
    - sdk/requirements.txt
    - sdk/governor.py
    - governance/governor-state.md
gates:
  - name: governor-help
    type: cmd
    cmd: "python cognitive-arch/sdk/governor.py --help"
    expect: "exit 0"
  - name: governor-dry-run
    type: cmd
    cmd: "python cognitive-arch/sdk/governor.py --dry-run"
    expect: "exit 0"
  - name: files-created
    type: file-changed
    paths: [sdk/__init__.py, sdk/requirements.txt, sdk/governor.py, governance/governor-state.md]
created_at: 2026-05-22
---

# Block 029 — Python project setup (`sdk/` skeleton + feature flag)

- **Tier:** S
- **Kind:** small-fix
- **Status:** wip

## 1. Purpose

Create the `sdk/` Python package directory with skeleton files — requirements, empty `__init__.py`, and a functioning `governor.py` CLI entry (--help, --dry-run, --block, --mode) — plus `governance/governor-state.md` template for ephemeral session state. Add `governor_mode` key to `_syntax.md`.

## 2. Files

- **Read:** `design/governor-v2.md`, `_syntax.md`, `protocols/governor-dispatch.md`
- **Modify:** `_syntax.md` (add `governor_mode` key)
- **Create:** `sdk/__init__.py`, `sdk/requirements.txt`, `sdk/governor.py`, `governance/governor-state.md`

## 3. Validation

- `python cognitive-arch/sdk/governor.py --help` exits 0 and lists all flags
- `python cognitive-arch/sdk/governor.py --dry-run` exits 0 and prints STATE.md + NEXT.md summary
- All 4 files exist

## 4. Out of scope

- Any module logic beyond the CLI skeleton (convention_snippet, task_packet, etc. — blocks 030-036)
- Actual Anthropic SDK calls (block-033)
- governor-state.md write logic (block-035)
