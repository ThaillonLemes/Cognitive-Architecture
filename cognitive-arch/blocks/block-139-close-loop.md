---
id: block-139
phase: phase-23
tier: M
status: done
actual_duration_hours: 1.3
duration_source: estimated
gates_passed: 4/4
created_at: 2026-05-29
---

# Block 139 Retrospective — Close the pattern → recommendation → proposal loop

## 1. What was built

- `sdk/pattern_analyzer.py`: `analyze(signals, window_size=30)` now accepts an
  optional `window_size: int | None`; the analyzer windows once at the top and
  passes the windowed list to each rule. `_window()` learned to skip the slice
  when `size is None`. Default stays at 30 — existing callers and the old
  `test_pattern_analyzer.py` suite are untouched.
- `sdk/patterns_report.py`: new flags `--full`, `--window N`, `--no-propose`;
  new `run_pipeline(arch_root, window_size, propose)` that runs
  `extract_all → analyze → recommend → write_report → ProtocolUpdater.run`
  in one call. CLI main() prints a one-line summary covering both stages.
- `sdk/session_start.py::run_pattern_mining`: now delegates to
  `patterns_report.run_pipeline` with `window_size=None, propose=True`, so the
  session bootstrap closes the full loop instead of stopping at the rendered
  report.
- `governance/tools-registry.yaml`: `pattern-mining` description and command
  updated to advertise the closed loop (full-history mine + recommend +
  propose); cadence unchanged at 7 days.
- New tests:
  - `sdk/tests/test_pattern_analyzer_window.py` (9 tests) — `_window` and
    `analyze` honor `window_size=30` default, explicit small sizes, and
    `None`-disables-windowing.
  - `sdk/tests/test_patterns_report_loop.py` (6 tests) — synthetic arch with
    five force-passed blocks runs end-to-end: `patterns.md` contains
    `**Recommendation:**` (no placeholder), `governance/proposals/` gets a
    proposal file, index is updated, second run is idempotent, `--no-propose`
    skips the writer, summary dict has the expected shape.
- `governance/proposals/index.md`: stripped a stale "_No proposals yet_"
  placeholder line that survived because `protocol_updater._update_proposals_index`
  only appends.

## 2. Gates

- tests-pass: 789 passed, 0 failed, 0 xfailed (was 774 + 0 xfailed; +15 new) ✓
- patterns-report-full: `python sdk/patterns_report.py --arch-root . --full`
  exits 0; rendered `governance/patterns.md` shows 3 patterns and 3
  `**Recommendation:**` lines (zero `_No recommendation yet_`) ✓
- proposals-loop-closes: 3 proposals created on first run
  (`gate-failures-recurring`, `scope-expansion-recurring`, `velocity-data-gap`);
  re-running prints `[skip] Proposal already exists` for each and creates 0 —
  idempotence confirmed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-139-close-loop.md ✓

## 3. What the closed loop surfaced

Full-history mining (window=None) over 111 done retros lit up three patterns
that the 30-block default had been hiding:

| Pattern | Severity | Occurrences | First → last seen |
|---------|----------|-------------|-------------------|
| `gate-failures-recurring` | warn | 4 | block-125 → block-132 |
| `scope-expansion-recurring` | warn | 9 | block-052 → block-097 |
| `velocity-data-gap` | info | 58 | block-001 → block-060 |

The velocity-data-gap proposal (58 blocks!) is the historical pre-block-086
era — these retros never carried `actual_duration_hours` because the field
didn't exist yet. Block-138's manifest-tier-fallback fixed the inference path,
but the underlying data is still missing. The proposal will sit pending until
a human decides whether to retroactively backfill (probably not worth it) or
accept the gap as historical.

The scope-expansion proposal points at blocks 052–097 — a cluster from
phase-12/13 that block-138's retro didn't see because they were outside the
30-block window. Worth a real ADR or block-start gate (see proposal text).

The gate-failures proposal covers the recent phase-22 cluster (blocks
125, 127, 131, 132). Already partially addressed by the gate-revision work
in phase-22; the human should likely mark this `accepted` with a note that
the underlying issue is closed.

## 4. Root cause of the prior gap

Three independent omissions, all from the same era (blocks 121–123 when the
self-observation pipeline was being assembled):

**A — `analyze()` had no window override.** `pattern_analyzer.analyze` always
ran every rule against the last 30 signals. No flag, no env var, no
opt-out. Even when `session_start.run_pattern_mining` wanted the full
history, the analyzer would silently truncate.

**B — `patterns_report` never called `recommend()`.** The CLI rendered
`Pattern.recommendation` straight from the dataclass default (empty string),
which the renderer fell back on with `_No recommendation yet. Run
sdk/recommendation_engine.py to populate._`. Nobody ever ran the engine
separately because nothing told them to.

**C — `protocol_updater` was wired into `TOOL_RUNNERS` but absent from the
registry.** `session_start.TOOL_RUNNERS["protocol-updater"] = run_protocol_updater`
existed (block-122), but `governance/tools-registry.yaml` had no matching
`id: protocol-updater` row. The dispatcher iterates the registry, so the
runner was dead code.

Block-139 collapses all three by making `patterns_report.run_pipeline` the
single composed step, then pointing `session_start.run_pattern_mining` and
the CLI entry point at it.

## 5. What I'd do differently

The pipeline composition (extract → analyze → recommend → render → propose)
should have lived in a single function from day one — the original split
across `pattern_analyzer.py`, `patterns_report.py`, `recommendation_engine.py`,
and `protocol_updater.py` made each step individually testable but
collectively orphaned. Today's `run_pipeline` is the missing top-level seam.

The registry-vs-runner mismatch in (C) above is the kind of bug that a
once-per-CI check `assert set(TOOL_RUNNERS) <= set(registry_ids) | KNOWN_EVENT_TOOLS`
would have caught immediately. Deferred (not worth a block yet) but worth
remembering the next time someone adds a runner.

## 6. Files actually touched

As manifest.

## 7. Post-implementation notes (block + proposals finalized)

- **`_window(None)` fix.** The full-history path was still latent: `_window`
  did not special-case `size=None`. Added the guard (`return signals` when
  `size is None`) — this is what makes `--full` / `window_size=None` actually
  mine all blocks instead of truncating to 30.
- **Dead runner removed.** `session_start.run_protocol_updater` and its
  `TOOL_RUNNERS["protocol-updater"]` entry were deleted. Proposing is folded
  into `pattern-mining` (`run_pipeline(propose=True)`), so a runner whose id
  never appeared in the registry was misleading dead code.
- **The 3 proposals are resolved** (no longer pending):
  `scope-expansion-recurring` → accepted, `gate-failures-recurring` → accepted,
  `velocity-data-gap` → rejected (historical — blocks 001–060 predate the
  `actual_duration_hours` field; nothing to backfill). See
  `governance/proposals/index.md`.
