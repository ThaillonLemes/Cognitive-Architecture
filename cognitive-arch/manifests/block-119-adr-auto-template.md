---
id: block-119
tier: S
kind: doc-only
phase: phase-19
status: planned
security: false
files:
  read:
    - templates/ADR.md
  modify: []
  create:
    - templates/ADR-auto.md
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
parallel_with: [block-117]
---

# Block 119 — templates/ADR-auto.md

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Parallel-with:** block-117

## 1. Purpose

Create templates/ADR-auto.md: the schema for auto-generated ADR scaffolds. Extends templates/ADR.md with auto-specific fields: synthesis_source (link to brainstorm synthesis file), options_considered (list of options from synthesis), recommended_option (AI recommendation), confidence_band (high/medium/low from brainstorm predictor), and rationale (placeholder for human to fill). Documents which fields are AI-populated vs human-required.

## 2. Dependencies

None (can run in parallel with block-117; adr_drafter.py reads this template).

## 3. Files

- **Read:** templates/ADR.md (base format reference)
- **Modify:** None (templates/ADR.md is immutable — do not touch)
- **Create:** templates/ADR-auto.md

## 4. Validation

- templates/ADR-auto.md exists and is valid markdown
- All core ADR fields present (id, status, title, context, decision, consequences)
- Auto-specific fields present: synthesis_source, options_considered, recommended_option, confidence_band
- Field annotations clearly mark AI-populated vs human-required fields

## 5. Gates

- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md changed

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Template diverges from manual ADR.md over time | Low | Comment in ADR-auto.md: "Core fields inherited from templates/ADR.md — keep in sync" |

## 7. Out of Scope

- Modifying the existing templates/ADR.md (immutable)
- Auto-generated ADR validation schema (human reviews before accepting)

## 8. New Abstraction

None. Documentation file only.
