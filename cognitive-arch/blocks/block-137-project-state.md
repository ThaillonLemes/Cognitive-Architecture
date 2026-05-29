---
id: block-137
phase: phase-23
tier: M
status: done
actual_duration_hours: 1.2
duration_source: estimated
gates_passed: 3/3
created_at: 2026-05-29
---

# Block 137 Retrospective — project_state.py single source of truth

## 1. What was built

- `sdk/project_state.py`: the canonical reader for "where are we" —
  `current_phase()` (from STATE.md `p:N`), `current_phase_name()`,
  `completed_block_ids()` (deduped, from BLOCK_LOG), `block_count()`,
  `phase_files()` (numeric sort, excludes `-retro`), `current_phase_file()`
- `sdk/tests/test_project_state.py`: 10 tests incl. the lexical-sort regression
- `sdk/health_report.py`: phase section now calls `project_state.current_phase_file()`
  instead of `sorted(glob("phase-[0-9]*.md"))[-1]`; `_parse_block_log()` delegates
  to `project_state.completed_block_ids()` so the header count matches by construction
- `sdk/tests/test_health_report_phase.py`: 3 tests asserting phase >= 22 on the
  real arch-root + header block count == project_state.block_count

## 2. Gates

- tests-pass: 753 passed, 1 xfailed (velocity_inference, see §4), 0 failed ✓
- phase-correct: `health_report.py --arch-root .` reports `Current phase: phase-23` ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Root cause (the lexical-sort bug)

`sorted(glob("phase-[0-9]*.md"))` compares strings, so `"phase-9"` sorts AFTER
`"phase-22"`; `[-1]` then returned phase-9 as "current." The glob also matched
`phase-N-retro.md`. `project_state` sidesteps both: current phase comes from
STATE.md's `p:` field (the canonical record), and `phase_files()` sorts by the
parsed integer and excludes retro files.

## 4. Discovered: block-136 left a crasher alive (deferred to block-138)

The full-suite run surfaced `velocity_inference.py --help` crashing with
`PermissionError: [Errno 13] Permission denied: '.'`. Cause: the tool has no
argparse, so `--help` is treated as a block id, yields an empty `Path("")`
manifest path, and reading it opens the directory `.`. This PermissionError was
named in phase-23 §2 as one of block-136's two target crashers, but block-136
fixed only the UTF-8 + `_find_git_root` bugs and prematurely emptied
`_KNOWN_CRASHERS` while reporting "0 failed." Per user decision, the real fix is
deferred to block-138; here it was re-marked as a known crasher (xfail strict)
purely to restore the green gate. `_KNOWN_CRASHERS` and the file header/reason in
`test_cli_smoke.py` were corrected to say block-138.

## 5. Reconciled stale counters

STATE.md `blocks_done` ended at block-134 and `next:block-135`, though BLOCK_LOG
already had 135 and 136 done — a live instance of the "counters disagree across
sources" problem phase-23 exists to fix. Updated `blocks_done` to include
135/136/137 and `next:block-138`. project_state reads BLOCK_LOG (canonical), so
its count (now 137) is the source of truth.

## 6. DX updated

`sdk/project_state.py` is the canonical "where are we" reader. New/updated tools
should import it rather than re-parsing STATE.md / BLOCK_LOG / phases/ themselves.
Next migrations (out of scope here): dashboard_generator, weekly_report.
