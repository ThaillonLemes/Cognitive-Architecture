---
id: phase-24
status: done
prev_phase: phase-23
exit_criteria_count: 6
blocks_count: 4
estimated_duration_minutes: 150
created_at: 2026-05-30
last_updated: 2026-05-30
owner: implementer
---

# Phase 24 — Context Diet (Boot-Cost Reduction)

BRIEF: The HOT boot costs ~7260 tok every session — 1.8× the 4000-tok budget. This
phase cuts it under budget by reclassifying files that aren't truly read at boot,
de-duplicating data that already lives elsewhere, and splitting fat catalogs into a
thin hot pointer + cold reference. No immutable file is touched.

## 1. Purpose

Every session pays a fixed context tax just to boot: the seven HOT files total
~7260 tokens against a documented 4000-token budget (audit check: `OVER BUDGET`,
1.8×). That tax is paid before any real work starts, on every single session.
This phase brings the HOT boot under 4000 tokens — not by deleting knowledge, but
by (a) aligning the HOT set with what the read-order *actually* reads at boot,
(b) removing a data duplication (`STATE.blocks_done` duplicates `BLOCK_LOG`), and
(c) splitting `INDEX.md`'s reference catalog into a thin hot index plus a cold,
load-on-demand catalog. Everything moved stays reachable and pointed-to. It also
advances the Phase-23 theme — instruments that tell the truth — by making the HOT
measurement reflect the documented read-order instead of an inflated stale set.

## 2. Goals

- HOT boot total < 4000 tok (audit no longer reports `OVER BUDGET`), with ≥200 tok headroom.
- `INDEX.md` split: thin HOT navigation index (HOT/WARM/COLD folder pointers) + new cold `CATALOG.md` carrying the per-file briefs; nothing lost, everything pointed-to.
- `STATE.md`: replace the inline `blocks_done:` list (139 entries) with a count + `BLOCK_LOG` pointer; `BLOCK_LOG.md` is the single source of truth for the done-set.
- `_syntax.md` reclassified to WARM/on-demand (read when writing AI-only files, not at every boot); its bytes stay identical (integrity lock intact), and the audit HOT set + `CLAUDE.md` read-order are updated to agree.
- A regression gate (test) fails if the HOT boot ever exceeds 4000 tok again — so the diet can't silently regress.
- No information lost: every relocated brief/list is reachable from a hot pointer.

## 3. Invariants

- **No immutable file is modified.** `PROTOCOLS.md` and `_syntax.md` bytes stay
  identical (both are in `.integrity.lock`); `_syntax.md` is *reclassified*, not
  edited. Integrity check stays green.
- All 789 tests stay green; `sdk/audit.py` stays PASS with 0 errors.
- No knowledge is deleted — only relocated, with a hot pointer to its new home.
- The audit's HOT set change is a *correction* (align with documented read-order),
  not metric-gaming: `CLAUDE.md` and the audit must agree on what is HOT.

## 4. Dependencies

- Phase 23 complete (instruments trustworthy; loop closed). ✓
- `BLOCK_LOG.md` is complete and authoritative (it is — through block-139).
- No external dependencies; stdlib + pytest only.

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Something parses `STATE.blocks_done` and breaks when it's removed | Med | block-141 first greps all readers; `session_start._read_state` only reads p/status/last_block/notes — not blocks_done. Migrate any reader to `project_state.completed_block_ids()` (BLOCK_LOG-backed, from block-137). |
| Reclassifying `_syntax.md` out of HOT loses needed syntax context at boot | Med | It's already a "see also" in the read-order, not a mandatory read; session_start parses STATE programmatically. Keep a one-line hot pointer in INDEX + CLAUDE.md so it's one hop away when writing AI-only files. This is the phase's one judgment call — flagged for review. |
| Editing `sdk/audit.py` HOT lists looks like gaming the metric | Med | Pair every audit-set change with the matching `CLAUDE.md`/`INDEX.md` read-order change in the same block, so protocol and measurement stay in sync. The real reductions (INDEX split, STATE dedup) are genuine content cuts, not list edits. |
| INDEX split leaves dangling references | Low | block-143 verifies every brief in the old INDEX is present in CATALOG.md and that INDEX points to it (pointer-integrity audit check covers cross-file refs). |

## 6. Validation

- Unit: each diet block keeps its module/tests green.
- Regression gate: a new test asserts HOT boot < 4000 tok (computed the same way
  as `sdk/audit.py::print_token_estimates`), so future growth fails CI.
- Integration: full `sdk/audit.py` run — PASS, 0 errors, HOT not `OVER BUDGET`,
  integrity lock still all-OK (no immutable drift).

## 7. Exit Criteria

1. `sdk/audit.py` HOT boot total < 4000 tok and the line no longer prints `OVER BUDGET` (was ~7260); ≥200 tok headroom.
2. `INDEX.md` HOT body ≤ ~600 tok; the per-file catalog lives in cold `CATALOG.md`, and every brief from the old INDEX is present there and reachable via an INDEX pointer.
3. `STATE.md` no longer contains the inline `blocks_done:` list; the done-set is read from `BLOCK_LOG` via `project_state`; `sdk/audit.py` and `session_start.py` still report the correct block count.
4. `_syntax.md` is byte-identical (integrity lock OK) but removed from the audit HOT set and the `CLAUDE.md` boot read-order, with a hot one-line pointer to it for on-demand use.
5. A regression test asserts HOT boot < 4000 tok and fails if exceeded; it is part of `sdk/tests/` and green.
6. Full suite green (≥789 tests); `sdk/audit.py` PASS with 0 errors; integrity check all-OK; no immutable file modified.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-140 | INDEX diet — split catalog to cold CATALOG.md | M | done | `manifests/block-140-index-diet.md` |
| block-141 | STATE diet — dedup blocks_done into BLOCK_LOG | M | done | `manifests/block-141-state-diet.md` |
| block-142 | HOT-set correction + _syntax reclassify | M | done | `manifests/block-142-hot-set-correct.md` |
| block-143 | Boot-budget regression gate + verification | S | done | `manifests/block-143-budget-gate.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 3
  groups:
    - id: 24A
      blocks: [block-140, block-141, block-142]
      type: parallel          # different files: INDEX.md / STATE.md / (audit.py + CLAUDE.md)
      depends_on: []
    - id: 24B
      blocks: [block-143]
      type: sequential        # regression gate + final audit, needs 140-142 landed
      depends_on: [24A]
```

## 10. Out of Scope

- Splitting `PROTOCOLS.md` into a hot axiom-cheatsheet + cold full text (touches an
  immutable file; not needed to get under budget — deferred to a future phase if the
  budget tightens).
- Trimming `CLAUDE.md` / `board.md` prose (already small; not worth the churn).
- Changing the 4000-tok budget itself (the goal is to fit it, not move it).
- Multi-agent activation, self-healing gates (Direction A), self-modification
  (Direction B) — separate future phases.
