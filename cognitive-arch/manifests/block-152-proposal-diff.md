---
id: block-152
tier: M
kind: implementation
phase: phase-27
scope: phase-bound
status: pending
security: false
dependencies:
  - block-125
  - block-122
files:
  read:
    - sdk/proposal_resolver.py
    - sdk/protocol_updater.py
    - governance/proposals/index.md
  modify: []
  create:
    - sdk/proposal_apply.py
    - sdk/tests/test_proposal_apply.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: dry-run-renders-diff
    type: command
    command: python sdk/proposal_apply.py --arch-root . --proposal 2026-05-29-scope-expansion-recurring --dry-run
    expect: 'exits 0; prints a unified diff (lines starting "--- ", "+++ ", "@@") against target_file; writes nothing'
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-152-proposal-diff.md]
created_at: 2026-05-30
---

# Block 152 — Proposal → concrete unified-diff generator (dry-run render)

- **Tier:** M
- **Kind:** implementation
- **Status:** pending
- **Parallel-with:** none (head of Phase 27 chain)

## 1. Purpose

Turn an `accepted` proposal into a concrete unified diff against its
`target_file` — a real, reviewable edit, not the HTML-comment stub that
`proposal_resolver.accept(apply=True)` appends today (see resolver lines
131–138). This block ships only the diff *generation + dry-run render*; guards
(153) and apply/rollback (154) build on it.

## 2. Dependencies

- `block-125` — `proposal_resolver.py` (status helpers, `_is_immutable`, `.bak`
  pattern; this block reuses its front-matter readers, must be `done`).
- `block-122` — `protocol_updater.py` (proposal schema: `target_file`,
  `proposed_change`, `rationale`, `status` front-matter; must be `done`).

## 3. Files

- **Read:** `sdk/proposal_resolver.py` (reuse `_get_frontmatter_field`,
  `_is_immutable`), `sdk/protocol_updater.py` (proposal field names),
  `governance/proposals/index.md` (real proposal IDs).
- **Modify:** none.
- **Create:** `sdk/proposal_apply.py`, `sdk/tests/test_proposal_apply.py`.

## 4. Validation

- All tests pass: `python -m pytest sdk/tests/ -q` (0 failed).
- `proposal_apply.py --help` exits 0 (argparse: `--arch-root`, `--proposal ID`,
  `--dry-run`).
- `build_diff(proposal_id)` reads the proposal, resolves `target_file`, derives
  the edit from `proposed_change` (append the proposed text as a new section if
  no anchor is given), and returns a `difflib.unified_diff` string with the
  rationale in a header comment. `--dry-run` prints it and writes nothing.
- Refuses cleanly (non-zero, message, no diff) when: proposal not found, status
  ≠ `accepted`, `target_file` is a placeholder (`<target>`), or target missing.
- Test builds a synthetic accepted proposal + temp target, asserts the diff
  contains `--- `, `+++ `, `@@`, and the proposed text; asserts placeholder and
  non-accepted proposals are refused; asserts dry-run leaves the target
  byte-identical.

## 5. Gates

Declared in front-matter: `tests-pass`, `dry-run-renders-diff` (real proposal,
dry-run emits a diff, no write), `files-updated`. The dry-run gate uses
`2026-05-29-scope-expansion-recurring` — diff generation must succeed even
though that target is immutable (the guard refusal is block 153's concern, not
generation's).

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `proposed_change` is free-form AI text with no edit anchor | Med | Default strategy = append as a new `## Proposed amendment (<proposal_id>)` section at EOF; deterministic, always applies cleanly. Anchored edits deferred (§7). |
| Diff generated for an immutable target misleads a reviewer | Low | Generation is guard-agnostic by design; 153 blocks the *write*. Dry-run header notes immutability via `_is_immutable` for reviewer context. |
| `difflib` line-ending drift on Windows (CRLF vs LF) | Low | Read/normalize with `splitlines(keepends=True)`; emit `\n`; covered by a test on CRLF input. |

## 7. Out of Scope

- Any write to disk, backup, or status change (blocks 153/154).
- Anchored / in-place edits driven by structured proposal directives — append
  strategy only this block.
- Multi-file diffs from one proposal (one `target_file` per proposal; phase §10).
- Immutability refusal and integrity-bump enforcement (block 153).

## 8. New Abstraction

`sdk/proposal_apply.py` module with a `ProposalApply` class (mirrors
`ProposalResolver(arch_root)`). Justified: it is the new home for the
apply pipeline that blocks 153–155 extend (guards, rollback, e2e) — three
named consumers satisfy Rule of Three (Axiom Q1). Front-matter parsing is
reused from `proposal_resolver`, not re-implemented.
