---
id: block-049
tier: S
kind: doc-only
phase: phase-6
status: done
dependencies:
  - block-048
files:
  read:
    - protocols/stack-addenda/python-fastapi.md
    - PROTOCOLS.md
  modify: []
  create:
    - protocols/stack-addenda/node-express.md
gates:
  - name: file-created
    type: file-changed
    paths: [protocols/stack-addenda/node-express.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 049 — Stack addendum: Node / Express

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Create `protocols/stack-addenda/node-express.md` covering Node.js / Express conventions: folder structure (`src/routes/`, `src/middleware/`, `src/models/`), naming (camelCase modules, kebab-case files), test runner (`jest` or `vitest`), linter (`eslint`), and HOT file additions for Node projects.

## 2. Files

- **Read:** `protocols/stack-addenda/python-fastapi.md` (format reference), `PROTOCOLS.md`
- **Modify:** none
- **Create:** `protocols/stack-addenda/node-express.md`

## 3. Validation

- `protocols/stack-addenda/node-express.md` exists
- Same section structure as prior addenda
- Covers ES module (`import/export`) vs CommonJS (`require`) decision point
- No library version numbers pinned
- Total length ≤ 80 lines

## 4. Out of scope

- NestJS or other Node frameworks (separate addenda)
- ORM conventions (Prisma, Sequelize) — too opinionated; leave as notes only
- Deployment / PM2 / Docker
