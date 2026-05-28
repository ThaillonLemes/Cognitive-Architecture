---
id: block-054
tier: S
kind: implementation
phase: phase-7
status: done
dependencies:
  - block-051
files:
  read:
    - sdk/return_validator.py
    - sdk/tests/conftest.py
  modify: []
  create:
    - sdk/tests/test_return_validator.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/test_return_validator.py -v
    expect: "passed"
  - name: file-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 054 — pytest: return_validator tests

- **Tier:** S
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Write `sdk/tests/test_return_validator.py` covering `validate_package()`: valid package returns `valid=True`, missing required fields returns `valid=False` with error list, `evidence:` free-text is parsed correctly, `tok_in`/`tok_out` are parsed as ints.

## 2. Files

- **Read:** `sdk/return_validator.py`, `sdk/tests/conftest.py`
- **Modify:** none
- **Create:** `sdk/tests/test_return_validator.py`

## 3. Validation

- `pytest sdk/tests/test_return_validator.py -v` exits 0
- Tests: valid package, missing `b:` field, missing `gates:` field, `tok_in` parsed as int, `evidence:` multi-line parse

## 4. Out of scope

- Fuzz testing of all field combinations
