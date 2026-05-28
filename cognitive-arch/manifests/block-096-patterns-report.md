---
id: block-096
tier: S
kind: implementation
phase: phase-14
status: pending
security: false
dependencies: [block-095]
files:
  read:
    - sdk/pattern_analyzer.py
    - sdk/pattern_schema.py
    - design/arch-v3.md
  modify: []
  create:
    - sdk/patterns_report.py
    - governance/patterns.md
gates:
  - name: report-generator-created
    type: file-changed
    paths: [sdk/patterns_report.py, governance/patterns.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-095]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-096-patterns-report.md]
created_at: 2026-05-23
---

# Block 096 — patterns.md generator

- **Tier:** S
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Generate `governance/patterns.md` from Pattern records. Human-readable markdown organized by severity. Auto-regenerated each time mining runs (default: every 7 days per Q8). First run produces initial patterns.md from existing 85-block corpus.

## 2. Files

- **Read:** pattern analyzer module + schema, arch-v3 design
- **Modify:** —
- **Create:** `sdk/patterns_report.py` (markdown renderer), `governance/patterns.md` (initial output)

## 3. Validation

- `governance/patterns.md` has structure: header, summary stats, section per pattern type with evidence + severity + last_detected
- Re-running generator produces deterministic output (no spurious diffs)
- Visual inspection of first run against current corpus passes reasonability test

## 4. Out of scope

- Recommendation engine output (block-097 — patterns.md only describes patterns)
- HTML version (Phase 16 dashboard handles that)
- Historical pattern.md versioning (overwrite-only for now)
