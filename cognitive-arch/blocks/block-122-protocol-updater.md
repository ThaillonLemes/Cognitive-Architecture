---
id: block-122
phase: phase-20
tier: M
status: done
actual_duration_hours: 1.0
duration_source: estimated
tok_actual: 5200
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 122 Retrospective — protocol_updater.py

## 1. What was built

- `sdk/protocol_updater.py`: `ProtocolUpdater.run(dry_run, threshold)` generates proposals from patterns.md
- `_parse_patterns_md()`: parses markdown pattern sections into structured dicts
- `_make_proposal_id()`: deterministic ID (date + pattern slug) for dedup
- `_already_proposed()`: glob-based existence check — prevents duplicates
- `_render_proposal()`: full proposal.md content with heuristic target_file suggestion
- `_update_proposals_index()`: append-only governance/proposals/index.md updates
- `sdk/session_start.py`: `run_protocol_updater` added to TOOL_RUNNERS
- `sdk/tests/test_protocol_updater.py`: 15 tests

## 2. Gates

- tests-pass: 591 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- `global` statement removed (Python 3.13 syntax error); threshold passed as parameter to `run()`
- `_already_proposed()` uses glob pattern `*-<slug>.md` — detects across any date prefix
- Target file suggestion is heuristic (pattern name keywords) — human always overrides

## 4. DX updated

`sdk/protocol_updater.py` created. `sdk/session_start.py` extended with `run_protocol_updater`.
