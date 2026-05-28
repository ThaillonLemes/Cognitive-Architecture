---
id: block-030
tier: M
kind: feature
phase: phase-5
status: wip
files:
  read:
    - protocols/convention-snippet-generation.md
    - PROTOCOLS.md
    - _syntax.md
    - design/governor-v2.md
  modify: []
  create:
    - sdk/convention_snippet.py
gates:
  - name: snippet-test
    type: cmd
    cmd: "python cognitive-arch/sdk/convention_snippet.py --test"
    expect: "exit 0, 4 kinds tested, all non-empty and distinct"
  - name: files-created
    type: file-changed
    paths: [sdk/convention_snippet.py]
created_at: 2026-05-22
---

# Block 030 — Module: convention snippet generator

- **Tier:** M
- **Kind:** feature
- **Status:** wip

## 1. Purpose

Implement `sdk/convention_snippet.py` — given a block kind string, produces the axiom list and snippet body to embed in a task packet. Follows `protocols/convention-snippet-generation.md` mapping table and format exactly.

## 2. Files

- **Read:** `protocols/convention-snippet-generation.md`, `PROTOCOLS.md`, `_syntax.md`, `design/governor-v2.md`
- **Modify:** none
- **Create:** `sdk/convention_snippet.py`

## 3. Validation

- `python sdk/convention_snippet.py --test` exits 0
- Prints distinct, non-empty snippets for: `doc-only`, `refactor`, `implementation`, `gate`, `discovery`

## 4. Out of scope

- Staleness detection (PROTOCOLS.md hash tracking) — block-035
- Integration with task packet builder — block-031
