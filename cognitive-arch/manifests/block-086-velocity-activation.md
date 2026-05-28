---
id: block-086
tier: M
kind: implementation
phase: phase-12
scope: phase-bound
status: pending
security: false
dependencies: []
files:
  read:
    - templates/block-retrospective.md
    - protocols/block-close-checklist.md
    - blocks/BLOCK_LOG.md
    - design/arch-v3.md
  modify:
    - templates/block-retrospective.md
    - protocols/block-close-checklist.md
    - audit.sh
  create:
    - sdk/velocity_inference.py
gates:
  - name: template-has-duration-field
    type: file-changed
    paths: [templates/block-retrospective.md]
  - name: checklist-asks-duration
    type: file-changed
    paths: [protocols/block-close-checklist.md]
  - name: audit-warns-empty-duration
    type: file-changed
    paths: [audit.sh]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-086-velocity-activation.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 086 — Velocity activation

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Activate the velocity tracking subsystem that exists in v2.5 but produces "INSUFFICIENT DATA — 0 blocks" because `actual_duration_hours` was never collected. Add the field to the retrospective template, update block-close to capture it (with hybrid auto-infer + manual override per Q1), and update audit to warn when empty.

## 2. Dependencies

None. First block of Phase 12.

## 3. Files

- **Read:** `templates/block-retrospective.md`, `protocols/block-close-checklist.md`, `blocks/BLOCK_LOG.md`, `design/arch-v3.md`
- **Modify:** `templates/block-retrospective.md` (add `actual_duration_hours` + `duration_source` fields), `protocols/block-close-checklist.md` (step 5 captures duration), `audit.sh` (new soft warning for empty duration on closed blocks)
- **Create:** `sdk/velocity_inference.py` (estimates duration from git commit timestamps of files in block scope)

## 4. Validation

- `templates/block-retrospective.md` contains `actual_duration_hours: <number>` and `duration_source: manual|auto-inferred|estimated` in the YAML frontmatter section.
- `protocols/block-close-checklist.md` step 5 has explicit instruction to fill duration field (auto-inferred shown as suggestion).
- `audit.sh` includes a check that scans last 30 closed blocks; warns if any have empty `actual_duration_hours`.
- `sdk/velocity_inference.py` is importable, has unit-testable function `infer_duration(block_id) -> tuple[float, str]`.

## 5. Gates

See YAML frontmatter. All must pass before block-close commit.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Auto-inference from git timestamps wrong when block work was non-continuous | Med | `duration_source: auto-inferred` flag makes inference transparency; user can override |
| Retro template change breaks downstream tooling | Low | Existing fields preserved; new fields are additive |

## 7. Out of Scope

- Backfilling `actual_duration_hours` on the 85 historical blocks (out of scope; left empty marked as legacy)
- Retroactive last-10-blocks estimate (deferred to phase-12 retrospective or block-088 health work)
- Visualization of velocity (Phase 16 — dashboard)

## 8. New Abstraction

`velocity_inference.py` is a new SDK module. Justification (Rule of Three): velocity needs to be inferable from git history for 3 distinct callers: block-close prompt, audit warning, health-report. Centralizing logic is correct now per Q1.
