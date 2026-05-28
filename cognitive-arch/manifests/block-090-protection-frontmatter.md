---
id: block-090
tier: M
kind: refactor
phase: phase-13
scope: phase-bound
status: pending
security: false
dependencies: []
files:
  read:
    - design/arch-v3.md
    - PROTOCOLS.md
    - _syntax.md
    - templates/manifest-small.md
    - templates/manifest-medium.md
    - templates/manifest-large.md
    - templates/block-retrospective.md
    - protocols/block-close-checklist.md
    - protocols/pointer-integrity.md
    - audit.sh
    - CLAUDE.md
    - INDEX.md
  modify:
    - PROTOCOLS.md
    - _syntax.md
    - templates/manifest-small.md
    - templates/manifest-medium.md
    - templates/manifest-large.md
    - templates/block-retrospective.md
    - protocols/block-close-checklist.md
    - protocols/pointer-integrity.md
  create: []
gates:
  - name: all-immutable-files-tagged
    type: file-changed
    paths: [PROTOCOLS.md, _syntax.md, templates/manifest-small.md, templates/manifest-medium.md, templates/manifest-large.md, templates/block-retrospective.md, protocols/block-close-checklist.md, protocols/pointer-integrity.md]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-090-protection-frontmatter.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 090 — Protection frontmatter

- **Tier:** M
- **Kind:** refactor
- **Status:** pending

## 1. Purpose

Add `protection:` field to frontmatter of all critical files per design/arch-v3.md §4. Three tiers: `immutable`, `guarded`, `open`. This block tags the immutable set explicitly; guarded files get tagged separately if needed (default behavior is `open`).

## 2. Dependencies

None. First block of Phase 13.

## 3. Files

- **Read:** All files in design/arch-v3.md §4 lists (to verify identity before tagging)
- **Modify:** 8 files marked `immutable` in design — add YAML frontmatter `protection: immutable` + `protection_reason` + `restore_command`
- **Create:** —

## 4. Validation

- Each modified file's YAML frontmatter (or top of file for those without) includes `protection: immutable`
- `protection_reason` field present with 1-sentence explanation
- File content (below frontmatter) unchanged — verify with diff inspection
- All 8 immutable files tagged

## 5. Gates

See YAML frontmatter. Note: audit.sh check 9 (integrity-lock) is NOT yet enforced — it lands in block-091.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Adding frontmatter to file that doesn't currently have it breaks parsers | Med | Files like audit.sh use bash comment style; PROTOCOLS.md already markdown — verify each pre-modify |
| Forgetting a file from the immutable list | Low | Cross-check with design doc §4 explicitly |

## 7. Out of Scope

- Tagging `guarded` files (separate concern, may be implicit-default with no tag for v1)
- Enforcement (block-091 lock + block-092 protocol handle that)
- Restoration mechanism (block-093)

## 8. New Abstraction

`protection:` field is a new vocabulary item. Justification: appears across 8 files + 2 protocols + 1 command. Rule of Three clearly met.
