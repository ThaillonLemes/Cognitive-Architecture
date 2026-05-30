---
id: block-149
tier: M
kind: refactor
phase: phase-26
scope: phase-bound
status: pending
security: false
dependencies:
  - block-148
files:
  read:
    - sdk/health_report.py
    - sdk/audit.py
    - sdk/health_model.py
  modify:
    - sdk/health_report.py
    - sdk/audit.py
  create:
    - sdk/tests/test_health_consistency.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: scores-agree
    type: command
    command: python -m pytest sdk/tests/test_health_consistency.py -q
    expect: "0 failed" (audit score == health_report score == health_model score on real arch-root)
  - name: audit-still-passes
    type: command
    command: python sdk/audit.py --arch-root .
    expect: exits 0; "Result: PASS"; same Score line as health_model
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-149-reconcile-health.md]
created_at: 2026-05-30
---

# Block 149 — Reconcile audit ↔ health_report onto one score

- **Tier:** M
- **Kind:** refactor
- **Status:** pending
- **Parallel-with:** block-150

## 1. Purpose

Kill the 32-vs-100 contradiction. `audit.py::AuditResult.to_dict` scores
`100 − errors·15 − warnings·2` while `health_report.py::_section_audit` independently
scores `100 − errors·20 − warnings·5` — two formulas, two numbers. Make both report
the SAME score from `health_model` (audit = the per-check detail view of that one
model), and add a test asserting they can never diverge again.

## 2. Dependencies

- `block-148` (`health_model.HealthScore` / `compute`) — must be `done`.

## 3. Files

- **Read:** `sdk/health_model.py` (the canonical `compute`/`HealthScore`).
- **Modify:**
  - `sdk/health_report.py::_section_audit` — replace its independent
    `100 − errors·20 − warnings·5` math with `health_model.compute(arch_root)`;
    render the score plus `top_drags(3)` (Exit Criterion 2 surfaces drags here).
  - `sdk/audit.py` — keep all 10 checks and per-check OK/WARN/ERROR detail, but make
    the reported `Score:` line (and `to_dict()["score"]`) come from
    `health_model.compute(...)` instead of the local `100 − e·15 − w·2`. Audit becomes
    the detail view of the shared model.
- **Create:** `sdk/tests/test_health_consistency.py`.

## 4. Validation

- All tests pass: `python -m pytest sdk/tests/ -q`.
- `test_health_consistency.py`: on the real arch-root, the score from
  `audit.run_audit(...).to_dict()`, the score parsed from `health_report`'s rendered
  output, and `health_model.compute(...).score` are **equal** — the regression that
  asserts the two instruments cannot diverge (Phase 26 §6).
- `python sdk/audit.py --arch-root .` still exits 0, prints `Result: PASS`, and shows
  the same number as a fresh `health_model` run.

## 5. Gates

Declared in frontmatter: `tests-pass`, `scores-agree`, `audit-still-passes`,
`files-updated`. `scores-agree` is the proof the contradiction is dead.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pointing audit's score at the model changes the headline number maintainers expect | Med | Keep every per-check OK/WARN/ERROR line intact; only the aggregate `Score:` changes. Document old→new mapping in the block-149 retro. |
| `audit.py` is run as a subprocess by other tools; importing `health_model` adds a path-insert dependency | Low | `health_model` is stdlib-only and importable via the same `sys.path.insert` audit/health_report already use for siblings. |
| `health_report` and `audit` compute on slightly different inputs and still disagree | Med | Both call the identical `health_model.compute(arch_root)` with the same arch-root — same input ⇒ same score, enforced by `scores-agree`. |
| `audit --json` consumers depend on the old score field | Low | Field name (`score`) unchanged; only its derivation changes; value range stays 0–100. |

## 7. Out of Scope

- Adding/removing audit checks (only their aggregate score is unified).
- Changing the weighting table (that lives in `health_model`, set in block-148).
- Forecast/risk surfaces (blocks 150–151).
- Touching the dashboard generator (it reads whichever score these now agree on).

## 8. New Abstraction

None. This block consumes `health_model.compute` / `HealthScore.top_drags` from
block-148 as-is and deletes the two duplicate scorers. Net abstraction count drops.
