---
id: block-113
tier: M
kind: implementation
phase: phase-18
scope: phase-bound
status: planned
security: false
dependencies:
  - block-112
files:
  read:
    - blocks/BLOCK_LOG.md
    - sdk/block_close.py
    - sdk/health_report.py
  modify: []
  create:
    - sdk/token_tracker.py
    - sdk/tests/test_token_tracker.py
    - governance/token-report.md
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: lint-pass
    cmd: python -m flake8 sdk/token_tracker.py --max-line-length=120
    expect: "0 errors"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-113-token-tracker.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-112]
created_at: 2026-05-28
---

# Block 113 — token_tracker.py

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Build sdk/token_tracker.py: reads all blocks/*-retro.md files, extracts tok_estimated and tok_actual fields, produces governance/token-report.md with per-block and per-phase token summary. Handles null tok_actual gracefully (marks as missing, not zero). Integrates into session_start.py TOOL_RUNNERS.

## 2. Dependencies

- block-112: tok_actual enforcement ensures the field exists going forward

## 3. Files

- **Read:** blocks/BLOCK_LOG.md, sdk/block_close.py (pattern reference), sdk/health_report.py (output format reference)
- **Modify:** None (session_start.py integration deferred to block-115 which needs the report)
- **Create:** sdk/token_tracker.py, sdk/tests/test_token_tracker.py, governance/token-report.md (first run)

## 4. Validation

- Run `python sdk/token_tracker.py --arch-root .` — produces governance/token-report.md
- token-report.md has columns: block_id, phase, tok_estimated, tok_actual, delta, date, missing
- Blocks with null tok_actual appear with missing:true and delta:null
- Test with mock retros covering: has both fields, missing tok_actual, malformed YAML
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, lint-pass, files-updated, dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Retro YAML parsing fails on edge cases | Med | Unit tests cover 5 variants; null-safe parsing with try/except per file |
| token-report.md format conflicts with dashboard parser | Low | Format matches health-report.md conventions; markdown table with consistent headers |

## 7. Out of Scope

- Real-time token counting (requires API integration)
- Per-agent token breakdown (single-agent today)
- Cost-in-dollars calculation

## 8. New Abstraction

`TokenRecord(block_id, phase, tok_estimated, tok_actual, delta, date, missing)` dataclass. `TokenTracker.load(arch_root)` → list[TokenRecord]. `TokenTracker.report(records)` → markdown string.
