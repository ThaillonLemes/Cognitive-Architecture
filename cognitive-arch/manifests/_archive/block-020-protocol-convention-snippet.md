---
id: block-020
tier: S
kind: doc-only
phase: phase-4
status: planned
dependencies: [block-017]
files:
  read:
    - design/governor-v2.md
    - PROTOCOLS.md
    - _syntax.md
  modify: []
  create:
    - protocols/convention-snippet-generation.md
gates:
  - name: protocol-exists
    type: file-exists
    paths: [protocols/convention-snippet-generation.md]
  - name: mapping-table
    type: manual
    description: protocol contains a block-kind to axioms mapping table (which axioms apply to doc-only, refactor, enhancement, etc.)
  - name: snippet-format
    type: manual
    description: protocol shows how to format the axioms: field in a task packet (comma-separated keys)
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 020 — Protocol: convention-snippet-generation

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Dependencies:** block-017

## 1. Purpose

Create `protocols/convention-snippet-generation.md` — the specification for how the Governor selects which axioms to include in a task packet's `axioms:` field. Instead of sending the full PROTOCOLS.md to every sub-agent, the Governor generates a lean "convention snippet" of only the relevant axioms for each block kind.

## 2. Files

- **Read:** design/governor-v2.md (Decision 5), PROTOCOLS.md (all 19 axioms), _syntax.md
- **Modify:** none
- **Create:** protocols/convention-snippet-generation.md

## 3. Spec

`protocols/convention-snippet-generation.md` must cover:

### Purpose of convention snippets
- Reduces context sent to sub-agents
- Ensures sub-agents apply the right axioms for their block kind
- Prevents axiom drift (sub-agents don't guess which rules apply)

### Block-kind to axiom mapping table

| Block kind | Core axioms | Optional axioms |
|------------|-------------|-----------------|
| doc-only | Q1, Q2, Q3, C2 | P1, C1, C6 |
| refactor | Q1, Q2, Q3, Q4, C2, C4 | P3, P5 |
| enhancement | Q1, Q2, Q3, Q5, Q6, C2, C4, C6 | P1, P4 |
| bugfix | Q1, Q3, Q4, Q6, C2, C4 | P5, P6 |
| feature | Q1, Q2, Q3, Q5, Q6, C1, C2, C4, C6 | P1, P4, P6 |

(Governor uses this table to populate `axioms:` in task packet)

### Format
```
axioms:Q1,Q3,Q5,C2   # comma-separated, no spaces, sorted by type (P then Q then C)
```

### Staleness rule
If PROTOCOLS.md changes (axioms added/removed), Governor must regenerate convention snippets. governor-state.md tracks PROTOCOLS.md hash to detect this.

### Manual fallback
If no Governor: implementer manually selects axioms from the mapping table when writing the task packet by hand.

## 4. Out of scope

- Changing the 19 axioms themselves (PROTOCOLS.md is read-only here)
- Per-block custom axiom overrides (Governor always uses the table)
