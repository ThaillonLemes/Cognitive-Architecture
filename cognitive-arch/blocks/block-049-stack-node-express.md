---
id: block-049
manifest: manifests/block-049-stack-node-express.md
status: done
gates_passed: 1/1
completed_at: 2026-05-22T06:52Z
agent: implementer
commit: -
duration_actual_days: 0
tok_estimated: ~300
tok_src: estimated
---

# Block 049 Retrospective — Stack addendum: Node / Express

## 1. What was built

- Created `protocols/stack-addenda/node-express.md`
- Covers: project setup (npm init, TypeScript, ts-node), naming conventions (camelCase or kebab-case — pick one), layered project structure (controllers/services/routes/middleware), jest/vitest test command, ESLint lint command, HOT file additions, TypeScript code header, ES module vs CommonJS decision point note

## 2. Tests added

None (doc-only).

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| file-created | ✓ | protocols/stack-addenda/node-express.md created; BRIEF + as_of: + 8 sections |

## 4. Decisions made

- Flagged ES module vs CommonJS as a decision that must be made in Phase 0 — this is the most common source of confusion in Node projects
- Recommended TypeScript over plain JS (ts-node + tsconfig) for cognitive-arch compatibility

## 5. Deferred to future blocks

- NestJS addendum (separate file if needed; significantly different structure)

## 6. Token estimate

```
tok_estimated: ~300  tok_src:estimated
```

## 7. Issues / surprises

None.

## 8. Files actually touched

As manifest.
