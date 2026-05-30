---
id: block-152
phase: phase-27
tier: M
status: done
actual_duration_hours: 0.8
duration_source: estimated
gates_passed: 3/3
created_at: 2026-05-30
---

# Block 152 Retrospective — Proposal → concrete unified-diff generator

## 1. What was built

- `sdk/proposal_apply.py`: `generate_diff(proposal_id, arch_root) -> DiffResult`
  (`proposal_id, target_file, is_immutable, unified_diff, rationale, status`). Loads the
  proposal, requires `status: accepted`, reads `target_file` from the proposal frontmatter
  (not the stale index placeholder), and produces a CONCRETE `difflib.unified_diff` of the
  target → target+reviewable section (provenance anchor + `## Note (from proposal …)` +
  the proposed-change text). Reuses `proposal_resolver._is_immutable` /
  `_get_frontmatter_field`; adds `_read_block_scalar` for YAML block bodies. **Writes
  nothing**; never raises. CLI renders the diff + an IMMUTABLE banner, exits 0.
- `sdk/tests/test_proposal_apply.py` — 25 tests.

## 2. Why this matters

The old `proposal_resolver.accept(apply=True)` only appended an opaque HTML comment. This
replaces it with a real, reviewable unified diff against the actual target file — the first
step of closing the learning loop's last mile (detect → propose → **concrete change**).
Generation is decoupled from application: 152 renders, 153 guards, 154 applies+rolls back.

## 3. Gates

- tests-pass: 965 passed, 0 failed (25 new + 1 smoke) ✓
- renders-immutable-target: `proposal_apply --proposal 2026-05-29-scope-expansion-recurring`
  exits 0, prints a unified diff + IMMUTABLE banner ✓
- writes-nothing: target (`templates/manifest-medium.md`) + proposals dir byte-identical
  after CLI/test runs (asserted) ✓

## 4. Files actually touched

`sdk/proposal_apply.py`, `sdk/tests/test_proposal_apply.py` created.
