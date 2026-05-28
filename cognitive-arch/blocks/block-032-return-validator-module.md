---
id: block-032
phase: phase-5
status: done
gates_passed: 2
gates_total: 2
created_at: 2026-05-22
---

# Block 032 Retrospective — Module: return package validator

## §1 What was built

- `sdk/return_validator.py` — full module with:
  - `_parse_kv(text)` — parses compressed key:value format (multi-line, multi-token-per-line, handles `evidence:` free-text line)
  - `ValidationResult` dataclass (valid, errors, parsed, evidence)
  - `validate_package(raw_text)` — checks required fields, status values, gate format, retro consistency, tok_in/tok_out format
  - CLI: `--test` (4 cases), `--stdin` (pipe a package for validation)

## §2 Gates

| Gate | Result | Evidence |
|------|--------|---------|
| validator-test | ✅ pass | 4/4 cases: 1 valid accepted, 3 malformed rejected with correct errors |
| files-created | ✅ pass | sdk/return_validator.py exists |

## §3 Decisions / deviations

- No deviations. Single file created per manifest.
- `_parse_kv` handles space-separated tokens per line (matches _syntax.md convention format).
- `retro_path` field: parsed correctly despite containing `/` characters (colon partition on first `:` only).

## §4 Scope

No scope expansion.

## §5 Token estimate

tok_in:~3500 tok_out:~1200 tok_src:estimated
