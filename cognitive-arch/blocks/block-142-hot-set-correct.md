---
id: block-142
phase: phase-24
tier: M
status: done
actual_duration_hours: 0.4
duration_source: estimated
gates_passed: 4/4
created_at: 2026-05-30
---

# Block 142 Retrospective — HOT-set correction: reclassify _syntax.md to WARM

## 1. What was built

- `sdk/audit.py`: removed `"_syntax.md"` from BOTH HOT lists — the `SIZE_BUDGETS` map
  (check 2) and the `print_token_estimates` cost list — so the budget and the token
  total agree. Added a comment documenting the reclassification.
- `INDEX.md`: moved the `_syntax.md` row from the HOT table to WARM, noting "read
  on-demand when writing STATE/NEXT/board (not a boot read)".
- `CLAUDE.md`: read-order item 2 now reads "`_syntax.md` holds the vocab — read
  on-demand, not at boot", so protocol and measurement agree (not metric-gaming).
- New `sdk/tests/test_hot_set.py` (4 tests): `_syntax.md` absent from `SIZE_BUDGETS`
  and the token-estimate list; the cost list is exactly the six boot files; CLAUDE.md
  does not number `_syntax.md` as a HOT read.
- `_syntax.md` itself: **not touched** — bytes identical, integrity lock green.

## 2. Gates

- tests-pass: 793 passed, 0 failed (was 789 + 4 new) ✓
- syntax-absent-from-hot-lists: `('_syntax.md' in SIZE_BUDGETS, in getsource) == (False, False)` ✓
- integrity-verify-all-ok: `_syntax.md: OK`; all 17 immutable files verified OK (no byte drift) ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md, this retro ✓

## 3. The Phase-24 milestone

**HOT boot total: ~7260 → ~3762 tok — UNDER the 4000 budget.** Audit no longer prints
`OVER BUDGET`. The three diet cuts compounded: INDEX −1789 (block-140), STATE −337
(block-141), _syntax −1412 (this block). The boot tax every session pays dropped ~48%.

## 4. The judgment call (flagged)

This block reclassified `_syntax.md` out of the boot set — the phase's one debatable
move. Justification held up: `_syntax.md` was already only a "see also" pointer, never
a numbered boot read, and `session_start.py` parses STATE in code without it. The audit
edit was paired with the matching CLAUDE.md/INDEX.md read-order edits in the same block
so the protocol and the measurement say the same thing. The hot one-line pointer keeps
it one hop away when writing AI-only files.

## 5. Files actually touched

As manifest (sdk/audit.py, CLAUDE.md, INDEX.md modified; sdk/tests/test_hot_set.py created).
