---
id: block-140
phase: phase-24
tier: M
status: done
actual_duration_hours: 0.5
duration_source: estimated
gates_passed: 4/4
created_at: 2026-05-30
---

# Block 140 Retrospective — INDEX diet: split catalog to cold CATALOG.md

## 1. What was built

- New cold `CATALOG.md`: holds every per-file brief — the old `INDEX.md` "## Briefs"
  table (~50 rows) plus the per-file WARM rows (individual phase docs + `sdk/` files).
  Back-pointer `Navigation map → INDEX.md`.
- `INDEX.md` rewritten as a thin folder-level navigation map: HOT table (kept), WARM
  as folders-only (per-file detail → CATALOG.md), COLD folders, and an explicit
  `Full per-file catalog → CATALOG.md` pointer. No brief deleted — relocated.
- `CLAUDE.md` HOT read-order #4 updated: "`INDEX.md` — folder navigation map; full
  per-file catalog → `CATALOG.md` (cold, on-demand)".

## 2. Gates

- tests-pass: 789 passed, 0 failed ✓
- pointer-integrity-clean: audit check 3 shows no broken pointer for INDEX.md or
  CATALOG.md (the WARNs present are all pre-existing — decisions/README, the
  pointer-integrity.md literal examples, proposals index) ✓
- index-hot-shrunk: INDEX.md ~2380 → **~591 tok**; HOT boot total ~7260 → **~5495 tok** ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md, this retro ✓

## 3. Note on execution vs manifest

The manifest said "cut the ## Briefs section"; to actually hit the ≤600-tok target I
also moved the per-file WARM rows (individual phase docs + sdk/ files) into CATALOG.md,
keeping only folder-level entries in INDEX. Same files (`INDEX.md` modify, `CATALOG.md`
create), broader cut — required to meet the exit criterion. Folder navigation stays in
INDEX; every specific-file lookup is one hop away in CATALOG.

## 4. Effect

INDEX.md is now ~25% of its former size and contains only what a session needs at boot
(where to look), with the full catalog one pointer away. This is the largest single
cut of the Phase-24 diet (−1789 tok). Remaining gap to <4000 is closed by block-141
(STATE dedup) and block-142 (_syntax reclassify).

## 5. Files actually touched

As manifest (INDEX.md, CLAUDE.md modified; CATALOG.md created).
