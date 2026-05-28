---
id: block-051
tier: S
kind: implementation
phase: phase-7
status: done
files:
  read:
    - sdk/requirements.txt
    - sdk/governor.py
  modify:
    - sdk/requirements.txt
  create:
    - sdk/tests/__init__.py
    - sdk/tests/conftest.py
    - sdk/pytest.ini
gates:
  - name: pytest-runs
    cmd: python -m pytest sdk/tests/ -q --tb=short
    expect: "passed"
  - name: file-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 051 — pytest: infrastructure + conftest

- **Tier:** S
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Set up the pytest test infrastructure for the `sdk/` package: add `pytest>=7.0` to `requirements.txt`, create `sdk/tests/__init__.py`, write `sdk/tests/conftest.py` with shared fixtures (arch_root path, temp arch directory, sample manifest content), and create `sdk/pytest.ini` pointing at the tests directory.

## 2. Files

- **Read:** `sdk/requirements.txt`, `sdk/governor.py` (for ARCH_ROOT reference)
- **Modify:** `sdk/requirements.txt` (add pytest>=7.0)
- **Create:** `sdk/tests/__init__.py`, `sdk/tests/conftest.py`, `sdk/pytest.ini`

## 3. Validation

- `python -m pytest sdk/tests/ -q` exits 0 (no test files yet but infra works)
- `sdk/tests/conftest.py` provides: `arch_root` fixture, `tmp_arch` fixture (temp dir copy), `sample_manifest_path` fixture
- `sdk/requirements.txt` contains `pytest>=7.0`

## 4. Out of scope

- Actual test cases (blocks 052-055)
- Coverage reporting
- CI integration (GitHub Actions)
