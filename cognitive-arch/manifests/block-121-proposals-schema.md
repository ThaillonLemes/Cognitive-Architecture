---
id: block-121
tier: S
kind: doc-only
phase: phase-20
status: planned
security: false
files:
  read:
    - governance/patterns.md
    - templates/ADR.md
  modify: []
  create:
    - governance/proposals/.gitkeep
    - templates/proposal.md
    - governance/proposals/index.md
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
---

# Block 121 — proposals/ Schema

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Define the governance/proposals/ directory structure and the proposal.md schema. A proposal is a formal, structured suggestion to update a governance or protocol file, generated when a pattern exceeds threshold. Fields: id, status (pending|accepted|rejected), pattern_id, target_file, proposed_change, rationale, created_at, resolved_at, resolved_by. Create governance/proposals/index.md (initially empty table).

## 2. Dependencies

None (first block of phase-20).

## 3. Files

- **Read:** governance/patterns.md (pattern field reference), templates/ADR.md (schema format inspiration)
- **Modify:** None
- **Create:** governance/proposals/.gitkeep (directory), templates/proposal.md, governance/proposals/index.md

## 4. Validation

- governance/proposals/ directory exists
- templates/proposal.md has all required fields documented
- governance/proposals/index.md is valid markdown table (empty but valid)
- `python -c "import yaml; yaml.safe_load(open('templates/proposal.md').read().split('---')[1])"` — valid YAML frontmatter

## 5. Gates

- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md changed

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Schema too rigid, blocks future proposal types | Low | proposed_change field is free-text; schema extensible via optional fields |

## 7. Out of Scope

- Proposal content validation (done in block-122)
- Proposal rendering in dashboard (block-124)

## 8. New Abstraction

None. Schema + directory only.
