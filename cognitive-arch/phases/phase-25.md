---
id: phase-25
status: done
prev_phase: phase-24
exit_criteria_count: 6
blocks_count: 4
estimated_duration_minutes: 180
created_at: 2026-05-30
last_updated: 2026-05-30
owner: implementer
---

# Phase 25 — Self-Healing / Anti-Drift

BRIEF: The architecture keeps drifting silently — stale/incomplete integrity lock,
missing retros, tier-less retros, runner not in registry — and nothing catches it
until a human runs an audit. This phase turns those passive audit *warnings* into
active *invariants* that the system checks at block-close and either auto-repairs or
HALTs on.

## 1. Purpose

Every failure this project has hit recently was silent bookkeeping drift, not a
logic bug: the `.integrity.lock` was stale for 26 blocks AND missing 9 of 17
immutable files; `block-085` is in `BLOCK_LOG` with no retro; 26 retros carried a
duration but no tier (block-138); a tool runner existed but was absent from the
registry (block-139). The audit *sees* these, but only as passive warnings nobody
acts on — which is why the audit score sits at 32/100 while `health_report` claims
100/100. This phase makes the architecture enforce its own invariants: a declarative
invariant registry, a checker engine, safe auto-repair, and a block-close gate that
HALTs on critical drift. It is the defensive half of "an architecture that keeps
itself honest," and the prerequisite for guarded self-modification (Phase 27).

## 2. Goals

- A declarative invariant registry (`sdk/invariant_schema.py`) + checker engine
  (`sdk/invariant_check.py`) with ≥6 invariants, each: id, description, severity
  (critical/warn), check fn, and an optional auto-repair fn.
- Seed invariants from real drift this project hit:
  - INV1: every file tagged `protection: immutable` ∈ `.integrity.lock`.
  - INV2: every `BLOCK_LOG` entry has a retro file in `blocks/`.
  - INV3: every retro with `actual_duration_hours` has a resolvable tier.
  - INV4: every id in `session_start.TOOL_RUNNERS` is in the registry (or a known event tool).
  - INV5: `STATE.last_block` == latest `BLOCK_LOG` entry; `NEXT` pointer consistent.
  - INV6: every proposal file ↔ a row in `proposals/index.md` (both directions).
- Safe auto-repair (dry-run by default, `--apply` to act) for the mechanically-fixable
  subset (INV1 lock incompleteness, INV4 reporting, INV6 index reconcile); HALT for
  the rest.
- A block-close invariant gate: critical violations block the close; warnings surface.
- Wired into `session_start` + `governance/tools-registry.yaml` so drift is visible
  every session.
- Real-arch-root scan reaches 0 *critical* violations (existing drift backfilled or documented).

## 3. Invariants

- Auto-repair NEVER modifies a `protection: immutable` file without the human
  integrity-bump gate (`commands/integrity-bump.md`); for immutable drift it stages
  a proposal/instruction, not a silent edit.
- All existing tests stay green; `sdk/audit.py` stays PASS (0 errors).
- The checker never crashes the session — a failing invariant is reported, not raised
  (mirror `pattern_analyzer.analyze` resilience).
- New invariants are data, not code branches — adding one is a registry entry + a fn.

## 4. Dependencies

- Phase 24 complete (or independent — touches different files; can run after 24).
- `project_state.py` (block-137) as the canonical BLOCK_LOG/phase reader.
- `integrity_check.py` (block-091/136) reused for INV1.

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Auto-repair makes an unwanted change | High | Dry-run default; `--apply` explicit; immutable files never auto-edited; every repair backs up to `_backups/`. |
| Block-close gate becomes a nuisance (false HALTs) | Med | Only `critical` invariants HALT; warnings just surface. Severity tuned against the real arch-root in block-147. |
| Backfilling block-085 retro fabricates history | Med | Don't invent — write a minimal "reconstructed retro" marked `duration_source: unknown`, or document it as an accepted gap (human decides in block-147). |
| Overlap with the existing audit checks | Low | Invariants are the *active/gating* layer; audit stays the *report* layer. block-146 notes which audit checks become invariant-backed. |

## 6. Validation

- Unit tests per invariant (fires on synthetic drift, clean on healthy input).
- Integration: checker on the real arch-root → enumerated violations; after backfill → 0 critical.
- Regression: a test asserts the block-close gate HALTs on a critical violation and passes when clean.

## 7. Exit Criteria

1. `sdk/invariant_check.py` + `sdk/invariant_schema.py` exist with ≥6 registered invariants, each with tests (fires-on-drift + clean-on-healthy).
2. Safe auto-repair implemented for INV1/INV4/INV6 with dry-run default and `_backups/` safety; immutable files never auto-edited.
3. Block-close gets an invariant gate: a documented step (in the close flow) + the engine returns a HALT-worthy result on critical violations, with a test.
4. `session_start` runs the checker and surfaces violations; `tools-registry.yaml` has an `invariant-check` entry.
5. Real-arch-root scan = 0 critical violations (block-085 and any others backfilled or documented as accepted).
6. Full suite green; `sdk/audit.py` PASS, 0 errors; integrity lock all-OK.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-144 | Invariant registry + checker engine (6 invariants + tests) | M | done | `manifests/block-144-invariant-engine.md` |
| block-145 | Safe auto-repair (INV1/INV4/INV6, dry-run + backups) | M | done | `manifests/block-145-auto-repair.md` |
| block-146 | Wire invariant gate into block-close + session_start + registry | M | done | `manifests/block-146-wire-gate.md` |
| block-147 | Backfill real drift to 0 critical + regression tests | M | done | `manifests/block-147-backfill-verify.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 1
  groups:
    - id: 25A
      blocks: [block-144]
      type: sequential
      depends_on: []
    - id: 25B
      blocks: [block-145, block-146]
      type: sequential        # both build on the engine; 146 needs 145's repair API
      depends_on: [25A]
    - id: 25C
      blocks: [block-147]
      type: sequential
      depends_on: [25B]
```

## 10. Out of Scope

- Applying repairs to immutable files (that's Phase 27's guarded-self-modification path).
- Predictive/forecasting checks (Phase 26).
- New audit checks unrelated to the seeded invariants.
- Auto-creating follow-up blocks from violations (violations surface; humans schedule).
