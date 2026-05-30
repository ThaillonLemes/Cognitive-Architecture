---
id: block-139
phase: phase-23
tier: M
kind: refactor
status: pending
files:
  read:
    - sdk/pattern_analyzer.py
    - sdk/patterns_report.py
    - sdk/recommendation_engine.py
    - sdk/protocol_updater.py
    - sdk/session_start.py
    - governance/tools-registry.yaml
    - blocks/block-138-velocity-fix.md
  modify:
    - sdk/pattern_analyzer.py
    - sdk/patterns_report.py
    - sdk/session_start.py
    - governance/tools-registry.yaml
  create:
    - sdk/tests/test_pattern_analyzer_window.py
    - sdk/tests/test_patterns_report_loop.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: 0 failed, 0 xfailed
  - name: patterns-report-full
    type: command
    command: python sdk/patterns_report.py --arch-root . --full
    expect: exits 0; patterns.md re-rendered; contains "**Recommendation:**" (no "No recommendation yet")
  - name: proposals-loop-closes
    type: command
    command: python sdk/protocol_updater.py --arch-root .
    expect: exits 0; at least one proposal file under governance/proposals/; index.md updated
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-139-close-loop.md]
created_at: 2026-05-29
---

# Block 139 — Close the pattern → recommendation → proposal loop

## 1. Purpose

The self-observation machinery has been instrumented (blocks 135–138) but the
loop never closes. `pattern_analyzer.analyze()` is hard-wired to the last 30
blocks (no full-history flag), `patterns_report.py` writes `governance/patterns.md`
without ever calling `recommendation_engine`, and `protocol_updater` exists but
is wired into `session_start.run_protocol_updater` while being absent from
`governance/tools-registry.yaml` — so it never fires. End result: every pattern
in `patterns.md` carries the placeholder "_No recommendation yet. Run …_", and
`governance/proposals/` stays empty. This block wires the loop end-to-end:
extract → analyze (full history) → recommend → render → propose.

## 2. Scope

In scope:
- `sdk/pattern_analyzer.py::analyze(signals, window_size=30)`: optional
  `window_size: int | None` parameter; `None` disables windowing (full history);
  default stays at 30 so existing callers/tests are untouched.
- `sdk/patterns_report.py`: add `--full` / `--window N` flags; in `main()`,
  invoke `recommendation_engine.recommend(patterns)` between `analyze` and
  `write_report` so `Pattern.recommendation` is populated before rendering;
  after `write_report`, invoke `protocol_updater.ProtocolUpdater(arch_root).run()`
  so the loop closes in one command.
- `sdk/session_start.py::run_pattern_mining`: wire the same recommend-then-update
  pass so the stale-tool run also closes the loop (currently it only calls
  `analyze → write_report`).
- `governance/tools-registry.yaml`: add a `protocol-updater` entry so the
  tool is tracked alongside `pattern-mining` (currently `run_protocol_updater`
  is defined in session_start but never invoked because no registry entry
  matches it).
- New tests:
  - `test_pattern_analyzer_window.py` — default still windows to 30; explicit
    `window_size=10` uses last 10; `window_size=None` uses all signals.
  - `test_patterns_report_loop.py` — synthetic retros → `patterns_report.main`
    end-to-end leaves a `patterns.md` containing `**Recommendation:**` (not the
    "_No recommendation yet_" placeholder), and `governance/proposals/index.md`
    has at least one row.

Out of scope:
- New detection rules (R9+) — existing R1–R8 are sufficient to prove the loop.
- Backfilling proposals for historical patterns already in the repo (the
  pipeline run at gate time will create them naturally).
- Changing the proposal template — `templates/proposal.md` stays as is.
- Surfacing proposals in `health_report.py` beyond the existing pending-count
  line — already done in block-137.

## 3. Gates

- tests-pass: full `sdk/tests/` suite, 0 failed, 0 xfailed.
- patterns-report-full: `python sdk/patterns_report.py --arch-root . --full`
  exits 0 and the rendered `governance/patterns.md` contains at least one
  `**Recommendation:**` line (and zero `_No recommendation yet_` lines if any
  patterns were detected).
- proposals-loop-closes: after `patterns_report --full` runs, invoking
  `protocol_updater` either creates ≥ 1 new proposal under
  `governance/proposals/` or reports "already exists" for every above-threshold
  pattern (idempotent). `governance/proposals/index.md` must list every active
  proposal.
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md, block-139 retro written.

## 4. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `--full` surfaces noise (patterns from blocks 1–30 that no longer apply) | Low | Default stays windowed at 30; `--full` is explicit. Recommendations cite evidence blocks so a human can dismiss stale ones via `proposal_resolver --reject`. |
| Wiring `recommend()` into `patterns_report` mutates `Pattern.recommendation` for the rendered report only; downstream consumers of `analyze()` see the same in-memory mutation | Low | `recommend()` already documents this side effect (see `recommendation_engine.recommend`). All current callers of `analyze` either render immediately or are tests that build their own patterns. |
| `protocol_updater` runs every time `patterns_report` runs → noise in commit history | Low | `_already_proposed` deduplicates by pattern slug; only new patterns create new files. |
| Adding `protocol-updater` to the registry changes `session_start` behavior for future sessions | Low | Idempotent: if no patterns above threshold, the tool prints "No patterns above threshold" and exits 0 without writing. |

## 5. Out of Scope

- New detection rules (R9+).
- Reworking the proposal template or schema.
- Migrating governance/patterns.md to a non-markdown format.
- Auto-applying proposals (still gated through `proposal_resolver --accept`).

## 6. New Abstraction

None. The change reuses `recommend()` and `ProtocolUpdater` exactly as
defined. The only API surface change is `analyze(signals, window_size=...)`,
which is an additive optional parameter.
