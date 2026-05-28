# Block Complexity Estimator

BRIEF: Heuristic decision tree for assigning S, M, or L tier to a block before writing its manifest. Use this when a phase is generated and each block needs a tier assigned, or when reviewing a block whose tier feels wrong.

---

## Tier Definitions

| Tier | Label | Typical duration | Description |
|------|-------|-----------------|-------------|
| S | Small | 0.5–2 hours | Single-focus, single artifact, no tests required, contained impact |
| M | Medium | 2–6 hours | Multi-file, requires tests OR involves protocol + code together |
| L | Large | 6–12 hours | Cross-module, tests + code + protocol, significant design decisions |

If a block would exceed 12 hours: split it into two or more blocks.

---

## Decision Tree

### Is this block SMALL (S)?

All 5 of the following must be true:

1. **Single primary artifact** — creates or modifies ONE file as the main deliverable (other files are ancillary updates, e.g., updating INDEX.md).
2. **No automated tests required** — the gate does not require running `pytest` or any test suite; verification is by file existence or grep.
3. **No SDK/production code changes** — the block writes markdown, configuration, or documentation only; no `.py`, `.ts`, `.go`, etc. files are in `files.modify` or `files.create`.
4. **All read files are scannable** — the block does not require deep reading of large code files; reading is for context, not for understanding complex logic.
5. **Estimated duration ≤ 2 hours** — if you honestly estimate more than 2 hours, it is not S.

→ If all 5 are true: assign **S**.

---

### Is this block MEDIUM (M)?

At least 3 of the following must be true:

1. **2–5 files modified or created** (across modify + create combined).
2. **Automated tests required** — gate includes `pytest` or equivalent test runner.
3. **Protocol AND code in same block** — both a new markdown protocol and a new/modified code file are deliverables.
4. **Existing module must be read and understood** — not just scanned; requires understanding logic flow to make the change safely.
5. **Estimated duration 2–6 hours** — honest estimate falls in this range.

→ If ≥ 3 are true (and not all 5 S criteria are true): assign **M**.

---

### Is this block LARGE (L)?

At least 1 of the following must be true:

1. **6+ files total** — across read + modify + create, the block touches 6 or more files.
2. **Cross-module impact** — the block changes a public API, shared data structure, or protocol that other modules depend on; requires checking call sites.
3. **Tests + code + protocol all required** — all three artifact types are present: new test file, new/modified code, new/modified protocol.
4. **Estimated duration 6–12 hours** — honest estimate.
5. **Regression gate required** — the block must run the full test suite (not just new tests) because of cross-module risk.

→ If any 1 is true: assign **L**.

---

## Split Triggers

A block must be split (regardless of tier assignment) if ANY of the following apply:

- **> 8 files** across read + modify + create → split at the natural boundary (e.g., protocol file in one block, code implementation in another).
- **> 12 hours estimated** → mandatory split; no L block should exceed 12 hours.
- **Two distinct deliverables** that could each be a standalone block → split; do not combine.
- **Simultaneous protocol change + API change** — if a block both defines a new protocol AND changes an existing public API, split: protocol first, then API change depending on it.

---

## Examples

| Block description | Files | Tests? | Code? | Tier |
|-------------------|-------|--------|-------|------|
| Create `protocols/phase-quality-rubric.md` | 2 (new protocol + command update) | No | No | **S** |
| Add `validate_rubric()` to `return_validator.py` + tests | 3 (protocol + code + test) | Yes | Yes | **M** |
| Add `dispatch_batch()` to `dispatch.py` + SDK tests + parallel governor flag | 5 (code + test + governor) | Yes | Yes | **M→L** (regression gate) |
| Add `--track` flag to `governor.py` + track dispatch tests | 4 (governor + dispatch + test + fixtures) | Yes | Yes | **M** |

---

## When to use this estimator

1. **During phase generation** — when listing blocks, assign tier immediately using this estimator.
2. **When writing a manifest** — confirm the tier is correct before writing the frontmatter.
3. **During block review** — if a block is taking longer than expected, check: should this have been M instead of S? Split if necessary.

---

## Out of scope

- Estimating calendar time (that is `commands/velocity.md`).
- Evaluating whether the phase as a whole is well-scoped (that is `protocols/phase-quality-rubric.md`).
- Defining execution procedure within a block (that is `protocols/block-execution-sparc.md`).

End of block-complexity-estimator.md.
