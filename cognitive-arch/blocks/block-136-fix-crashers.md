---
id: block-136
phase: phase-23
tier: M
status: done
actual_duration_hours: 0.9
duration_source: estimated
tok_actual: 3200
gates_passed: 2/2
created_at: 2026-05-29
---

# Block 136 Retrospective — Fix crashers (UTF-8 + PermissionError)

## 1. What was built

- `sdk/safe_io.py`: shared `force_utf8()` — reconfigures stdout/stderr to UTF-8 with `errors='replace'`; idempotent; never raises
- `sdk/recommendation_engine.py`: imports + calls `force_utf8()`; `→` replaced with `->`
- `sdk/velocity_inference.py`: replaced weak win32-only `_fix_utf8` with `force_utf8()`; added missing `import re`; fixed `_find_git_root` (the final `return` was indented inside the loop, so it only ever checked the first parent)
- `sdk/tests/test_safe_io.py`: 4 tests (idempotent, wraps cp1252 stream, survives None stream, unencodable char doesn't raise)
- `sdk/tests/test_cli_smoke.py`: `_KNOWN_CRASHERS` emptied — both now pass normally

## 2. Gates

- tests-pass: 743 passed, 0 failed, 0 xfailed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Root cause (verified)

The crash had two faces from one cause: under a redirected pipe with a cp1252 locale, Python (a) raised `UnicodeEncodeError` mid-run printing `→`, and (b) returned **exit 120** at shutdown when it could not flush buffered un-encodable output. `errors='replace'` kills both: encoding can never raise, so flush always succeeds. Direct terminal runs masked the bug (exit 0) — only the piped/cp1252 path (what the smoke test forces) exposed it.

## 4. Bonus bugs fixed

- velocity `import re` was missing → `_tier_from_manifest` would `NameError` whenever called
- velocity `_find_git_root` returned on the first loop iteration (indent bug) → never walked up the tree

## 5. DX updated

`sdk/safe_io.py` is now the canonical stdout guard for new CLI tools.
