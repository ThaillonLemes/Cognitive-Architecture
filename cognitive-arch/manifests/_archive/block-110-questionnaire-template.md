---
id: block-110
tier: S
kind: implementation
phase: phase-17
status: pending
security: false
dependencies: [block-109]
files:
  read:
    - protocols/brainstorm-pattern.md
    - sdk/brainstorm_predictor.py
    - sdk/prediction_schema.py
    - design/arch-v3.md
    - _brainstorm/v3-evolution-questionnaire.md
  modify:
    - protocols/brainstorm-pattern.md
  create:
    - templates/brainstorm-v2-questionnaire.md
    - protocols/brainstorm-pattern-v2.md
gates:
  - name: template-and-protocol-created
    type: file-changed
    paths: [templates/brainstorm-v2-questionnaire.md, protocols/brainstorm-pattern-v2.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-109]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-110-questionnaire-template.md]
created_at: 2026-05-23
---

# Block 110 — Questionnaire template w/ predictions

- **Tier:** S
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Update `protocols/brainstorm-pattern.md` to v2 (or create coexisting v2 doc per Q15-3 decision) reflecting the three principles: always recommend, variable option count, open answers always permitted. Create `templates/brainstorm-v2-questionnaire.md` showing the rendering with predictions inline.

## 2. Files

- **Read:** existing brainstorm-pattern.md, predictor module + schema, arch-v3, sample v3 questionnaire (as example to retroactively render with predictions)
- **Modify:** `protocols/brainstorm-pattern.md` (mark v1 as deprecated, point to v2)
- **Create:** `templates/brainstorm-v2-questionnaire.md` (template), `protocols/brainstorm-pattern-v2.md` (specification)

## 3. Validation

- Protocol v2 covers all 3 principles with concrete examples
- Template shows: question, AI recommendation with confidence band, rationale, variable-count options, open-answer hint
- Sample rendering of one question from v3-evolution included as example
- v1 protocol clearly marked deprecated with pointer to v2

## 4. Out of scope

- Synthesis automation (block-111)
- Retroactive conversion of existing brainstorms (v3 questionnaire stays as v1-format)
- Multi-language support
