---
id: block-121
phase: phase-20
tier: S
status: done
actual_duration_hours: 0.3
duration_source: estimated
tok_actual: 1500
gates_passed: 1/1
created_at: 2026-05-28
---

# Block 121 Retrospective — proposals/ Schema

## 1. What was built

- `governance/proposals/` directory created with `.gitkeep`
- `templates/proposal.md`: complete schema with all required fields + field reference table
- `governance/proposals/index.md`: empty but valid markdown table (append-only)

## 2. Gates

- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- proposed_change field is free-text (not a structured diff format) — keeps it simple and human-readable
- index.md uses same markdown table format as other governance indexes (consistency)

## 4. DX updated

`governance/proposals/` directory. `templates/proposal.md`. `governance/proposals/index.md`.
