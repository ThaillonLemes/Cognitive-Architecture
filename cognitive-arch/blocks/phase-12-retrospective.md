---
id: phase-12
status: done
blocks: 4
blocks_done: [block-086, block-087, block-088, block-089]
completed_at: 2026-05-27
exit_criteria_met: 5/5
---

# Phase 12 Retrospective — Foundation Fix

## 1. What was delivered

Four activation blocks that turned dormant v2.5 capabilities into live, session-visible features:

- **block-086** (Velocity activation): `actual_duration_hours` + `duration_source` fields added to retro template; `sdk/velocity_inference.py` created; audit check 9 warns on empty duration.
- **block-087** (ADR reintroduction): 3 backfilled ADRs written (ADR-003: tier S/M/L system; ADR-004: Governor v2 Python SDK; ADR-005: Group M axioms split).
- **block-088** (Security revalidation): `governance/security-status.md` created; S1/S3 COVERED, S2 N/A, S4 WARN (threat model deferred), S5 PARTIAL; overall PASS WITH WARNINGS.
- **block-089** (Health report on boot): CLAUDE.md step 5 added; `protocols/health-on-boot.md` created with 5-line summary format and 1h cache rules.

## 2. Exit criteria check

| Criterion | Met? |
|---|---|
| 1. Template has `actual_duration_hours` + `duration_source` fields; checklist step 5 asks for it | ✓ |
| 2. 3 ADRs in `decisions/` covering tier system, Governor v2 SDK, Group M split; each `backfilled:true` | ✓ |
| 3. `governance/security-status.md` audits S1-S5; gaps flagged | ✓ |
| 4. CLAUDE.md step 5 instructs AI to surface health report at boot | ✓ |
| 5. `audit.sh` warns when blocks close without `actual_duration_hours` (check 9, soft warning) | ✓ |

## 3. Risks that materialized

None. CLAUDE.md budget (60 lines) was tight; managed by removing terminal marker.

## 4. What phase 13 inherits

- `governance/security-status.md` is a good reference for which files are security-adjacent (SDK dispatch, config).
- S4 gap (no threat model) → candidate for phase-13 extension or standalone block.
- Velocity data starts accumulating from block-086 onward; first meaningful velocity report possible after ~10 more blocks.

---

End of phase-12 retrospective.
