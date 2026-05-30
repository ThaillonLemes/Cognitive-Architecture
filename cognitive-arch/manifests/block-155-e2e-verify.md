---
id: block-155
tier: M
kind: gate
phase: phase-27
scope: phase-bound
status: pending
security: true
dependencies:
  - block-154
files:
  read:
    - sdk/proposal_apply.py
    - governance/proposals/index.md
  modify: []
  create:
    - sdk/tests/test_apply_e2e.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: audit-pass
    type: command
    command: python sdk/audit.py --arch-root .
    expect: "PASS, 0 errors"
  - name: integrity-all-ok
    type: command
    command: python sdk/integrity_check.py --verify --arch-root . --strict
    expect: "All immutable files verified OK (exit 0); no immutable file modified without a recorded bump"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-155-e2e-verify.md]
created_at: 2026-05-30
---

# Block 155 — End-to-end demo (apply + forced rollback) + verify

- **Tier:** M
- **Kind:** gate
- **Status:** pending
- **Parallel-with:** none (capstone, group 27C)

## 1. Purpose

Prove the whole pipeline on real inputs: take one accepted proposal against a
**non-immutable** target through the apply path (write + tests pass + status
`applied` + log + ADR), and a forced-failure case through the rollback path
(byte-identical restore + `apply-failed`). Close the phase with a green suite,
`audit.py` PASS, and the integrity lock all-OK.

## 2. Dependencies

- `block-154` — full `apply()` with rollback + provenance (must be `done`).

## 3. Files

- **Read:** `sdk/proposal_apply.py` (the pipeline under test),
  `governance/proposals/index.md` (the real accepted proposals).
- **Modify:** none.
- **Create:** `sdk/tests/test_apply_e2e.py`.

## 4. Validation

- All tests pass: `python -m pytest sdk/tests/ -q` (0 failed).
- **Apply path (non-immutable target):** the two repo-accepted proposals both
  target immutable files (`scope-expansion-recurring` →
  `templates/manifest-medium.md`; `gate-failures-recurring` →
  `protocols/block-close-checklist.md` — both `protection: immutable`). So the
  e2e apply test builds a fixture accepted proposal whose `target_file` is a
  **non-immutable** real file —
  `protocols/block-complexity-estimator.md` (or `governance/token-budget.md`) —
  inside a `tmp_path` copy of the arch root, runs `apply()`, and asserts: target
  changed as the diff specified, proposal status `applied`, a governor-log entry
  and an `ADR-*` stub were created.
- **Rollback path:** a second fixture proposal whose diff deliberately breaks a
  test; `apply()` must restore the target byte-identical, set `apply-failed`,
  retain the backup, and leave the suite green afterward.
- **Immutable refusal regression:** asserts `apply()` on the real
  `2026-05-29-scope-expansion-recurring` (immutable target, no bump) is refused
  with no write — guarding the phase invariant end-to-end.
- Tests run against an isolated `tmp_path` clone so the live repo's protocol
  files and proposal statuses are never mutated by the suite.

## 5. Gates

Front-matter: `tests-pass` (full suite green); `audit-pass` (`sdk/audit.py`
PASS, 0 errors — Exit Criterion 6); `integrity-all-ok` (lock verifies, proving
no immutable file was modified without a recorded bump); `files-updated`. These
four together satisfy phase-27 Exit Criteria 5 and 6.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| E2E mutates the live repo (real proposals/targets) and dirties the tree | High | All apply/rollback runs operate on a `tmp_path` copy of the arch root; the live repo is read-only to the test. |
| Chosen non-immutable target later gains `protection: immutable`, breaking the test | Med | Test asserts `not _is_immutable(target)` first and skips with a clear message if so; pick `block-complexity-estimator.md`, currently non-immutable (verified at authoring). |
| Forced-failure fixture is flaky (test it breaks is reordered/removed) | Med | The breaking diff targets a dedicated fixture file with its own asserting test in the temp clone, not a real `sdk/tests/` file. |
| `audit.py` surfaces unrelated pre-existing warnings | Low | Gate expects PASS/0 errors on the current tree; any pre-existing failure is fixed or scoped out before close (block-close checklist). |

## 7. Out of Scope

- New apply/guard/rollback logic — 155 only exercises and verifies 152–154.
- Applying against a real immutable target with a real bump (the refusal
  regression is sufficient; a live bump stays a human action).
- Demonstrating multi-file or cross-repo proposals (phase §10).
- CI wiring of the e2e test beyond `sdk/tests/` (already covered by the suite).

## 8. New Abstraction

None. Tests-only block; reuses `ProposalApply` and `proposal_resolver._is_immutable`.
