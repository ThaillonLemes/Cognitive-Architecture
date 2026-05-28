---
id: block-030
phase: phase-5
status: done
gates_passed: 2
gates_total: 2
created_at: 2026-05-22
---

# Block 030 Retrospective — Module: convention snippet generator

## §1 What was built

- `sdk/convention_snippet.py` — full module with:
  - `AXIOMS` dict: all 19 axioms (P1-P6, Q1-Q7, C1-C6) as condensed one-liners
  - `_CORE` / `_OPTIONAL` mapping tables per `protocols/convention-snippet-generation.md`
  - Kind aliases: `doc` = `doc-only`, `implementation` ≈ `feature`, `small-fix` ≈ bugfix-like
  - `build_snippet(kind, *, modifies_code, axiom_override)` → `(axioms_str, snippet_body)`
  - CLI: `--test`, `--kind KIND`, `--list-kinds`

## §2 Gates

| Gate | Result | Evidence |
|------|--------|---------|
| snippet-test | ✅ pass | 5 kinds tested, all non-empty, all distinct, correct P→Q→C order |
| files-created | ✅ pass | sdk/convention_snippet.py exists |

## §3 Decisions / deviations

- **Sort order bug fixed:** initial `_SORT_KEY` used alphabetical group sort (C < P < Q); corrected to `_GROUP_ORDER = {P:0, Q:1, C:2}` per protocol (P → Q → C).
- **Unicode fix:** Q2 text had `≤` (U+2264); replaced with `<=` for CP1252 compatibility on Windows terminals.
- **`implementation` kind:** mapped to `feature` axiom set (Q1,Q2,Q3,Q5,Q6,C2,C4,C6) — aligns with design/governor-v2.md §4 kind vocabulary vs. protocol's `feature` label.

## §4 Scope

No scope expansion. Single file created per manifest.

## §5 Token estimate

tok_in:~4000 tok_out:~1500 tok_src:estimated
