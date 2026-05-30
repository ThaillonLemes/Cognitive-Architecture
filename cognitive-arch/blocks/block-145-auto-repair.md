---
id: block-145
phase: phase-25
tier: M
status: done
actual_duration_hours: 0.8
duration_source: estimated
gates_passed: 3/3
created_at: 2026-05-30
---

# Block 145 Retrospective — Safe auto-repair (dry-run + backups)

## 1. What was built

- `sdk/invariant_schema.py`: new `RepairAction(invariant_id, kind, description,
  requires_human, applied, details, backup_path)`; `REPAIR_KINDS = (apply, stage,
  manual, halt, noop, failed)`.
- `sdk/invariant_check.py`: `repair_all(arch_root, *, apply=False)` (dry-run by
  default), `_backup()` (copies to `_backups/<file>.<stamp>.bak` before any write,
  content-hash stamp since clock/random are unavailable), `--repair`/`--apply` CLI.
  Each repair wrapped so a failure degrades to `kind="failed"`, never raises.
- `sdk/tests/test_invariant_repair.py` — 20 tests.

## 2. Per-invariant repair disposition (safety first)

| INV | Kind | Behavior |
|-----|------|----------|
| INV6 | **apply** | Appends a missing `proposals/index.md` row (backs up first); flags, never deletes, ghost rows. The only safe auto-fix. |
| INV1 | **stage** | NEVER writes `.integrity.lock` (bypasses the human bump). Emits the `integrity_check --regenerate` command + missing list; under `--apply` stages `.integrity.lock.proposed`. |
| INV4 | **stage** | Emits a `tools-registry.yaml` stub; never auto-writes the guarded registry. |
| INV2/INV3 | **manual** | Describes the hand fix (backfill retro / add tier). |
| INV5 | **halt** | STATE/NEXT are human-owned. |

## 3. Gates

- tests-pass: 839 passed, 0 failed (20 new) ✓
- repair-dry-run-clean: `--repair` exits 0, prints planned actions, writes nothing;
  real-root run = 0 applied / 1 staged (INV1) / 2 manual (INV2,INV3); no `_backups/` created ✓
- immutable-safety: test proves `.integrity.lock` byte-identical after `repair_all(apply=True)`,
  and INV6 `--apply` creates the backup before appending ✓

## 4. Why this matters

The architecture can now *fix* the drift it detects — but only where it is provably
safe. Immutable files and guarded files are staged behind the human integrity-bump,
never silently edited. This is the guardrail that makes Phase 27's self-modification
trustworthy: repairs are reversible (backup-first) and never bypass the human gate.

## 5. Files actually touched

As manifest (sdk/invariant_schema.py, sdk/invariant_check.py modified; sdk/tests/test_invariant_repair.py created).
