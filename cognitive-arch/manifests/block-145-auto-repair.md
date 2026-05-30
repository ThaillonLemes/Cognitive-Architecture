---
id: block-145
tier: M
kind: implementation
phase: phase-25
scope: phase-bound
status: pending
security: false
dependencies:
  - block-144
files:
  read:
    - sdk/invariant_check.py
    - sdk/integrity_check.py
    - commands/integrity-bump.md
  modify:
    - sdk/invariant_check.py
  create:
    - sdk/tests/test_invariant_repair.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: dry-run-default-no-writes
    type: command
    command: python sdk/invariant_check.py --arch-root . --repair
    expect: "exits 0; prints planned repairs prefixed DRY-RUN; .integrity.lock + proposals/index.md byte-identical afterward"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-145-auto-repair.md]
created_at: 2026-05-30
---

# Block 145 — Safe auto-repair (INV1 / INV4 / INV6)

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Add a `repair` fn to the mechanically-fixable invariants — INV1 (lock
incompleteness), INV4 (reporting), INV6 (proposals index reconcile) — via a
`--repair` flag that is **dry-run by default**, writing only under `--apply`.
Every applied write backs up to `_backups/`. All other invariants HALT.

## 2. Dependencies

- `block-144` (done) — `Invariant.repair` field + engine exist.

## 3. Files

- **Read:** `sdk/invariant_check.py` (registry + engine to extend),
  `sdk/integrity_check.py` (`regenerate` for INV1 staging),
  `commands/integrity-bump.md` (the human gate INV1 must respect).
- **Modify:** `sdk/invariant_check.py` — populate `repair` for INV1/INV4/INV6;
  add `run_repairs(arch_root, apply: bool) -> list[str]`; add `--repair` /
  `--apply` to `__main__`; add `_backup(path, arch_root)` writing to
  `_backups/<rel>.<ts>` before any mutating write.
- **Create:** `sdk/tests/test_invariant_repair.py` — dry-run leaves files
  byte-identical; `--apply` fixes INV6/INV4 and creates a backup; INV1 on
  immutable drift stages (never silently edits) the lock.

Repair semantics:

- **INV1** (lock incompleteness): the lock is itself `protection: immutable`
  per `integrity-bump.md`, so repair NEVER rewrites it silently. `--apply`
  stages the regenerated lock to `_backups/.integrity.lock.proposed` and prints
  the exact `integrity-bump` instruction (`python sdk/integrity_check.py
  --regenerate`) for the human gate. Dry-run prints the same instruction only.
- **INV4** (runner-not-in-registry): repair is **report-only** — emits the
  missing-id line and the registry-entry stub to add; never edits the registry
  (a real tool entry needs name/command/interval a human supplies). This is the
  "INV4 report" required by the phase doc.
- **INV6** (proposals index): reconcile both directions — append a row for any
  orphan `proposals/*.md` file, and flag (do not delete) index rows whose file
  is missing. Backs up `proposals/index.md` to `_backups/` before writing under
  `--apply`.
- **All others (INV2/INV3/INV5):** no `repair` → `run_repairs` reports
  "HALT — manual fix required (see block-147 / block-close)".

## 4. Validation

- `python -m pytest sdk/tests/ -q` passes.
- Dry-run (`--repair` without `--apply`) on the real root leaves `.integrity.lock`
  and `proposals/index.md` byte-identical (test compares before/after hashes).
- `--apply` on a tmp root with an orphan proposal file appends exactly one index
  row and writes one `_backups/` copy of the prior index.
- INV1 `--apply` on a tmp root with a missing immutable lock entry writes
  `_backups/.integrity.lock.proposed` and prints the integrity-bump command —
  and leaves the real `.integrity.lock` untouched.

## 5. Gates

Declared in frontmatter: tests-pass, dry-run-default-no-writes (the safety
invariant — `--repair` alone mutates nothing), files-updated.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Auto-repair silently edits an immutable file | High | INV1 never writes the lock; it stages `.proposed` + prints the integrity-bump command. The lock is the ONLY immutable file any repair touches, and it goes through the human gate. |
| `--apply` clobbers a file with no recovery | High | `_backup()` copies the target to `_backups/<rel>.<ts>` before every mutating write; dry-run is the default so `--apply` is always deliberate. |
| INV6 deletes a pending row whose file moved | Med | Reconcile never deletes — missing-file rows are flagged for a human; only orphan files get a row appended. |
| `_backups/` accumulates cruft | Low | Timestamped filenames; pruning is out of scope (later block if needed). |

## 7. Out of Scope

- Repairs for INV2 (missing retro), INV3 (tier), INV5 (state pointer) — they HALT
  (block-147 backfills INV2 by hand).
- Auto-running `integrity-bump` (it stays human-gated, by design).
- Pruning / rotating `_backups/`.
- Wiring repair into session_start or block-close — block-146.

## 8. New Abstraction

None. Reuses the `Invariant.repair` field defined in block-144 and
`integrity_check.regenerate`. `_backup()` is a 3-line helper, not a new
abstraction (single caller pattern, below Rule-of-Three).
