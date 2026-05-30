---
id: block-138
phase: phase-23
tier: M
kind: refactor
status: pending
files:
  read:
    - sdk/velocity_inference.py
    - sdk/health_report.py
    - sdk/tests/test_cli_smoke.py
    - blocks/block-086-velocity-activation.md
  modify:
    - sdk/velocity_inference.py
    - sdk/health_report.py
    - sdk/tests/test_cli_smoke.py
  create:
    - sdk/tests/test_velocity_inference.py
    - sdk/tests/test_health_report_velocity.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: 0 failed, 0 xfailed (velocity xfail removed)
  - name: velocity-help-clean
    type: command
    command: python sdk/velocity_inference.py --help
    expect: exits 0, no traceback
  - name: velocity-measured-count
    type: command
    command: python sdk/health_report.py --arch-root . && grep -c "MEASURED" governance/health-report-*.md
    expect: ">= 50 measured samples surfaced (was 25)"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-29
---

# Block 138 — Velocity fix (argparse + tier-fallback + confidence label)

## 1. Purpose

`velocity_inference.py --help` crashes (no argparse → `--help` is read as a
block_id; the empty manifest path resolves to `.` and `read_text` raises
`PermissionError`). And `health_report` reports only 25 measured samples out
of ~50 retros that actually carry `actual_duration_hours`, because 26 of those
retros omit the `tier:` field in their frontmatter and the velocity collector
silently drops them. This block fixes both.

## 2. Scope

In scope:
- `sdk/velocity_inference.py`: add `argparse` (`--help`, `--arch-root`, positional
  `block_id`); guard `_files_from_manifest` against `Path("")` and any path that
  isn't a file (current code calls `read_text` on a falsy Path which resolves to
  `.` on Windows → PermissionError).
- `sdk/health_report.py::_collect_velocity_data`: when retro frontmatter has
  `actual_duration_hours` but no `tier:`, fall back to
  `velocity_inference._tier_from_manifest(arch_root/manifests/<block_id>-*.md)`.
  This recovers the 26 blocks (086–111) whose retros pre-date the tier field.
- Velocity output: add explicit per-tier `MEASURED` (count >= 3) /
  `ESTIMATED` (count < 3, falling back to TIER_ESTIMATES) confidence label
  alongside the existing HIGH/MEDIUM/INSUFFICIENT row.
- `sdk/tests/test_cli_smoke.py`: remove `velocity_inference.py` from
  `_KNOWN_CRASHERS` (xfail goes away — the strict=True will fail the suite if
  the fix regresses).
- New tests: `test_velocity_inference.py` (--help exits 0; `Path("")` safe;
  manifest-tier inference) and `test_health_report_velocity.py` (tier-fallback
  via manifest recovers >= 50 measured samples on the real arch-root;
  MEASURED/ESTIMATED label appears in the rendered section).

Out of scope:
- Re-mining patterns over the full 134-block history → block-139.
- Closing the pattern → recommendation → proposal loop end-to-end → block-139.
- Backfilling `tier:` into the 26 old retros (their frontmatter is historical;
  the fallback is the correct fix).
- Migrating dashboard/weekly_report onto `project_state` (deferred indefinitely
  unless a bug forces it).

## 3. Gates

- tests-pass: full `sdk/tests/` suite, 0 failed, 0 xfailed (velocity xfail
  removed from `test_cli_smoke.py`).
- velocity-help-clean: `python sdk/velocity_inference.py --help` exits 0 with
  no traceback (smoke test enforces under cp1252).
- velocity-measured-count: rendered health report shows >= 50 measured samples
  across S/M/L tiers (was 25), and every row carries `MEASURED` or `ESTIMATED`.
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md updated; block-138 retro
  written.

## 4. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Manifest tier inference picks wrong tier for old blocks | Low | `_tier_from_manifest` is the same reader velocity_inference already uses; it defaults to M (the most common tier in 086-111), so worst case matches the prior silent drop. |
| Confidence label confuses existing health_report consumers | Low | Label is additive — HIGH/MEDIUM/INSUFFICIENT DATA stay; MEASURED/ESTIMATED is a new column. |
| `--help` smoke-test still fails post-fix on a Windows quirk | Low | Test runs with `PYTHONIOENCODING=cp1252`; argparse output is ASCII. |

## 5. Out of Scope

- Pattern re-mining + loop close (block-139).
- Backfilling tier into historical retros.
- New CLI subcommands on velocity_inference (single positional block_id is enough).

## 6. New Abstraction

None. The fix uses the existing `_tier_from_manifest` helper from
`velocity_inference` directly from `health_report`.
