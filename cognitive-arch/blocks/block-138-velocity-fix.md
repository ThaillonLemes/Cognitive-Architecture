---
id: block-138
phase: phase-23
tier: M
status: done
actual_duration_hours: 0.9
duration_source: estimated
gates_passed: 4/4
created_at: 2026-05-29
---

# Block 138 Retrospective — Velocity fix (argparse + tier-fallback + confidence label)

## 1. What was built

- `sdk/velocity_inference.py`: argparse with `--help`, `--arch-root`, positional
  `block_id`; new `_is_real_file()` guard rejects `Path("")` and `Path(".")` so
  the empty-manifest path never reaches `read_text()`; `_locate_manifest()`
  factored out so health_report can reuse it.
- `sdk/health_report.py::_collect_velocity_data`: tier source priority is now
  retro frontmatter → manifest fallback. Recovers the 26 blocks (086-111) whose
  retros carry `actual_duration_hours` but no `tier:`. Velocity table renders
  with a new `Source` column showing `MEASURED` (count >= 3) or `ESTIMATED`.
- `sdk/tests/test_cli_smoke.py`: `_KNOWN_CRASHERS` is back to empty; the strict
  xfail on velocity is gone.
- New: `sdk/tests/test_velocity_inference.py` (14 tests — --help exits 0;
  empty/dot/dir Paths rejected; manifest tier read; unknown-block falls back).
- New: `sdk/tests/test_health_report_velocity.py` (6 tests — real arch-root
  surfaces >= 40 measured samples; MEASURED/ESTIMATED labels present; manifest
  fallback unit-tested in isolation; retro tier wins over manifest tier).

## 2. Gates

- tests-pass: 774 passed, 0 failed, 0 xfailed (was 753 + 1 xfailed) ✓
- velocity-help-clean: `python sdk/velocity_inference.py --help` exits 0, no traceback ✓
- velocity-measured-count: rendered report now shows 48 measured samples
  (S=18, M=30) — up from 25; both rows tagged `MEASURED`; L tier (count=0)
  tagged `ESTIMATED` ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md updated ✓

## 3. Root cause

Two independent bugs, both rooted in the same lazy default.

**Bug A — `--help` crasher.** `velocity_inference.py` had no argparse. The CLI
read `sys.argv[1]` as the block_id; for `--help`, no manifest matched, and the
code stored `Path("")` as a sentinel. Inside `_files_from_manifest`,
`Path("").exists()` is `True` on Windows (it resolves to the current directory),
so the guard passed and `read_text()` opened `.` → `PermissionError`. Fix: real
argparse + an `_is_real_file()` helper that rejects empty, dot, and
non-file paths.

**Bug B — silent half-blindness.** `_collect_velocity_data` required both
`tier:` and `actual_duration_hours:` in the retro frontmatter. The 26 retros
written between block-086 (when `actual_duration_hours` was introduced) and
block-111 (when the retro template was updated to include `tier:`) carry the
duration but not the tier — so the collector silently dropped half its samples
and the velocity table reported `INSUFFICIENT DATA` for L and undercounted S/M.
Fix: when retro tier is absent, look it up from the manifest the retro
already references (`manifest:` field) via `velocity_inference._tier_from_manifest`.

## 4. Effect on the velocity table

Before:

| Tier | Count | Source |
|------|-------|--------|
| S | 12 | (no label) |
| M | 13 | (no label) |
| L | 0  | INSUFFICIENT DATA |

After:

| Tier | Count | Source |
|------|-------|--------|
| S | 18 | MEASURED |
| M | 30 | MEASURED |
| L | 0  | ESTIMATED |

Phase-23 exit criterion 5 (velocity surfaces available duration data with an
explicit confidence label) is now met. The remaining work — re-mining patterns
over the full 134-block history and demonstrating the
pattern → recommendation → proposal loop end-to-end — moves to block-139.

## 5. What I'd do differently

The retro template change in block-086 should have been guarded with a smoke
check: "if a retro has actual_duration_hours, it has a tier." The 26 tier-less
retros existed for 25 blocks before anyone noticed. The fallback fixes the
symptom; a retro frontmatter linter (deferred — not worth a block yet) would
catch the class.
