---
id: block-058
manifest: manifests/block-058-token-metrics.md
status: done
gates_passed: 2/2
completed_at: 2026-05-22T09:45Z
agent: implementer
commit: -
duration_actual_days: 0
tok_estimated: ~100
tok_src: estimated
---

# Block 058 Retrospective — Token metrics: real tok_in/tok_out from API

## 1. What was built

- `sdk/dispatch.py` docstring updated: added "Token tracking" section documenting tok source per mode (SDK = API response.usage, Mock = realistic placeholders 100/500, Manual = 0)
- Mock dispatch `tok_in`/`tok_out` adjusted to match spec: 100 and 500 respectively (previously 500 and 200)
- `test_dispatch.py` test `test_dispatch_result_has_tok_in_tok_out` sharpened from `>= 0` to `> 0` to verify positive mock values

## 2. Pre-existing state

`DispatchResult` already had `tok_in: int = 0` and `tok_out: int = 0` fields (built in Phase 5/block-033). SDK mode already populated them from `response.usage.input_tokens`/`output_tokens`. Block-058's deliverable was therefore: document the source, align mock values to spec, and sharpen the gate test.

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| dispatch-result-has-tok-fields | ✓ | `DispatchResult.__dataclass_fields__` has `tok_in`, `tok_out` |
| mock-returns-tok-values | ✓ | `pytest -k tok` → 2 passed |

## 4. Token estimate

```
tok_estimated: ~100  tok_src:estimated
```

## 5. Files actually touched

- `sdk/dispatch.py` — docstring + mock values updated
- `sdk/tests/test_dispatch.py` — tok test sharpened to `> 0`
