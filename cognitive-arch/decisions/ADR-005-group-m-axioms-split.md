---
id: ADR-005
title: group-m-axioms-split-cognitive-arch-as-axioms
status: accepted
created_at: 2026-05-23
decided_at: 2026-05-22
deciders: [user, AI]
backfilled: true
original_decision_date: "2026-05-22 (approx. phase-9 / v2.5 port)"
context_phase: phase-9
---

# ADR-005 — Group M: Cognitive-arch axioms as a separate axiom group

## 1. Context

The canonical cognitive-arch uses four axiom groups: **P** (Principles), **Q** (Quality), **C** (Charter), **S** (Security). These 24 axioms are universal — they apply to any project that adopts the architecture.

When cognitive-arch was ported to the MMORPG project (`C:\Users\thail\MMORPG\`) as its governance layer, the MMORPG team needed axioms that described how to treat the cognitive architecture methodology *itself* — axioms about meta-governance, multi-repo orchestration, and the cognitive-arch-as-framework rules. These axioms were MMORPG-specific and inappropriate for the universal canonical source.

The decision was: should these meta-axioms be added to the canonical source, or kept in the application layer?

## 2. Decision

**Create Group M exclusively in the MMORPG application layer, not in the canonical cognitive-arch source.**

- The canonical cognitive-arch retains 24 axioms across P/Q/C/S.
- Group M (8 axioms) lives in `MMORPG/PROTOCOLS.md` and covers MMORPG-specific orchestration rules (multi-repo coordination, Governor dispatch across 4 sub-repos, etc.).
- The embedded `cognitive-arch/` copy in MMORPG remains canonical-generic and does NOT include Group M — it is a reference copy, not an application.
- Group S (Security) was added to canonical in v2.5 and ported additively to MMORPG. Group M was NOT ported back — it stays application-specific.

This maintains the principle: **canonical source = universal; application = extended**.

## 3. Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| Add Group M to canonical source | Single source of truth | Meta-governance axioms would be meaningless outside multi-repo context | Not chosen |
| No Group M — inline in MMORPG PROTOCOLS.md comments | Less formal | Axioms buried in comments are not enforceable; audit can't check them | Not chosen |
| **Group M in MMORPG application layer only** | Application-specific axioms stay in application | Canonical and MMORPG PROTOCOLS.md diverge (managed via port discipline) | ✓ chosen |
| Parameterize canonical axioms (feature flags) | Flexible | Adds complexity to universal source for a niche concern | Not chosen |

## 4. Consequences

- **Positive:** Canonical cognitive-arch stays lean (24 axioms). MMORPG can extend freely. Port discipline (`memory/cognitive-arch-mmorpg-relationship.md`) prevents accidental overwrite.
- **Negative:** Two PROTOCOLS.md files to maintain. Port events require explicit stewardship (version bump + `governor/log.md` entry).
- **Neutral:** Future applications of cognitive-arch that need meta-governance axioms follow the same pattern: extend locally, don't pollute canonical.

## 5. References

- Memory: `C:\Users\thail\.claude\projects\...\memory\cognitive-arch-mmorpg-relationship.md`
- MMORPG PROTOCOLS.md: `C:\Users\thail\MMORPG\PROTOCOLS.md` (v3.6, 27 axioms P/Q/C/M/S)
- Canonical PROTOCOLS.md: `PROTOCOLS.md` (v2.5, 24 axioms P/Q/C/S)

---

End of ADR.
