---
id: block-048
tier: S
kind: doc-only
phase: phase-6
status: done
dependencies:
  - block-047
files:
  read:
    - protocols/stack-addenda/python-fastapi.md
    - PROTOCOLS.md
  modify: []
  create:
    - protocols/stack-addenda/react-nextjs.md
gates:
  - name: file-created
    type: file-changed
    paths: [protocols/stack-addenda/react-nextjs.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 048 — Stack addendum: React / Next.js

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Create `protocols/stack-addenda/react-nextjs.md` following the same structure as `python-fastapi.md`. Covers: project structure conventions (`app/`, `components/`, `lib/`), naming (PascalCase components, kebab-case files), test runner (`vitest` or `jest`), linter (`eslint`), HOT file additions for React projects.

## 2. Files

- **Read:** `protocols/stack-addenda/python-fastapi.md` (format reference), `PROTOCOLS.md`
- **Modify:** none
- **Create:** `protocols/stack-addenda/react-nextjs.md`

## 3. Validation

- `protocols/stack-addenda/react-nextjs.md` exists
- Same section structure as `python-fastapi.md` (BRIEF, `as_of:`, Setup, Naming, Test, Lint, HOT additions, Code Header example)
- Covers Next.js App Router conventions (not Pages Router)
- No library version numbers pinned
- Total length ≤ 80 lines

## 4. Out of scope

- React Native / Expo (separate addendum)
- Next.js Pages Router conventions
- Backend API routes in depth (those belong to a Node addendum)
- Deployment (Vercel, etc.)
