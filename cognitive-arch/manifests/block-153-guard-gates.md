---
id: block-153
tier: M
kind: implementation
phase: phase-27
scope: phase-bound
status: pending
security: true
dependencies:
  - block-152
files:
  read:
    - sdk/proposal_apply.py
    - sdk/proposal_resolver.py
    - sdk/integrity_check.py
    - commands/integrity-bump.md
  modify:
    - sdk/proposal_apply.py
  create:
    - sdk/tests/test_apply_guards.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: immutable-refused
    type: command
    command: python sdk/proposal_apply.py --arch-root . --proposal 2026-05-29-scope-expansion-recurring
    expect: 'exits non-zero; message names immutable target + integrity-bump; no write, no backup'
  - name: integrity-all-ok
    type: command
    command: python sdk/integrity_check.py --verify --arch-root . --strict
    expect: "All immutable files verified OK (exit 0)"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-153-guard-gates.md]
created_at: 2026-05-30
---

# Block 153 — Guard gates: immutability + integrity + backup + sanity

- **Tier:** M
- **Kind:** implementation
- **Status:** pending
- **Parallel-with:** none (precedes 154 in group 27B)

## 1. Purpose

Insert the guard layer between diff generation (152) and any write: refuse an
immutable `target_file` unless a recorded integrity-bump satisfies the lock,
back the target up to `_backups/` before touching it, and run a structural
sanity check on the would-be result. Enforces the phase invariant *no immutable
file modified without a recorded integrity-bump*.

## 2. Dependencies

- `block-152` — `proposal_apply.py` with `build_diff` (must be `done`).

## 3. Files

- **Read:** `sdk/proposal_apply.py` (extend), `sdk/proposal_resolver.py`
  (reuse `_is_immutable`), `sdk/integrity_check.py` (`load_lock`, `verify`,
  `LOCK_FILE`, `find_immutable_files`), `commands/integrity-bump.md` (the human
  gate + `INTEGRITY BUMP APPROVED` block format).
- **Modify:** `sdk/proposal_apply.py` — add `check_guards(proposal_id) ->
  (ok, reason)` and `backup_target(path) -> Path`.
- **Create:** `sdk/tests/test_apply_guards.py`.

## 4. Validation

- All tests pass: `python -m pytest sdk/tests/ -q` (0 failed).
- **Immutability guard:** if `proposal_resolver._is_immutable(target, root)` is
  True, `check_guards` refuses UNLESS the lock verifies clean for that file AND
  a matching `INTEGRITY BUMP APPROVED` entry naming the file exists in
  `governance/governor-log.md`. Refusal returns a clear message and writes
  nothing.
- **Integrity gate:** reuse `integrity_check.verify(root)`; if the locked entry
  for the target is `MISMATCH`/`MISSING`, refuse (drift must be resolved via
  `commands/integrity-bump.md`, not auto-bumped here).
- **Backup:** `backup_target` copies the target to
  `_backups/<relpath>.<UTC-timestamp>.bak` (parents created); returns the path;
  byte-identical to source (`shutil.copy2`).
- **Sanity check:** the post-edit text is non-empty, still valid UTF-8, retains
  any `protection:`/front-matter header it began with, and (for `.md`) does not
  drop the H1. Failure → refuse, no write.
- Tests: immutable target without bump → refused; immutable target WITH a
  forged bump entry + clean lock → passes guard (no write yet); non-immutable
  target → passes guard and produces a backup; sanity check rejects an edit
  that empties the file or strips the header.

## 5. Gates

Front-matter: `tests-pass`; `immutable-refused` (real immutable-targeted
proposal is refused with the right message, no write/backup); `integrity-all-ok`
(`integrity_check --verify --strict` stays green — this block must not mutate
any immutable file); `files-updated`.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Guard parses governor-log too loosely and accepts a stale/unrelated bump | High | Match an `INTEGRITY BUMP APPROVED` block whose `file:` equals the target relpath AND require `integrity_check.verify` clean for it; test asserts an unrelated bump is rejected. |
| `_backups/` accumulates unbounded copies | Low | Timestamped names are append-only by design; pruning is ops, not apply. `_backups/` added to `.gitignore` (within create budget via test-only touch; documented in §7). |
| Sanity check too strict → blocks legitimate appends | Med | Checks are minimal-invariant (non-empty, UTF-8, header/H1 retained); the append strategy from 152 cannot violate them, so the happy path is unaffected. |
| Reusing `_is_immutable` couples apply to resolver internals | Low | Acceptable: single source of truth for immutability (phase invariant); re-implementing would risk divergence. |

## 7. Out of Scope

- Performing the write, running tests, rollback, or status change (block 154).
- Auto-running `integrity_check --regenerate` (the bump stays human, per
  `commands/integrity-bump.md`).
- A `.gitignore` rewrite beyond ensuring `_backups/` is ignored.
- Diff generation changes (block 152 owns `build_diff`).

## 8. New Abstraction

None. Adds `check_guards` / `backup_target` methods to the existing
`ProposalApply` class; immutability and lock logic are reused from
`proposal_resolver` and `integrity_check`, not re-created.
