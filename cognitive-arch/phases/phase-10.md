---
id: phase-10
status: planned
version: v2.4
prev_phase: phase-9
exit_criteria_count: 5
blocks_count: 5
estimated_duration_days: 2
created_at: 2026-05-23
last_updated: 2026-05-23
owner: implementer
---

# Phase 10 — Security Protocol

## Purpose

Phase 10 adds security as a first-class concern throughout the architecture. Prior phases treat security as implicit and optional. For long-term software — especially MMORPGs with authentication, real-time networking, persistent data, and financial transactions — security must function as an axiom, not an afterthought.

This phase formalizes five security axioms (S1-S5), wires a security-review gate into the block-close workflow, and ensures every new block manifest declares whether it touches security-critical surfaces.

---

## Exit Criteria

1. `PROTOCOLS.md` contains 5 security axioms S1-S5, correctly formatted alongside existing P/Q/C axioms.
2. `protocols/stack-addenda/security.md` exists covering all 5 axiom domains (input validation, auth chain, data handling, threat modeling, security gates).
3. `templates/threat-model.md` and `protocols/threat-model-generation.md` exist; the threat model template has sections for attack surface, threat actors, mitigations, and residual risks.
4. `commands/security-review.md` exists with a step-by-step review procedure referencing S1-S5 and the threat model.
5. `protocols/block-close-checklist.md` has a security gate step (conditional on `security: true` in manifest); `templates/manifest-medium.md` and `templates/manifest-large.md` have a `security: false` field.

---

## Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-076 | Security Axioms (S1-S5) | S | planned | manifests/block-076-security-axioms.md |
| block-077 | Security Stack Addendum | S | planned | manifests/block-077-security-stack-addendum.md |
| block-078 | Threat Model Template | S | planned | manifests/block-078-threat-model-template.md |
| block-079 | Security Review Command | S | planned | manifests/block-079-security-review-command.md |
| block-080 | Security Gate Integration | S | planned | manifests/block-080-security-gate-integration.md |

---

## Dependency Groups

### Group 10A — Axiom Foundation
Blocks: `block-076`
No dependencies. The security axioms must exist before anything else in this phase can reference them.

### Group 10B — Conventions and Templates
Blocks: `block-077`, `block-078`
Depends on: Group 10A
The stack addendum and threat model template both build on the axiom vocabulary established in block-076. These two blocks may execute in parallel once 10A is complete.

### Group 10C — Review Command
Blocks: `block-079`
Depends on: Group 10B
The security-review command references the stack addendum (for axiom checks) and the threat model template (for S4 verification). Both must exist before the command is written.

### Group 10D — Gate Integration
Blocks: `block-080`
Depends on: Group 10C
The security gate integration wires the completed review command into the block-close checklist and adds the `security:` field to manifest templates. This is the last block in the phase and completes the closed loop.

---

## Execution Order

```
block-076
  └─ block-077 ─┐
  └─ block-078 ─┤
                └─ block-079
                     └─ block-080
```

---

## Notes

- All blocks in this phase are Tier S (Strategic). They modify foundational protocol files that affect every subsequent phase.
- Phase 10 does not produce runnable code. Its deliverables are protocol documents, templates, and command procedures.
- The security gate introduced in block-080 is retroactively relevant to prior blocks that touched auth or networking (e.g., blocks in phases covering multiplayer or persistence). Those blocks do not need to be re-closed, but any future modifications to them must pass the security-review gate.
- The `security: false` default on manifest templates means the gate is opt-in per block, preventing false positives on purely structural or documentation blocks.
