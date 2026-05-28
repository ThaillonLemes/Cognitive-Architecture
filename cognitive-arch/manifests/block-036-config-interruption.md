---
id: block-036
tier: S
kind: small-fix
phase: phase-5
status: done
files:
  read:
    - design/governor-v2.md
    - sdk/governor.py
  modify: []
  create:
    - sdk/config.py
gates:
  - name: config-exists
    type: file-changed
    paths: [sdk/config.py]
  - name: config-runs
    type: cmd
    cmd: "python cognitive-arch/sdk/config.py"
    expect: "exit 0"
created_at: 2026-05-22
---

# Block 036 — Config + user interruption signal

- **Tier:** S
- **Kind:** small-fix
- **Status:** done (delivered inside block-035)

## 1. Purpose

`sdk/config.py` with `GovConfig` dataclass, `load_config()`, and pause-file interruption mechanism. Delivered inside block-035 (scope absorbed cleanly — no conflicts).

## 2. Files

- **Create:** `sdk/config.py` ✅ (created in block-035)

## 3. Validation

- `sdk/config.py` exists ✅
- `python sdk/config.py` prints config summary

## 4. Out of scope

Nothing deferred.
