---
id: block-111
tier: M
kind: implementation
phase: phase-17
scope: phase-bound
status: pending
security: false
dependencies: [block-109, block-110]
files:
  read:
    - sdk/brainstorm_predictor.py
    - sdk/brainstorm_context.py
    - sdk/prediction_schema.py
    - templates/brainstorm-v2-questionnaire.md
    - design/arch-v3.md
  modify: []
  create:
    - sdk/brainstorm_synthesis.py
    - sdk/tests/test_brainstorm_synthesis.py
    - protocols/brainstorm-synthesis.md
gates:
  - name: synthesis-module
    type: file-changed
    paths: [sdk/brainstorm_synthesis.py, protocols/brainstorm-synthesis.md]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_brainstorm_synthesis.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-109, block-110]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-111-synthesis-automation.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 111 — Synthesis automation

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

After user confirms (or modifies) predictions across a brainstorm, automatically generate the final `design/<topic>.md` document. Handles three answer types: accepted predictions, modified predictions, free-text answers — synthesizes them into coherent design doc.

## 2. Dependencies

- block-109 (predictions are input)
- block-110 (template defines expected answer formats)

## 3. Files

- **Read:** predictor module, context module, prediction schema, v2 questionnaire template, arch-v3
- **Modify:** —
- **Create:** `sdk/brainstorm_synthesis.py`, test file, `protocols/brainstorm-synthesis.md` (procedure doc)

## 4. Validation

- Synthesis takes: questionnaire with answers (accepted/modified/free) → produces design markdown
- Output design has structured sections: context, decisions table, rationale, dependencies, references
- Round-trip test: synthesize from sample answers; resulting design doc is human-readable and complete
- Handles mixed answer types correctly: option `A1=2` accepted; option `A2=3+modifier` integrated; option `B5=open free text` synthesized

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Synthesis distorts user intent | High | Each section cites source answer; user reviews before commit |
| Free-text answers integrated incorrectly | Med | Test suite covers mixed cases; conservative synthesis preserves verbatim where possible |
| Auto-generated design too generic | Med | Template inherits structure from arch-v3.md as exemplar of good design doc |

## 7. Out of Scope

- Auto-commit of generated design (always requires user review)
- ADR auto-creation from design (user authors ADRs separately per Phase 12)
- Multi-topic synthesis (one brainstorm = one design)
- Versioning of design docs (overwrite-on-update)

## 8. New Abstraction

`SynthesisEngine`. Justification: consumed by user invocation, by Master Agent (orchestrates brainstorms in future), by potential CI automation. Past Rule of Three.
