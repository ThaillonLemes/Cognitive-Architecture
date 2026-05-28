---
id: block-047
tier: S
kind: doc-only
phase: phase-6
status: done
dependencies:
  - block-046
files:
  read:
    - protocols/code-header-protocol.md
    - PROTOCOLS.md
    - _syntax.md
  modify: []
  create:
    - protocols/stack-addenda/python-fastapi.md
gates:
  - name: file-created
    type: file-changed
    paths: [protocols/stack-addenda/python-fastapi.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 047 — Stack addendum: Python / FastAPI

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Create `protocols/stack-addenda/python-fastapi.md` — the first stack addendum. This file gives Python/FastAPI-specific conventions to overlay on top of the generic cognitive architecture: virtual environment setup, module naming, test runner (`pytest`), linter (`ruff`), and any FastAPI-specific HOT/WARM file additions.

## 2. Files

- **Read:** `protocols/code-header-protocol.md`, `PROTOCOLS.md`, `_syntax.md`
- **Modify:** none
- **Create:** `protocols/stack-addenda/python-fastapi.md` (and implicitly the `protocols/stack-addenda/` directory)

## 3. Validation

- `protocols/stack-addenda/python-fastapi.md` exists
- Document has BRIEF, `as_of:` date, and sections: Setup, Naming Conventions, Test Command, Lint Command, HOT file additions, Code Header example
- No library version numbers pinned (conventions only, not `fastapi==0.x.x`)
- Total length ≤ 80 lines

## 4. Out of scope

- FastAPI deployment / Docker instructions
- Pinning specific library versions
- CI/CD pipeline configuration
- Coverage of all Python projects (this addendum is specifically FastAPI; Django etc. would be separate)
