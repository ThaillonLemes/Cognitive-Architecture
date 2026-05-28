---
id: block-058
tier: S
kind: implementation
phase: phase-7
status: done
dependencies:
  - block-055
files:
  read:
    - sdk/dispatch.py
    - sdk/return_validator.py
  modify:
    - sdk/dispatch.py
  create: []
gates:
  - name: dispatch-result-has-tok-fields
    cmd: python -c "from sdk.dispatch import DispatchResult; r = DispatchResult.__dataclass_fields__; assert 'tok_in' in r and 'tok_out' in r; print('OK')"
    expect: "OK"
  - name: mock-returns-tok-values
    cmd: python -m pytest sdk/tests/test_dispatch.py -k tok -v
    expect: "passed"
  - name: file-updated
    type: file-changed
    paths: [sdk/dispatch.py, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 058 — Token metrics: real tok_in/tok_out from API

- **Tier:** S
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Add `tok_in: int` and `tok_out: int` fields to `DispatchResult`. In SDK mode, populate from `response.usage.input_tokens` and `response.usage.output_tokens`. In mock mode, `MockAnthropicClient` returns `tok_in=100, tok_out=500` as realistic placeholders. Update `test_dispatch.py` with a test asserting tok_in > 0 after mock dispatch.

## 2. Files

- **Read:** `sdk/dispatch.py`, `sdk/return_validator.py`
- **Modify:** `sdk/dispatch.py` (add fields to DispatchResult, populate in both mock and SDK paths)
- **Create:** none

## 3. Validation

- `DispatchResult` has `tok_in` and `tok_out` int fields
- Mock dispatch returns `tok_in=100, tok_out=500`
- SDK dispatch reads from `response.usage.input_tokens/.output_tokens`
- `pytest sdk/tests/test_dispatch.py -k tok` passes

## 4. Out of scope

- Persisting token totals across sessions (that's a dashboard feature, v2.2)
- Modifying retrospective template to include tok_in/tok_out fields (already has tok_estimated field)
