---
id: block-117
tier: M
kind: implementation
phase: phase-19
scope: phase-bound
status: planned
security: false
dependencies:
  - block-111
files:
  read:
    - sdk/brainstorm_synthesis.py
    - templates/ADR.md
    - design/
  modify: []
  create:
    - sdk/adr_drafter.py
    - sdk/tests/test_adr_drafter.py
    - design/adrs/.gitkeep
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: lint-pass
    cmd: python -m flake8 sdk/adr_drafter.py --max-line-length=120
    expect: "0 errors"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-117-adr-drafter.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-111]
created_at: 2026-05-28
parallel_with: [block-119]
---

# Block 117 — adr_drafter.py Core

- **Tier:** M
- **Kind:** implementation
- **Status:** planned
- **Parallel-with:** block-119

## 1. Purpose

Build sdk/adr_drafter.py: reads a brainstorm synthesis JSON file, finds decisions with significance:high or significance:medium, generates an ADR scaffold for each and saves to design/adrs/YYYY-MM-DD-<slug>.md. The draft includes: title, status:draft, synthesis_source reference, options_considered list, recommended_option, confidence_band, and a rationale placeholder. Never overwrites existing ADR files.

## 2. Dependencies

- block-111: brainstorm_synthesis.py exists and produces structured output (phase-17 deliverable)

## 3. Files

- **Read:** sdk/brainstorm_synthesis.py (output schema), templates/ADR.md (field reference)
- **Modify:** None
- **Create:** sdk/adr_drafter.py, sdk/tests/test_adr_drafter.py, design/adrs/.gitkeep (directory init)

## 4. Validation

- Feed a test synthesis JSON with 2 significant decisions — confirm 2 ADR files created in design/adrs/
- Feed synthesis JSON with 0 significant decisions — confirm 0 files created
- Run adr_drafter twice on same synthesis — confirm no overwrite (unique slug with counter suffix)
- ADR files have all required fields: title, status:draft, synthesis_source, options_considered, recommended_option, confidence_band
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, lint-pass, files-updated, dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Synthesis JSON schema changes in future phases | Low | adr_drafter reads via stable keys; adds `schema_version` check |
| Slug collision if two ADRs created same second | Low | Add incrementing counter suffix if file exists |
| design/adrs/ missing from repo | Low | adr_drafter creates directory if missing |

## 7. Out of Scope

- Generating ADRs from sources other than brainstorm synthesis
- ADR content quality validation (human responsibility)
- Publishing ADRs externally

## 8. New Abstraction

`AdrDrafter.generate(synthesis_path, arch_root)` — reads synthesis JSON, returns list of created file paths. `_make_slug(title)` — title to filesystem-safe slug. Both in sdk/adr_drafter.py.
