---
id: block-052
tier: S
kind: implementation
phase: phase-7
status: done
dependencies:
  - block-051
files:
  read:
    - sdk/convention_snippet.py
    - sdk/tests/conftest.py
  modify: []
  create:
    - sdk/tests/test_convention_snippet.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/test_convention_snippet.py -v
    expect: "passed"
  - name: file-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 052 — pytest: convention_snippet tests

- **Tier:** S
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Write `sdk/tests/test_convention_snippet.py` covering the key behaviors of `convention_snippet.py`: sort order (P→Q→C), kind aliases, axiom override, unknown kind fallback.

## 2. Files

- **Read:** `sdk/convention_snippet.py`, `sdk/tests/conftest.py`
- **Modify:** none
- **Create:** `sdk/tests/test_convention_snippet.py`

## 3. Validation

- `pytest sdk/tests/test_convention_snippet.py -v` exits 0
- Tests include: sort order, all valid kinds, axiom_override param, unknown kind behavior, snippet body non-empty

## 4. Out of scope

- Exhaustive testing of all 19 axioms (sample coverage sufficient)
