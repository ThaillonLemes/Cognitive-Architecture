---
id: phase-12
status: planned
prev_phase: phase-11
exit_criteria_count: 5
blocks_count: 4
estimated_duration_days: 4
created_at: 2026-05-23
last_updated: 2026-05-23
owner: implementer
---

# Phase 12 — Foundation Fix

BRIEF: Activate dormant capabilities. Velocity, ADRs, security review, and health report — features that exist in the architecture but are not used in day-to-day flow.

## 1. Purpose

Phases 1-11 built a rich set of capabilities. A v3 brainstorm revealed that several are technically present but never activated: `actual_duration_hours` is empty across 85 blocks, ADRs are not being written despite the template existing, security review hasn't been revalidated since Phase 10, and the health report is generated but never consulted. Phase 12 closes this activation gap before adding new capabilities in subsequent phases.

## 2. Goals

- Velocity data starts accumulating: every new block records actual duration
- ADR creation becomes part of natural flow: 3 historical decisions backfilled as worked examples
- Security review revalidates against current code: any drift in S1-S5 coverage identified
- Health report visible at start of every session: not a buried command anymore
- No new features added beyond what's needed to activate existing ones

## 3. Invariants

- No existing template structure broken (Phase 13 enforces this, but Phase 12 respects it)
- `BLOCK_LOG.md` remains append-only
- All existing 85 blocks remain immutable (only new template fields added)

## 4. Dependencies

- Phase 11 closed and merged
- `cognitive-arch v2.5` baseline in place
- Decision document `design/arch-v3.md` exists

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Adding `actual_duration_hours` retroactively to old retros could distort velocity metrics | Med | Backfill only last 10 blocks with explicit `inferred:true` flag; older blocks left empty |
| ADR backfilling could misrepresent original intent | Low | ADRs marked `backfilled:true` with date; current ADR template gets `retroactive: bool` field |
| Health report on boot adds latency to session start | Low | Cache report 1h; only regenerate if stale or audit changed |

## 7. Exit Criteria

1. `templates/block-retrospective.md` has `actual_duration_hours` and `duration_source: manual|auto-inferred|estimated` fields; `protocols/block-close-checklist.md` step 5 asks for it.
2. At least 3 ADRs exist in `decisions/` covering: (a) Tiers S/M/L manifest system, (b) Governor v2 Python SDK, (c) Group M cognitive-arch-as-axiomas split. Each marked `backfilled: true`.
3. `governance/security-status.md` exists and audits S1-S5 against current code in cognitive-arch + 4 MMORPG sub-repos; any gaps flagged.
4. `CLAUDE.md` instructs AI to run health report (or read cached version) as part of HOT boot. Output visible in session start.
5. `audit.sh` updated: warns when blocks close without `actual_duration_hours` filled (soft warning, not fail).

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-086 | Velocity activation | M | planned | `manifests/block-086-velocity-activation.md` |
| block-087 | ADR reintroduction | S | planned | `manifests/block-087-adr-reintroduction.md` |
| block-088 | Security review revalidation | S | planned | `manifests/block-088-security-revalidation.md` |
| block-089 | Health report on boot | S | planned | `manifests/block-089-health-report-on-boot.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 2
  groups:
    - id: 12A
      blocks: [block-086, block-087, block-088]
      type: parallel
      depends_on: []
    - id: 12B
      blocks: [block-089]
      type: sequential
      depends_on: [12A]
```

block-089 reads outputs from 086-088 (template changes + ADRs + security-status) to compose the boot-time health summary.

## 10. Out of Scope

- Master Agent capabilities (Phase 15)
- Pattern mining of historical retros (Phase 14)
- File protection enforcement (Phase 13)
- Dashboard HTML generation (Phase 16)
- Token measurement (deferred to `_future/token-based-modes.md`)

---

End of phase-12.
