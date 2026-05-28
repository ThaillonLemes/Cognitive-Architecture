---
id: block-119
phase: phase-19
tier: S
status: done
actual_duration_hours: 0.3
duration_source: estimated
tok_actual: 1400
gates_passed: 1/1
created_at: 2026-05-28
---

# Block 119 Retrospective — templates/ADR-auto.md

## 1. What was built

- `templates/ADR-auto.md`: complete schema for auto-generated ADR scaffolds
- Extends templates/ADR.md with: synthesis_source, significance, confidence_band, recommended_option, auto_generated
- Field reference table marking AI-populated vs human-required fields
- Clear annotation that status is always draft until human accepts

## 2. Gates

- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- Template kept additive: core ADR.md fields preserved; auto-specific fields appended
- Added note: "Core fields inherited from templates/ADR.md — keep in sync"
- HUMAN REQUIRED comments clearly mark what the human must fill before accepting

## 4. DX updated

`templates/ADR-auto.md` created.
