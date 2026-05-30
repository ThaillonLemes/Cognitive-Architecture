---
id: block-150
tier: M
kind: implementation
phase: phase-26
scope: phase-bound
status: pending
security: false
dependencies:
  - block-137
files:
  read:
    - sdk/pattern_analyzer.py
    - sdk/velocity_inference.py
    - sdk/project_state.py
  create:
    - sdk/risk_forecast.py
    - sdk/tests/test_risk_forecast.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: risk-smoke
    type: command
    command: python sdk/risk_forecast.py --arch-root . --block-id block-150
    expect: exits 0; prints a risk verdict (LOW/ELEVATED) with per-heuristic rationale; advisory, never non-zero exit
  - name: heuristics-fire
    type: command
    command: python -m pytest sdk/tests/test_risk_forecast.py -q
    expect: "0 failed" (known-bad manifest flags >=1 heuristic; known-good flags none)
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-150-risk-forecast.md]
created_at: 2026-05-30
---

# Block 150 — Risk-at-block-start forecaster (heuristics + tests)

- **Tier:** M
- **Kind:** implementation
- **Status:** pending
- **Parallel-with:** block-149

## 1. Purpose

Give the architecture its first forward-looking signal at *block start*: read a
manifest before work begins and flag risk via ≥3 heuristics, each with a rationale.
Purely advisory — it informs, never blocks (Phase 26 §3, §5).

## 2. Dependencies

- `block-137` (project_state — phase/done-block context).
- Reuses `pattern_analyzer` rule semantics and `velocity_inference` tier/overrun data;
  neither is modified.

## 3. Files

- **Read:** `sdk/pattern_analyzer.py` (the known-bad clusters to resemble —
  `scope-expansion-recurring` R4, `l-tier-systematic-overrun` R7, `forced-pass-clustering` R5),
  `sdk/velocity_inference.py` (`_files_from_manifest`, `_tier_from_manifest`,
  `TIER_ESTIMATES`, `infer_duration`), `sdk/project_state.py`.
- **Create:** `sdk/risk_forecast.py` — `RiskFlag(heuristic, fired, rationale)`;
  `assess(manifest_path, arch_root) -> list[RiskFlag]`; CLI `--block-id` / `--arch-root`.
  `sdk/tests/test_risk_forecast.py`.

## 4. Validation

The ≥3 heuristics (Exit Criterion 4):
- **H1 scope-expansion resemblance** — this block's manifest shares ≥2 files with
  blocks already in the `scope-expansion-recurring` evidence set (reuse R4's signal),
  rationale names the overlapping files.
- **H2 L-tier overrun history** — `tier == "L"` AND the L-tier overrun pattern
  (`l-tier-systematic-overrun`, R7) is active in history; rationale cites the prior
  overrunning L blocks.
- **H3 oversized modify list** — `len(files.modify + files.create)` exceeds the tier
  budget (M caps at 8 per `manifest-medium.md`); rationale states count vs budget.

Checks:
- All tests pass: `python -m pytest sdk/tests/ -q`.
- Unit: a known-bad synthetic manifest (10-file modify list, tier L) fires ≥1 flag with
  a non-empty rationale; a known-good manifest (3 files, tier M, no cluster overlap)
  fires none.
- `risk_forecast.py --block-id block-150` exits 0 and prints a verdict + rationale.

## 5. Gates

Declared in frontmatter: `tests-pass`, `risk-smoke`, `heuristics-fire`,
`files-updated`. `risk-smoke` asserts the tool stays advisory (always exit 0).

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| False alarms erode trust in the signal | Med | Advisory only — never blocks a block start; every flag shows rationale + evidence so a human dismisses it in seconds. Thresholds tuned against history in block-151. |
| Heuristics crash on a malformed/partial manifest at block-start | Med | Each heuristic wrapped in try/except → unfired flag with a "could not evaluate" rationale; the assessor never raises (mirrors `analyze()`). |
| Overlap signal needs pattern evidence that may be empty early in a project | Low | H1/H2 degrade to "not enough history" (unfired) when the pattern set is empty; H3 (pure manifest shape) always works standalone. |

## 7. Out of Scope

- Blocking or gating on risk (Phase 26 §10 — it informs; humans/Phase 27 act).
- Auto-creating mitigation blocks from a flag.
- New detection rules in `pattern_analyzer` (this reuses R4/R5/R7 evidence).
- Wiring into block-start automation (`block_start.py`) — surfacing point is deferred;
  this block delivers the engine + CLI only.

## 8. New Abstraction

`RiskFlag` dataclass (Axiom Q1). Justified by Rule of Three: three independent
heuristics each need to return the same shape — `(heuristic, fired, rationale)` — so a
caller can render or filter them uniformly; a bare bool/tuple would lose the rationale
the advisory contract requires.
