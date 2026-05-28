---
id: ADR-003
title: three-tier-manifest-system-S-M-L
status: accepted
created_at: 2026-05-23
decided_at: 2026-05-21
deciders: [user, AI]
backfilled: true
original_decision_date: "2026-05-21 (approx. phase-2)"
context_phase: phase-2
context_block: block-011
---

# ADR-003 — Three-tier manifest system (S / M / L)

## 1. Context

During phase-1, all blocks used a single manifest schema regardless of complexity. A 1-file doc correction and a multi-file SDK module carried the same gate structure. This created two problems: small blocks were burdened with unnecessary gate definitions, and large blocks lacked explicit scope-escalation signals. By phase-2, the block corpus was large enough (11+ blocks) to reveal three empirically distinct complexity bands.

## 2. Decision

**Adopt a three-tier manifest system:**

- **Tier S (Small):** ≤ 2 files modified/created, doc-only or single-function fix. Mandatory fields: `id`, `tier`, `kind`, `status`, `files`, `gates`. No pseudocode requirement.
- **Tier M (Medium):** 3-10 files or multi-function implementation. Adds `dependencies`, `estimated_duration_days`, SPARC execution protocol mandatory.
- **Tier L (Large):** Cross-cutting, >10 files, or introduces new abstraction visible to multiple callers. Adds `risks` table, new-abstraction justification (`§8`), parallel execution plan.

Each tier has its own generation protocol: `protocols/manifest-{small,medium,large}-generation.md`.

## 3. Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| Single schema (current) | No friction for small blocks | Over-engineered for doc fixes; under-structured for complex work | Not chosen |
| Two tiers (S / L) | Simpler than three | M-tier work is the plurality; binary forces awkward upgrades | Not chosen |
| **Three tiers S/M/L** | Right-sized per block; generation protocols match complexity | Requires tier judgment at manifest creation | ✓ chosen |
| Four+ tiers | Finer granularity | Judgment cost outweighs benefit; empirical data shows 3 clusters | Not chosen |

## 4. Consequences

- **Positive:** Block overhead scales with block complexity. Tier S blocks complete in minutes. Tier L blocks have explicit risk tables and parallel plans.
- **Negative:** Tier misjudgment requires manifest revision mid-block. Upgrade path (S→M) is cheap; downgrade (M→S) requires manifest edit and re-gate.
- **Neutral:** `audit.sh` check 5 validates tier schema compliance. Mis-tiered blocks surface as warnings.

## 5. References

- Phase doc: `phases/phase-2.md`
- Block manifests: `manifests/block-011-schema-tier-s.md`, `manifests/block-012-schema-tier-m.md`, `manifests/block-013-schema-tier-l.md`
- Generation protocols: `protocols/manifest-small-generation.md`, `protocols/manifest-medium-generation.md`, `protocols/manifest-large-generation.md`

---

End of ADR.
