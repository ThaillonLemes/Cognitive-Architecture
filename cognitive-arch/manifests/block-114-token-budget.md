---
id: block-114
tier: S
kind: doc-only
phase: phase-18
status: planned
security: false
files:
  read:
    - PROTOCOLS.md
    - governance/token-report.md
  modify:
    - PROTOCOLS.md
  create:
    - governance/token-budget.md
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
parallel_with: [block-113]
---

# Block 114 — token-budget.md + Axiom P-TOK-1

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Parallel-with:** block-113

## 1. Purpose

Create governance/token-budget.md defining per-phase token budgets based on historical data. Add Axiom P-TOK-1 ("Track actual token cost on every block; budget overrun triggers governance review") to PROTOCOLS.md. This establishes the policy that makes token tracking governable — not just observable.

## 2. Dependencies

None (can run in parallel with block-113; reads token-report.md if available but can use defaults).

## 3. Files

- **Read:** PROTOCOLS.md (axiom format), governance/token-report.md (for baseline numbers if available)
- **Modify:** PROTOCOLS.md — append P-TOK-1 to the P-axioms section
- **Create:** governance/token-budget.md

## 4. Validation

- governance/token-budget.md exists with per-phase budget table
- PROTOCOLS.md contains P-TOK-1 with correct format
- Axiom text matches existing P-axiom formatting conventions
- `grep "P-TOK-1" PROTOCOLS.md` returns match

## 5. Gates

- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md changed

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Budget numbers arbitrary without historical baseline | Low | Phase 18 token-report establishes baseline retroactively; budgets labeled "estimated" until block-116 |
| P-TOK-1 conflicts with existing axiom IDs | Low | Check existing axiom IDs before adding; next available P-axiom slot used |

## 7. Out of Scope

- Hard token limits at phase level (advisory only)
- Per-block token budgets (too granular for phase-18)

## 8. New Abstraction

None. Governance document + axiom addition only.
