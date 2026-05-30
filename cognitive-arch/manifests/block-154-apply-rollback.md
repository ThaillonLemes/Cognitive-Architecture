---
id: block-154
tier: M
kind: implementation
phase: phase-27
scope: phase-bound
status: pending
security: true
dependencies:
  - block-153
files:
  read:
    - sdk/proposal_apply.py
    - governance/governor-log.md
    - templates/ADR.md
    - sdk/proposal_resolver.py
  modify:
    - sdk/proposal_apply.py
  create:
    - sdk/tests/test_apply_rollback.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: rollback-restores-byte-identical
    type: command
    command: python -m pytest sdk/tests/test_apply_rollback.py -q
    expect: 'forced-failure case restores target byte-for-byte; proposal marked apply-failed; backup retained'
  - name: integrity-all-ok
    type: command
    command: python sdk/integrity_check.py --verify --arch-root . --strict
    expect: "All immutable files verified OK (exit 0)"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-154-apply-rollback.md]
created_at: 2026-05-30
---

# Block 154 — Apply-with-rollback + provenance (log + ADR stub)

- **Tier:** M
- **Kind:** implementation
- **Status:** pending
- **Parallel-with:** none (applies through 153's guards)

## 1. Purpose

Atomically apply a guarded diff, run the test suite + audit, and on ANY failure
auto-restore from the 153 backup — leaving no partial write. Record the outcome:
set the proposal `applied`/`apply-failed`, append a provenance entry to
`governance/governor-log.md`, and drop an ADR stub in `decisions/`. The test
suite is the gate: a change that breaks any test is never kept.

## 2. Dependencies

- `block-153` — `check_guards` + `backup_target` in `proposal_apply.py` (must be
  `done`); apply always passes through guards first.

## 3. Files

- **Read:** `sdk/proposal_apply.py` (extend), `governance/governor-log.md`
  (append format), `templates/ADR.md` (stub shape, sequential `ADR-<NNN>`),
  `sdk/proposal_resolver.py` (reuse `_update_frontmatter_field`,
  `_update_index_status`, `re.sub` of the `**Status:**` line).
- **Modify:** `sdk/proposal_apply.py` — add `apply(proposal_id) ->
  (ok, status)` orchestrating guard → backup → atomic-write → verify → log/ADR,
  with rollback.
- **Create:** `sdk/tests/test_apply_rollback.py`.

## 4. Validation

- All tests pass: `python -m pytest sdk/tests/ -q` (0 failed).
- **Atomic write:** write to `<target>.tmp` then `os.replace` over the target
  (no torn file on crash).
- **Post-apply verify:** run `python -m pytest sdk/tests/ -q` and `sdk/audit.py`
  via `subprocess`; either non-zero → rollback.
- **Rollback:** restore the target from the 153 backup byte-for-byte
  (`shutil.copy2` back, or `os.replace`), confirm equality, then set proposal
  status `apply-failed` and append a `APPLY FAILED` provenance entry. Backup is
  retained on failure; deleted only after a clean verify (phase Risk row).
- **Success path:** set proposal status `applied` (front-matter + index +
  `**Status:**` line via reused resolver helpers); append `APPLY APPLIED`
  provenance to `governor-log.md`; create
  `decisions/ADR-<next>-apply-<proposal-slug>.md` from `templates/ADR.md` with
  `status: accepted`, `context_phase: phase-27`, `context_block: block-154`,
  and the proposal rationale in §1.
- Tests: a passing synthetic diff → status `applied`, log + ADR present, backup
  cleaned; a deliberately-breaking diff (e.g. injects a line that fails a
  test) → rollback restores byte-identical, status `apply-failed`, log entry
  present, target unchanged from pre-apply.

## 5. Gates

Front-matter: `tests-pass`; `rollback-restores-byte-identical` (the forced
failure path is explicitly exercised — restore + `apply-failed` + retained
backup); `integrity-all-ok` (no immutable file mutated by this block);
`files-updated`. ADR numbering continues from the current max (ADR-005 → ADR-006).

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Rollback itself fails, leaving partial state | High | Atomic `os.replace` for both write and restore; backup retained until a clean post-verify; a test forces the failure path and asserts byte-identical restore. |
| Post-apply verify recursively re-runs apply (infinite loop) | Med | Verify runs `pytest`/`audit` only — never `proposal_apply`; e2e (155) drives apply exactly once. |
| Subprocess test run inherits a broken cwd/encoding on Windows | Med | Invoke with explicit `cwd=arch_root` and `env` carrying `PYTHONIOENCODING`; mirrors the cp1252 smoke-test convention (block-138). |
| ADR number collision under concurrent applies | Low | Compute next index by scanning `decisions/ADR-*.md` at write time; apply is single-flight per proposal (phase §10). |
| governor-log corrupted by a partial append | Low | Append-only via a single `open(..., "a")` write of a fully-formed block; no in-place edits. |

## 7. Out of Scope

- Diff generation (152) and guard/backup creation (153) — reused, not changed.
- Immutable-target applies (still hard-blocked by 153's guard; bump stays human).
- Concurrency / locking across simultaneous applies (one proposal at a time).
- Surfacing applied changes in `health_report.py` (phase §4 marks it optional;
  deferred).

## 8. New Abstraction

None. Adds `apply()` to `ProposalApply`; status mutation reuses
`proposal_resolver` helpers, ADR generation copies `templates/ADR.md`, and the
log append follows the existing `governor-log.md` block format.
