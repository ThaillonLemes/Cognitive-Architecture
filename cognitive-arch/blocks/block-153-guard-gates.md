---
id: block-153
phase: phase-27
tier: M
status: done
actual_duration_hours: 0.8
duration_source: estimated
gates_passed: 3/3
created_at: 2026-05-30
---

# Block 153 Retrospective — Guard gates (immutability + integrity + backup + sanity)

## 1. What was built

- `sdk/proposal_apply.py`: `check_guards(proposal_id, arch_root) -> GuardResult(allowed,
  target_file, reasons, backup_plan)` — evaluate-only (writes nothing). Four guards:
  1. **Acceptance** — non-accepted proposal → refused (short-circuits).
  2. **Immutability** — immutable target → REFUSED unless an `INTEGRITY BUMP APPROVED`
     block in `governor-log.md` names the file (`_has_integrity_bump`). Unrelated bump
     doesn't clear it.
  3. **Integrity** — locked target must `integrity_check.verify` clean; pre-existing
     MISMATCH blocks apply.
  4. **Structural sanity** — would-be post-change content must be valid: `.py` must
     `compile()`; `.md` must keep balanced frontmatter.
  Plus `_backup(target)` → `_backups/<file>.<contenthash>.bak` (block-154 calls it).
  `check_guards` never raises (fail-safe REFUSED on error).

## 2. Gates

- tests-pass: 993 passed, 0 failed (28 new) ✓
- refuses-immutable: real-root `--check-guards 2026-05-29-scope-expansion-recurring` →
  **REFUSED** (immutable target, no bump), exit 0 ✓
- no-immutable-touched: `integrity_check --verify --strict` 17/17 OK; nothing applied ✓

## 3. Why this matters (security)

This is the wall that makes self-modification safe: an immutable protocol file can NOT be
auto-modified without a recorded human integrity-bump, a locked file with drift is refused,
and any change that would corrupt structure (unparseable .py, broken frontmatter) is
blocked BEFORE a byte is written. block-154 may only apply what passes these guards.

## 4. Files actually touched

`sdk/proposal_apply.py` modified; `sdk/tests/test_apply_guards.py` created.
