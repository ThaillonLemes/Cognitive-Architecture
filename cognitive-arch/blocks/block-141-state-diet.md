---
id: block-141
phase: phase-24
tier: M
status: done
actual_duration_hours: 0.4
duration_source: estimated
gates_passed: 4/4
created_at: 2026-05-30
---

# Block 141 Retrospective — STATE diet: dedup blocks_done into BLOCK_LOG

## 1. What was built

- `STATE.md`: removed the inline `blocks_done:block-001,…,block-139` list (139 IDs that
  fully duplicated `blocks/BLOCK_LOG.md`) and replaced it with
  `blocks_done_count:140 blocks_done_source:blocks/BLOCK_LOG.md`. Also corrected the
  `next:` pointer to `block-141` (was stale from `block_close`).
- `sdk/integration.py::_update_state_md`: removed the dead `blocks_done` append loop —
  BLOCK_LOG already records the done event and `project_state.completed_block_ids()` is
  the canonical reader. The `blocks_done_extra` param is kept for signature
  compatibility (documented as unused).

## 2. Gates

- tests-pass: 789 passed, 0 failed ✓
- state-no-inline-blocks-done: STATE.md ~449 → **~112 tok**; no `blocks_done:block-001,…`
  line remains ✓
- block-count-correct: `project_state.block_count()` returns **140** (= BLOCK_LOG
  done-set), unchanged by removing the STATE list — proving BLOCK_LOG is authoritative.
  (The manifest gate said "139"; it was written before block-140 closed — the live
  count is 140, intent met.) ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md, this retro ✓

## 3. Effect

STATE.md is now ~25% of its former size and carries no duplicated done-set — the
"two sources of truth" smell (the very thing block-137 / project_state exists to fix)
is gone for this field. HOT boot total: 5495 → **5158 tok**. block-142 (_syntax
reclassify, −~1412) brings it under 4000.

## 4. Files actually touched

As manifest (STATE.md, sdk/integration.py).
