---
id: block-008
tier: S
kind: refactor
phase: phase-2
status: planned
dependencies: []
files:
  read:
    - templates/block-retrospective.md
    - _syntax.md
  modify:
    - templates/block-retrospective.md
  create: []
gates:
  - name: tok-fields-present
    type: manual
    description: templates/block-retrospective.md frontmatter includes tok_estimated and tok_src fields
  - name: files-updated
    type: file-changed
    paths: [templates/block-retrospective.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 008 — Retrospective template — token fields

- **Tier:** S
- **Kind:** refactor
- **Status:** planned

## 1. Purpose

Add `tok_estimated:` and `tok_src:` fields to `templates/block-retrospective.md` frontmatter. Every block retro from Phase 2 onward records estimated token cost so the architecture can track its own operational cost over time.

## 2. Files

- **Read:** templates/block-retrospective.md, _syntax.md
- **Modify:** templates/block-retrospective.md (add tok fields to frontmatter + section prompt)
- **Create:** none

## 3. Spec

Add to frontmatter:
```yaml
tok_estimated: ~NNN   # chars/4 estimate for files read during this block
tok_src: estimated    # always "estimated" until Phase 5 SDK measurement
```

Add to the retrospective body (token section or Notes section):
- Prompt: "Estimate tokens consumed: list files read, count chars/4, sum total."
- Format: `tok_estimated: ~NNN tok_src:estimated`

## 4. Validation

- `templates/block-retrospective.md` frontmatter has `tok_estimated:` and `tok_src:` placeholders
- A human-readable note explains the chars/4 proxy method

## 5. Out of scope

- Actual SDK measurement (Phase 5)
- Per-block token budget gates
