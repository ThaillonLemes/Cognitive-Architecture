---
id: block-147
tier: M
kind: gate
phase: phase-25
scope: phase-bound
status: pending
security: false
dependencies:
  - block-146
files:
  read:
    - sdk/invariant_check.py
    - blocks/BLOCK_LOG.md
  modify:
    - blocks/block-085-project-memory-layers.md
    - .integrity.lock
  create:
    - sdk/tests/test_invariant_realroot.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: realroot-zero-critical
    type: command
    command: python sdk/invariant_check.py --arch-root . --strict
    expect: "exits 0; 0 critical violations (warns allowed); prints final 'CRITICAL: 0'"
  - name: integrity-verify-ok
    type: command
    command: python sdk/integrity_check.py --verify --arch-root .
    expect: "All immutable files verified OK (0 MISSING / MISMATCH)"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-147-backfill-verify.md]
created_at: 2026-05-30
---

# Block 147 — Backfill real drift to 0 critical + regression tests

- **Tier:** M
- **Kind:** gate
- **Status:** pending

## 1. Purpose

Run the checker on the real arch-root, then backfill or document every CRITICAL
violation until the strict run reports **0 critical** (phase-25 exit criterion 5).
Known criticals: INV2 (`block-085` in BLOCK_LOG, no retro file) and INV1
(immutable files missing from `.integrity.lock`). A regression test pins the
real root at 0 critical so future drift is caught.

## 2. Dependencies

- `block-146` (done) — gate wired; `run_all` / strict mode exist.

## 3. Files

- **Read:** `sdk/invariant_check.py` (run it against `.`), `blocks/BLOCK_LOG.md`
  (confirms `block-085 done` has no retro — the INV2 drift).
- **Modify:**
  - `blocks/block-085-project-memory-layers.md` — **create the missing retro**
    (slug matches `manifests/block-085-project-memory-layers.md`) as a minimal
    reconstructed retro (per phase-25 §5 risk note): frontmatter
    `duration_source: unknown`, `actual_duration_hours:` left blank/0, a one-line
    "reconstructed at block-147; original retro never written" note. Alternative
    if the human prefers: document it as an ACCEPTED gap and whitelist block-085
    in INV2 with a written rationale (default is reconstruct).
  - `.integrity.lock` — regenerate via the human integrity-bump gate
    (`integrity-bump.md`) so all `protection: immutable` files are locked,
    clearing INV1. (This is the one immutable-adjacent write, and it goes through
    the approved bump command, recorded in the governance log — never a silent edit.)
- **Create:** `sdk/tests/test_invariant_realroot.py` — asserts
  `invariant_check.run_all(REAL_ROOT)` yields 0 `severity == "critical"`
  violations (warns permitted); a focused test that block-085 now has a retro
  resolvable by `project_state` + INV2.

Total modify+create = 3 (well under 8).

## 4. Validation

- `python sdk/invariant_check.py --arch-root . --strict` exits 0 with `CRITICAL: 0`
  (warns from INV3/INV4/INV6 are allowed and listed).
- `python sdk/integrity_check.py --verify --arch-root .` reports all immutable
  files OK (INV1 cleared) after the integrity-bump.
- `python -m pytest sdk/tests/ -q` passes, including the new real-root regression.
- The block-085 retro is parseable: `project_state.completed_block_ids` ∩ the
  retro glob now covers block-085 (INV2 clean for it).

## 5. Gates

Declared in frontmatter: tests-pass, realroot-zero-critical (the phase exit
gate), integrity-verify-ok (INV1 cleared via bump), files-updated.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Reconstructed block-085 retro fabricates history | Med | Marked `duration_source: unknown`, duration blank, with an explicit "reconstructed" note — it documents the gap rather than inventing metrics; the alternative (accepted-gap whitelist) is offered for the human to choose. |
| Regenerating `.integrity.lock` edits an immutable file | High | Done ONLY through `commands/integrity-bump.md` (human-approved `--regenerate`), with the approval logged. Not a silent or auto repair. |
| A hidden 3rd critical surfaces on the real root | Med | The strict run enumerates ALL criticals; each is backfilled or documented before the gate passes — the gate is the definition of done, so an unexpected critical simply fails it until handled. |
| Real-root regression test goes stale as blocks are added | Low | The test reads the live root, so it tracks new blocks automatically; it asserts a property (0 critical), not a fixed list. |

## 7. Out of Scope

- Clearing WARN-severity violations (INV3 tier gaps, INV4 advisory, INV6) —
  warns are allowed; only criticals gate this block.
- Backfilling retros for blocks other than the criticals the checker reports.
- Editing detection thresholds beyond an explicit, documented block-085 whitelist
  if the human picks the accepted-gap path.
- Pruning `_backups/` produced by any repair runs.

## 8. New Abstraction

None. This is a gate block: it runs the block-144 checker, backfills data, and
adds a regression test. No new code abstraction is introduced.
