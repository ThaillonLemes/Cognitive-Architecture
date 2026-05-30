---
id: block-142
phase: phase-24
tier: M
kind: refactor
status: pending
files:
  read:
    - sdk/audit.py
    - CLAUDE.md
    - INDEX.md
    - _syntax.md
  modify:
    - sdk/audit.py
    - CLAUDE.md
    - INDEX.md
  create:
    - sdk/tests/test_hot_set.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: syntax-absent-from-hot-lists
    type: command
    command: python -c "import sys; sys.path.insert(0,'sdk'); import audit; print('_syntax.md' in audit.SIZE_BUDGETS, '_syntax.md' in __import__('inspect').getsource(audit.print_token_estimates))"
    expect: '"False False" — _syntax.md absent from both the size-budget map and the token-estimate list'
  - name: integrity-verify-all-ok
    type: command
    command: python sdk/integrity_check.py --verify --arch-root .
    expect: 'all-OK; _syntax.md hash matches .integrity.lock (bytes unchanged); no MISMATCH'
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-142-hot-set-correct.md]
created_at: 2026-05-30
---

# Block 142 — HOT-set correction: reclassify _syntax.md to WARM

- **Tier:** M
- **Kind:** refactor
- **Status:** pending
- **Parallel-with:** block-140, block-141 (different files)

## 1. Purpose

`_syntax.md` (~1412 tok) is counted and budgeted as HOT, but it is never a mandatory
boot read — `session_start.py` parses STATE programmatically, and the read-order only
needs `_syntax` when *writing* AI-only files. This block aligns measurement with
reality: remove `_syntax.md` from BOTH HOT lists in `sdk/audit.py` (the `SIZE_BUDGETS`
map AND the `print_token_estimates` list) and from the `CLAUDE.md` boot read-order,
keeping a one-line hot pointer in `INDEX.md`/`CLAUDE.md` so it stays one hop away.
`_syntax.md` bytes are NOT touched (integrity lock stays green). This is the phase's
one judgment call — flagged for review.

## 2. Dependencies

None. `sdk/audit.py`, `CLAUDE.md`, `INDEX.md` are mutable; `_syntax.md` is immutable
(in `.integrity.lock`) and is reclassified, not edited.

## 3. Files

- **Read:** `sdk/audit.py` (the two HOT lists: `SIZE_BUDGETS` ~L95–102 and the list in
  `print_token_estimates` ~L359; `HOT_FILES` in check 1 is existence-only, out of
  scope), `CLAUDE.md` (read-order line referencing `_syntax.md`), `INDEX.md` (HOT table
  lists `_syntax.md`), `_syntax.md` (confirm bytes; do not edit).
- **Modify:** `sdk/audit.py` (drop `"_syntax.md"` from `SIZE_BUDGETS` AND from the
  `print_token_estimates` list — both, so token total and budget agree), `CLAUDE.md`
  (remove `_syntax.md` from the numbered HOT read-order; keep the inline
  `(AI-only; see _syntax.md)` pointer on the STATE line as the on-demand hot pointer),
  `INDEX.md` (move the `_syntax.md` row from the HOT table to WARM, brief noting
  "on-demand: vocabulary for AI-only files").
- **Create:** `sdk/tests/test_hot_set.py` (asserts `_syntax.md` is NOT in
  `audit.SIZE_BUDGETS` and NOT in the `print_token_estimates` source list, and that
  CLAUDE.md's HOT read-order no longer numbers `_syntax.md` as a boot read).

## 4. Validation

- `python -m pytest sdk/tests/ -q` → 0 failed (includes new `test_hot_set.py`).
- `python sdk/integrity_check.py --verify --arch-root .` → all-OK: `_syntax.md` hash
  still equals the lock (no byte changed); audit check 10 stays green.
- `python sdk/audit.py --arch-root .` → PASS; `print_token_estimates` no longer lists
  `_syntax.md` (HOT total drops ~1412 tok) and check 2 no longer budgets it; check 3
  still resolves the `_syntax.md` pointer from INDEX/CLAUDE (one hop, no DOC-DRIFT).

## 5. Gates

Frontmatter: tests-pass, syntax-absent-from-hot-lists, integrity-verify-all-ok,
files-updated. The audit-set edit is paired with the CLAUDE.md read-order edit in THIS
block so protocol and measurement stay in sync (not metric-gaming).

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Reclassifying loses needed syntax context at boot | Med | `_syntax.md` was already a "see also", not a mandatory read; session_start parses STATE in code. Hot one-line pointer in INDEX + CLAUDE keeps it one hop away when writing AI-only files. Judgment call — flagged for review. |
| Editing audit HOT lists looks like gaming the metric | Med | Paired with the matching CLAUDE.md read-order change in the same block; the genuine content cuts are blocks 140/141. |
| Accidentally editing `_syntax.md` bytes (integrity break) | Low | Block does not modify `_syntax.md`; integrity-verify gate fails loudly on any byte drift. `HOT_FILES` (check 1) intentionally keeps `_syntax.md` — that list is existence-only, not a cost list (see §7). |

## 7. Out of Scope

- Removing `_syntax.md` from `HOT_FILES` (check 1, existence-only — not a cost list).
- Editing `_syntax.md` contents or regenerating `.integrity.lock` (immutable;
  reclassify only — no immutable file changes, so no bump needed).
- Re-classifying any other HOT file (INDEX split is block-140; STATE dedup is block-141).

## 8. New Abstraction

None. The change edits two existing lists and one read-order; `test_hot_set.py`
reuses the standard pytest+import pattern already in `sdk/tests/`.
