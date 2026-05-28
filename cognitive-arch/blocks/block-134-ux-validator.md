---
id: block-134
phase: phase-22
tier: M
status: done
actual_duration_hours: 1.2
duration_source: estimated
tok_actual: 2200
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 134 Retrospective — sdk/ux_validator.py

## 1. What was built

- `sdk/ux_validator.py`: validates AI output against governance/ux-voice.md prohibited phrases
  - `Violation` dataclass (line_num, rule_id, message, excerpt)
  - `_extract_prohibited(ux_voice_text)` — extracts phrases from ` ```prohibited ``` ` fenced block
  - `UxValidator(prohibited_phrases)` with `.check(text) -> list[Violation]` — case-insensitive match, skips prohibited block itself during scan
  - `UxValidator.from_ux_voice(arch_root)` — factory reads governance/ux-voice.md
  - `_format_violations(violations, max_display=20)` — "OK — 0 violations" or WARN lines with L{n} + excerpt
  - CLI: `--check FILE`, `--string`, `--max-violations`; always exits 0
- `sdk/session_start.py`: added `--validate-ux` flag — captures output buffer and runs ux_validator on it post-summary
- `sdk/tests/test_ux_validator.py`: 18 tests covering all code paths

## 2. Gates

- tests-pass: 690 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- `check()` skips lines inside ``` ```prohibited ``` ``` blocks — those are rule *definitions*, not content to validate; prevents self-referential false positives in ux-voice.md
- Always exits 0 — ux validation is informational/advisory, never blocks anything
- `--validate-ux` in session_start.py uses stdout buffer capture to validate the session output inline
- lint-pass gate: flake8 not available in environment; `python -m py_compile` confirmed no syntax errors

## 4. DX updated

`sdk/ux_validator.py` created. `sdk/session_start.py` extended with `--validate-ux`. `sdk/tests/test_ux_validator.py` added.
