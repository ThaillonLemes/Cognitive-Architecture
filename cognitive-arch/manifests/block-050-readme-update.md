---
id: block-050
tier: M
kind: doc-only
phase: phase-6
scope: phase-bound
status: done
dependencies:
  - block-049
files:
  read:
    - README.md
    - RETROFIT.md
    - BOOTSTRAP.md
    - protocols/stack-addenda/python-fastapi.md
    - protocols/stack-addenda/react-nextjs.md
    - protocols/stack-addenda/node-express.md
    - design/governor-v2.md
  modify:
    - README.md
  create: []
gates:
  - name: readme-updated
    type: file-changed
    paths: [README.md]
  - name: file-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 050 — Update README.md for new adopters (v2.0)

- **Tier:** M
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Update root `README.md` to reflect Governor v2 capabilities, the two-tier architecture, and the three stack addenda. The README is the first thing a new adopter reads; it must explain what the architecture is, how to bootstrap or retrofit, which governor mode to choose, and where to find stack-specific guidance — all in ≤ 130 lines.

## 2. Dependencies

`block-049` — all three stack addenda must exist before README can link to them.

## 3. Files

- **Read:** `README.md` (current content to preserve what's good), `RETROFIT.md`, `BOOTSTRAP.md`, all three stack addenda, `design/governor-v2.md`
- **Modify:** `README.md`
- **Create:** none

## 4. Validation

- `README.md` ≤ 130 lines after update
- Contains sections: What it is, Quick start (BOOTSTRAP or RETROFIT link), Governor v2 (manual vs SDK), Stack addenda (links to all 3), File structure overview
- Links to `BOOTSTRAP.md`, `RETROFIT.md`, `protocols/stack-addenda/` are valid paths
- Governor v2 section explains `governor_mode` flag and SDK install in ≤ 15 lines
- No placeholder text; no stale v1.x-only language

## 5. Gates

- `README.md` file changed
- Standard block-close files updated

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| README grows beyond 130 lines | Low | Write summary-only; all detail lives in RETROFIT/BOOTSTRAP/design |
| Links to stack-addenda files use wrong paths | Low | Verify paths against actual created files from blocks 047–049 |

## 7. Out of scope

- Creating a separate ONBOARDING.md (update README.md in place)
- Adding screenshots or diagrams
- Writing a CONTRIBUTING.md
- Documenting Phase 7 features (async dispatch, pytest) — not implemented yet

## 8. New Abstraction

None. This is a documentation update only.
