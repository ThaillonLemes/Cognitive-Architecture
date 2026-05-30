---
id: block-147
phase: phase-25
tier: M
status: done
actual_duration_hours: 0.7
duration_source: estimated
gates_passed: 3/3
created_at: 2026-05-30
---

# Block 147 Retrospective — Backfill real drift to 0 critical + regression test

## 1. What was built

- **Root-cause fix in `sdk/integrity_check.py`:** `find_immutable_files` now matches
  `protection: immutable` ONLY as a YAML frontmatter field (new `_frontmatter_block()`
  + `is_immutable_text()` with a MULTILINE field regex), not as a prose substring. Files
  that merely *discuss* the phrase (this session's manifests, phase-25.md, retros) are no
  longer miscounted as immutable.
- `governance/known-drift.md`: documents the 29 remaining WARNs as accepted/historical —
  INV2 (blocks 061-085 done without a retro, pre-template era) and INV3 (blocks 108-111
  no resolvable tier). Not fabricated into fake retros.
- `sdk/tests/test_integrity_check.py` (16 tests): prose mention NOT counted; real
  frontmatter tag IS (quoted/commented/BOM variants).
- `sdk/tests/test_invariant_realroot.py` (5 tests): the permanent Phase-25 exit guard —
  `run_all(REAL_ROOT)` has 0 critical, `gate_result` ok=True.

## 2. Gates

- tests-pass: 871 passed, 0 failed (21 new) ✓
- realroot-zero-critical: `invariant_check --arch-root .` → **Totals: 0 critical, 29 warn** ✓
- integrity-verify: all 17 immutable files OK — lock NOT regenerated, no immutable file modified ✓

## 3. Critical count: 7 → 0

All 7 criticals were INV1 false positives from the loose substring matcher. Fixing the
DETECTION (frontmatter-only) — rather than fabricating retros or regenerating the lock —
cleared them at the root. The 8 genuinely-tagged immutable files are all in the lock;
the lock keeps 9 extra historical entries as a harmless superset (INV1 only requires
detected-immutable ⊆ lock). Pruning them would need the human integrity-bump — deferred.

## 4. Deviation from manifest (intentional)

The manifest proposed fabricating a block-085 retro + regenerating the lock. That was
the wrong fix — the criticals were a detection bug, not a real missing lock entry. Fixed
the matcher instead: no retro fabricated, lock untouched, no immutable file modified.
This is exactly the anti-drift discipline Phase 25 is about — fix the instrument, don't
paper over the symptom.

## 5. Files actually touched

`sdk/integrity_check.py` modified; `governance/known-drift.md`,
`sdk/tests/test_integrity_check.py`, `sdk/tests/test_invariant_realroot.py` created.
