---
id: block-003
tier: M
kind: refactor
phase: phase-1
scope: phase-bound
status: done
dependencies: []
files:
  read:
    - PROTOCOLS.md
    - CLAUDE.md
    - INDEX.md
    - README.md
    - phase-0/02-domain-overview.md
  modify:
    - CLAUDE.md
    - INDEX.md
    - README.md
    - phase-0/02-domain-overview.md
  create:
    - decisions/ADR-002-charter-naming.md
gates:
  - name: no-comment-charter-remaining
    type: manual
    description: grep "Comment Charter" across *.md returns 0 matches in non-retrospective, non-roadmap, non-manifest files
  - name: files-updated
    type: file-changed
    paths: [CLAUDE.md, INDEX.md, README.md, phase-0/02-domain-overview.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-20
---

# Block 003 — Disambiguate "Charter" vs "Comment Charter" naming

- **Tier:** M
- **Kind:** refactor
- **Status:** wip

## 1. Purpose

Rename all occurrences of "Comment Charter" to "Charter" to match PROTOCOLS.md (the single source of truth). PROTOCOLS.md uses "Charter" at lines 3 and 47; CLAUDE.md, INDEX.md, README.md, and phase-0/02-domain-overview.md use "Comment Charter". Violation of P3 (single source of truth).

## 2. Dependencies

None (independent of block-001 and block-002 content; does not depend on them logically).

## 3. Files

- **Read:** PROTOCOLS.md, CLAUDE.md, INDEX.md, README.md, phase-0/02-domain-overview.md
- **Modify:** CLAUDE.md, INDEX.md, README.md, phase-0/02-domain-overview.md
- **Create:** decisions/ADR-002-charter-naming.md

## 4. Validation

- grep "Comment Charter" across all .md files returns 0 matches in canonical files (CLAUDE.md, INDEX.md, README.md, PROTOCOLS.md, phase-0/*, templates/*)
- Matches in block retrospectives and roadmap-draft are acceptable (historical record)

## 5. Gates

- `no-comment-charter-remaining` — manual grep check
- `files-updated` — all declared files modified at block-close

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Miss an occurrence | Low | grep before closing block |

## 7. Out of Scope

- Updating any templates that might reference "Comment Charter" (block-005 sweep handles this)
- Updating `phase-0/03-roadmap-draft.md` line 24 (historical description of block-003 — accurate as-is)

## 8. New Abstraction

None.
