---
id: block-123
phase: phase-20
tier: S
status: done
actual_duration_hours: 0.3
duration_source: estimated
tok_actual: 2100
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 123 Retrospective — session_start Proposals

## 1. What was built

- `sdk/session_start.py`: `_count_pending_proposals(arch_root)` reads `governance/proposals/index.md`, counts rows with `"| pending |"`
- Summary section extended: prints `[PROPOSALS] N pending — see governance/proposals/` (or `0 pending — none to review`)
- Zero-crash guarantee: returns 0 on missing file or OSError

## 2. Gates

- tests-pass: 606 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Count by string match `"| pending |"` — fast, no YAML parsing needed
- Always prints even when 0 — silence would mean proposals are ignored

## 4. DX updated

`sdk/session_start.py` extended with `_count_pending_proposals`.
