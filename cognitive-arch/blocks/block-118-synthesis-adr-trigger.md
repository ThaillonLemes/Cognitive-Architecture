---
id: block-118
phase: phase-19
tier: S
status: done
actual_duration_hours: 0.5
duration_source: estimated
tok_actual: 2200
gates_passed: 2/2
created_at: 2026-05-28
---

# Block 118 Retrospective — synthesis → ADR Trigger

## 1. What was built

- `write_design_doc()` in `sdk/brainstorm_synthesis.py` extended with `decisions` and `no_adr` params
- Post-synthesis ADR trigger: if decisions provided and `no_adr=False`, calls `AdrDrafter(root).generate(decisions)`
- Auto-fills `synthesis_source` on decisions that lack it (uses output.design_path)
- Import failure wrapped in `try/except` — ADR failure never blocks synthesis
- `--no-adr` CLI flag added to brainstorm_synthesis.py

## 2. Gates

- tests-pass: 565 passed, 0 failed ✓
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- `decisions` parameter added to `write_design_doc()` (optional; backwards-compatible; None = no-op)
- ADR trigger is post-doc-write: synthesis doc always written regardless of ADR outcome

## 4. DX updated

`sdk/brainstorm_synthesis.py` — `write_design_doc()` extended, `--no-adr` CLI flag added.
