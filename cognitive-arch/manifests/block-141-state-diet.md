---
id: block-141
phase: phase-24
tier: M
kind: refactor
status: pending
files:
  read:
    - STATE.md
    - sdk/project_state.py
    - sdk/session_start.py
    - sdk/audit.py
    - blocks/BLOCK_LOG.md
  modify:
    - STATE.md
    - sdk/integration.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: state-no-inline-blocks-done
    type: command
    command: python sdk/audit.py --arch-root .
    expect: 'STATE.md contains no "blocks_done:block-001,..." inline list; STATE.md token estimate drops from ~449 toward ~120 tok'
  - name: block-count-correct
    type: command
    command: python -c "import sys; sys.path.insert(0,'sdk'); import project_state as p; from pathlib import Path; print(p.block_count(Path('.')))"
    expect: 'prints 139 (matches BLOCK_LOG done-set); unchanged by removing the STATE list'
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-141-state-diet.md]
created_at: 2026-05-30
---

# Block 141 — STATE diet: dedup blocks_done into BLOCK_LOG

- **Tier:** M
- **Kind:** refactor
- **Status:** pending
- **Parallel-with:** block-140, block-142 (different files)

## 1. Purpose

`STATE.md` carries an inline `blocks_done:block-001,…,block-139` list — 139 IDs that
fully duplicate `blocks/BLOCK_LOG.md`, the documented single source of truth for the
done-set (the "two sources" problem Phase 23 / block-137 exists to fix). It is ~330
of STATE's ~449 HOT tokens and drifts every block. This block replaces it with
`blocks_done_count:139` + a `BLOCK_LOG` pointer, and migrates the one piece of code
that touched the list so nothing reads or writes a stale copy.

## 2. Dependencies

block-137 (`sdk/project_state.py` exists and provides `completed_block_ids()` /
`block_count()`, BLOCK_LOG-backed). STATE.md is mutable (not in `.integrity.lock`).

## 3. Files

- **Read:** `STATE.md` (the inline list to remove), `sdk/project_state.py`
  (`completed_block_ids()` / `block_count()` — the canonical replacement reader),
  `sdk/session_start.py` (confirm `_read_state` only reads p/status/last_block/notes
  — NOT blocks_done, so no migration needed there), `sdk/audit.py` (confirm no check
  parses STATE.blocks_done; `print_token_estimates` measures the STATE shrink),
  `blocks/BLOCK_LOG.md` (the source of truth the count must match).
- **Modify:** `STATE.md` (delete `blocks_done:block-001,…` from the state line; add
  `blocks_done_count:139` + a comment pointer to `blocks/BLOCK_LOG.md`),
  `sdk/integration.py` (`_update_state_md` — drop the now-dead `blocks_done` append
  loop; BLOCK_LOG already records the done event, see §4).

## 4. Validation

- Grep proof (done at authoring): the ONLY code touching `blocks_done` is
  `sdk/integration.py::_update_state_md`, which *appends* via
  `re.sub(r"(blocks_done:[^\n]+)", …)`. No code *reads* it for logic —
  `session_start._read_state` reads only p/status/last_block/notes; `audit.py` and
  `project_state` both use `BLOCK_LOG`. `_syntax.md:18` only documents the vocab
  (immutable — untouched).
- After edit the `re.sub` no longer matches → remove that append loop (and the now-
  unused `blocks_done_extra` plumbing); update `test_integration.py` (lines 177/182)
  only if it asserts on the appended list.
- `python -m pytest sdk/tests/ -q` → 0 failed; `project_state.block_count(Path('.'))`
  returns 139 (= BLOCK_LOG done-set), proving the count survives the removal.
- `python sdk/audit.py --arch-root .` → PASS; STATE.md token estimate drops and STATE
  stays a valid AI-only key:value file (check 4 OK — `blocks_done_count:139` is k:v).

## 5. Gates

Declared in frontmatter: tests-pass, state-no-inline-blocks-done, block-count-correct,
files-updated. `block-count-correct` proves BLOCK_LOG remains authoritative after the
dedup; block-143 adds the <4000-tok regression gate.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| A hidden reader parses `STATE.blocks_done` and breaks when removed | Med | Repo-wide grep found only `integration.py` (a writer) + docs; migrate any reader that surfaces to `project_state.completed_block_ids()`. |
| Removing the append loop breaks `_update_state_md` callers / tests | Low | `blocks_done_extra` becomes unused; drop or ignore the param and adjust `test_integration.py` (L177/182); done-event still lands in BLOCK_LOG. |
| `blocks_done_count` drifts from BLOCK_LOG over time | Low | Count is informational; `project_state.block_count()` is the live source — the count is just a convenience mirror. |

## 7. Out of Scope

- Editing `_syntax.md` to retire the `blocks_done:` vocab line (immutable; the
  vocabulary entry can stay as historical/AI-write reference).
- Rewriting historical retro frontmatter that uses `blocks_done:` (phase retros).
- Changing how blocks are appended to BLOCK_LOG (unchanged).
- Splitting any other STATE field (none duplicates BLOCK_LOG like this one does).

## 8. New Abstraction

None. Reuses `project_state.completed_block_ids()` / `block_count()` exactly as
defined in block-137. No new code abstraction introduced.
