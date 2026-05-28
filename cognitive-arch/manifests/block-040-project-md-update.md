---
id: block-040
tier: S
kind: doc-only
phase: phase-6
status: done
dependencies:
  - block-039
files:
  read:
    - PROJECT.md
    - STATE.md
  modify:
    - PROJECT.md
  create: []
gates:
  - name: file-updated
    type: file-changed
    paths: [PROJECT.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 040 — PROJECT.md freshness update

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Update `PROJECT.md` frontmatter so it reflects the actual current state: `current_phase: Phase 6`, `last_updated: 2026-05-22`, `status: active`. Also update the Pointers section to include `sdk/` and `phases/phase-6.md`, and fix the Status transitions note to reflect Phase 5 completion.

## 2. Files

- **Read:** `PROJECT.md`, `STATE.md` (for authoritative current values)
- **Modify:** `PROJECT.md`
- **Create:** none

## 3. Validation

- `PROJECT.md` frontmatter `current_phase` equals `Phase 6`
- `PROJECT.md` frontmatter `last_updated` is `2026-05-22`
- `PROJECT.md` Pointers section mentions `sdk/` with a brief
- No placeholder text (`<placeholder>`, `N/A` where values are now known) remains

## 4. Out of scope

- Changing the project vision or target-user sections
- Adding new sections beyond what the template defines
- Updating the roadmap (that's block-043)
