---
id: block-117
phase: phase-19
tier: M
status: done
actual_duration_hours: 1.0
duration_source: estimated
tok_actual: 5500
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 117 Retrospective — adr_drafter.py Core

## 1. What was built

- `sdk/adr_drafter.py`: `AdrDrafter.generate()` from synthesis data dict or list
- `_make_slug()`: title to kebab-case slug (max 50 chars)
- `_unique_path()`: collision-safe file naming with counter suffix
- `_render_adr()`: full ADR-auto template populated from decision dict
- `_update_adr_index()` / `_rebuild_index()`: append-only + full-rebuild for governance/adrs/index.md
- `design/adrs/.gitkeep`: directory initialized
- CLI: `--synthesis`, `--rebuild-index`, `--dry-run` flags
- `sdk/tests/test_adr_drafter.py`: 17 tests

## 2. Gates

- tests-pass: 565 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Synthesis input accepts both list-of-decisions or `{"decisions": [...]}` dict (flexible)
- No-overwrite: `_unique_path()` adds counter suffix; original file untouched
- Index is append-only during generation; `--rebuild-index` replaces full rebuild when needed

## 4. DX updated

`sdk/adr_drafter.py` created. `design/adrs/` directory initialized.
