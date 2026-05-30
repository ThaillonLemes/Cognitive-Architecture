---
id: block-140
phase: phase-24
tier: M
kind: refactor
status: pending
files:
  read:
    - INDEX.md
    - CLAUDE.md
    - sdk/audit.py
    - protocols/pointer-integrity.md
  modify:
    - INDEX.md
    - CLAUDE.md
  create:
    - CATALOG.md
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: pointer-integrity-clean
    type: command
    command: python sdk/audit.py --arch-root .
    expect: 'check [3/10] prints "OK: pointer integrity" — no "broken pointer" lines for INDEX.md or CATALOG.md'
  - name: index-hot-shrunk
    type: command
    command: python sdk/audit.py --arch-root .
    expect: 'INDEX.md token estimate dropped from ~2380 toward ~550 tok; HOT boot total line decreases'
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-140-index-diet.md]
created_at: 2026-05-30
---

# Block 140 — INDEX diet: split catalog to cold CATALOG.md

- **Tier:** M
- **Kind:** refactor
- **Status:** pending
- **Parallel-with:** block-141, block-142 (different files)

## 1. Purpose

`INDEX.md` costs ~2380 HOT tokens — the single largest line item in the ~7260-tok
boot, and ~33% of the whole budget. Most of that weight is the per-file "Briefs"
catalog (lines ~69–120, ~50 rows describing individual `sdk/` and `protocols/`
files) that nobody needs at boot — it's a lookup table, read on demand. This block
splits `INDEX.md` into a thin HOT navigation index (HOT/WARM/COLD folder pointers
only, ~550 tok) and moves the big per-file briefs catalog into a new cold
`CATALOG.md`, with `INDEX.md` and `CLAUDE.md` pointing to it. No brief is deleted.

## 2. Dependencies

None. (Phase 23 complete; INDEX.md is not in `.integrity.lock`, so it is mutable.)

## 3. Files

- **Read:** `INDEX.md` (source of the split), `CLAUDE.md` (read-order line 4 names
  INDEX as "file catalog" — must be updated to mention CATALOG), `sdk/audit.py`
  (check 3 pointer-integrity + `print_token_estimates` measure the result),
  `protocols/pointer-integrity.md` (Phase 4 "INDEX.md catalog" + relative-path rule).
- **Modify:** `INDEX.md` (cut the `## Briefs` section, lines ~69–120; keep HOT/WARM/
  COLD folder tables; add a one-line pointer `Full per-file catalog → CATALOG.md`),
  `CLAUDE.md` (HOT read-order #4: "`INDEX.md` — folder map; full file catalog →
  `CATALOG.md`").
- **Create:** `CATALOG.md` (header + BRIEF + the relocated per-file Briefs table,
  with a back-pointer `Navigation map → INDEX.md`; classified COLD in INDEX).

## 4. Validation

- Build/tests: `python -m pytest sdk/tests/ -q` → 0 failed.
- `python sdk/audit.py --arch-root .`: check 3 reports no broken pointer for the
  new `INDEX → CATALOG` and `CATALOG → INDEX` links; `print_token_estimates` shows
  INDEX.md down toward ~550 tok and a lower HOT boot total.
- Manual diff: every brief row present in old `INDEX.md` lines 69–120 appears in
  `CATALOG.md` (no row lost); the relative paths in those rows still resolve from
  `CATALOG.md`'s directory (same repo root, so paths are unchanged).
- `INDEX.md` line count stays ≤ its 250-line size budget (check 2) — it will, it shrinks.

## 5. Gates

Declared in frontmatter: tests-pass, pointer-integrity-clean, index-hot-shrunk,
files-updated. `index-hot-shrunk` is the diet's evidence; `pointer-integrity-clean`
guards against a dangling split. block-143 adds the hard <4000-tok regression gate.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| A brief row is dropped during the cut/paste | Med | Move the whole `## Briefs` block verbatim; diff old vs new row counts; pointer-integrity Phase 4 flags files cataloged in neither. |
| Relative paths in moved rows break because CATALOG.md lives elsewhere | Low | CATALOG.md sits at repo root next to INDEX.md, so every relative path resolves identically; audit check 3 confirms. |
| Agents still read only INDEX and miss the catalog | Low | INDEX + CLAUDE.md both carry an explicit `→ CATALOG.md` pointer; CATALOG is one hop, classified COLD/on-demand by design. |

## 7. Out of Scope

- Trimming the HOT/WARM/COLD folder tables themselves (kept as the navigation core).
- Re-categorizing any file between HOT/WARM/COLD (that is `_syntax` only, block-142).
- Touching `PROTOCOLS.md` or `_syntax.md` (immutable).
- Auto-generating CATALOG.md from disk (manual split now; generator is future work).

## 8. New Abstraction

None. CATALOG.md is a content file, not code — it reuses the existing INDEX table
format. No new trait/class/utility.
