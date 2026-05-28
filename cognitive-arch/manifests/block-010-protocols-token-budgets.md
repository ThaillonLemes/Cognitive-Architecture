---
id: block-010
tier: S
kind: doc-only
phase: phase-2
status: planned
dependencies: []
files:
  read:
    - PROTOCOLS.md
  modify:
    - PROTOCOLS.md
  create: []
gates:
  - name: token-budget-in-q2
    type: manual
    description: PROTOCOLS.md Q2 section mentions token estimates (chars/4) alongside line budgets
  - name: files-updated
    type: file-changed
    paths: [PROTOCOLS.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 010 — PROTOCOLS.md Q2 — token budget estimates

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Update `PROTOCOLS.md` Q2 axiom (file size / token budget) to mention token estimates alongside the existing line budget. Closes the gap: the architecture says "keep files small" but never defines what "small" means in tokens.

## 2. Files

- **Read:** PROTOCOLS.md
- **Modify:** PROTOCOLS.md (Q2 section, 1-3 lines added)
- **Create:** none

## 3. Spec

Current Q2 likely reads something like:
> "Keep HOT files within line budgets."

Update to add after the line budget statement:
> "Token estimate (proxy): chars÷4. HOT boot target: <4,000 tok total. Single HOT file soft cap: 1,000 tok. Run `/token-audit` for breakdown."

The addition must be minimal (≤3 lines) to stay within CLAUDE.md's Q2 budget tracking.

## 4. Validation

- PROTOCOLS.md Q2 mentions "chars÷4" or "chars/4" token estimate method
- PROTOCOLS.md Q2 mentions the 4,000 tok HOT boot target
- PROTOCOLS.md total line count increases by ≤3 lines

## 5. Out of scope

- Changing other axioms
- Hard token budget enforcement (informational only until Phase 5)
