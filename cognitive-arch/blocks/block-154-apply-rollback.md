---
id: block-154
phase: phase-27
tier: M
status: done
actual_duration_hours: 1.0
duration_source: estimated
gates_passed: 3/3
created_at: 2026-05-30
---

# Block 154 Retrospective — Apply-with-rollback + provenance

## 1. What was built

- `sdk/proposal_apply.py`: `apply_proposal(proposal_id, arch_root, *, confirm=False)
  -> ApplyResult(applied, proposal_id, target_file, backup_path, tests_passed,
  rolled_back, reasons)`. Flow: check_guards (refuse → no write) → `confirm=False` dry-run
  → `_backup` first → **atomic write** (temp + `os.replace`) → **verify** (subprocess
  pytest + audit PASS) → on failure **auto-rollback** (atomic restore from backup) → on
  success mark proposal `applied`, append `APPLY APPLIED` to `governor-log.md`, write
  `decisions/ADR-NNN-apply-<slug>.md`. Never raises (exception → rollback).
- `sdk/tests/test_apply_rollback.py` — 25 tests, all on synthetic tmp_path targets.

## 2. Gates

- tests-pass: 1018 passed, 0 failed (25 new) ✓
- rollback-byte-identical: forced-fail verify → target restored byte-identical, proposal
  stays accepted, no ADR (proven via monkeypatch AND a real failing-audit subprocess) ✓
- real-files-untouched: real immutable proposal refused even with `--confirm`; integrity
  17/17 OK; no stray _backups/tmp/ADR in the repo ✓

## 3. Why this matters (the capstone mechanism)

This is guarded self-modification made safe: every apply backs up first, writes atomically,
and is GATED on the full test suite + audit passing — any failure auto-restores the
original. Combined with block-153's guards (immutable refused without a human bump), the
architecture can now change its own non-immutable protocols safely and reversibly, and can
NEVER silently corrupt itself. Acceptance stays human; only the application is automated.

## 4. Files actually touched

`sdk/proposal_apply.py` modified; `sdk/tests/test_apply_rollback.py` created.
