---
id: block-032
tier: S
kind: small-fix
phase: phase-5
status: wip
files:
  read:
    - templates/sub-agent-return.md
    - protocols/sub-agent-contract.md
    - _syntax.md
  modify: []
  create:
    - sdk/return_validator.py
gates:
  - name: validator-test
    type: cmd
    cmd: "python cognitive-arch/sdk/return_validator.py --test"
    expect: "exit 0, 1 valid accepted, 3 malformed rejected"
  - name: files-created
    type: file-changed
    paths: [sdk/return_validator.py]
created_at: 2026-05-22
---

# Block 032 — Module: return package validator

- **Tier:** S
- **Kind:** small-fix
- **Status:** wip

## 1. Purpose

Implement `sdk/return_validator.py` — parses a sub-agent return package string (compressed `_syntax.md` key:value format), validates all required fields and values, and returns a structured result for the Governor to act on.

## 2. Files

- **Read:** `templates/sub-agent-return.md`, `protocols/sub-agent-contract.md`, `_syntax.md`
- **Modify:** none
- **Create:** `sdk/return_validator.py`

## 3. Validation

- `python sdk/return_validator.py --test` exits 0
- Accepts 1 valid package; rejects 3 malformed variants (missing field, bad status, bad gate format)

## 4. Out of scope

- Governor action on validation result (block-035)
- Schema Mode 5 (schema-invalid return — logged in governor-failure-handling.md)
