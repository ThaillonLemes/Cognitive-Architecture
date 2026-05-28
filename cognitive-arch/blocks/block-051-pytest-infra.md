---
id: block-051
manifest: manifests/block-051-pytest-infra.md
status: done
gates_passed: 1/1
completed_at: 2026-05-22T07:10Z
agent: implementer
commit: -
duration_actual_days: 0
tok_estimated: ~400
tok_src: estimated
---

# Block 051 Retrospective — pytest: infrastructure + conftest

## 1. What was built

- Added `pytest>=7.0` to `sdk/requirements.txt`
- Created `sdk/tests/__init__.py` (package marker)
- Created `sdk/tests/conftest.py`: 3 fixtures — `arch_root` (session scope, real arch path), `tmp_arch` (function scope, isolated temp copy of state files), `sample_manifest_path` (creates minimal valid S-tier manifest in temp dir)
- Created `sdk/pytest.ini`: testpaths=tests, standard options
- Verified: `python -m pytest tests/ -q` runs without import errors (exit 5 = "no tests collected", expected)

## 2. Tests added

Infrastructure only (no test cases yet).

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| pytest-runs | ✓ | pytest 9.0.3 installed; runs without errors; "no tests ran" (0 items) as expected for infra-only block |

## 4. Decisions made

- `arch_root` fixture is session-scoped (expensive path resolution once per session)
- `tmp_arch` is function-scoped (fresh isolation per test)
- `sys.path.insert(0, str(_SDK_DIR))` in conftest ensures all sibling modules are importable in tests without package install

## 5. Deferred to future blocks

- Actual test cases (blocks 052-055)

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `sdk/requirements.txt` | ~300 | ~75 |
| `sdk/governor.py` (ARCH_ROOT pattern) | ~500 | ~125 |

```
tok_estimated: ~200  tok_src:estimated
```

## 7. Issues / surprises

pytest was already installed (v9.0.3 via existing Python environment). No install needed.

## 8. Files actually touched

As manifest plus sdk/pytest.ini (not in manifest create list — added as beneficial extra).
