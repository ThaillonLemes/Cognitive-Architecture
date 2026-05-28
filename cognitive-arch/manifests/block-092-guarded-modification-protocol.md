---
id: block-092
tier: M
kind: implementation
phase: phase-13
scope: phase-bound
status: pending
security: false
dependencies: [block-090]
files:
  read:
    - PROTOCOLS.md
    - protocols/code-header-protocol.md
    - protocols/pointer-integrity.md
    - design/arch-v3.md
  modify:
    - PROTOCOLS.md
  create:
    - protocols/architecture-integrity.md
gates:
  - name: protocol-created
    type: file-changed
    paths: [protocols/architecture-integrity.md]
  - name: protocols-md-updated
    type: file-changed
    paths: [PROTOCOLS.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-090]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-092-guarded-modification-protocol.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 092 — AI guarded modification protocol

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Document the explicit behavior the AI follows when asked to modify a `protection:`-tagged file. Three tiers with three behaviors: immutable refuses + requires override ceremony; guarded requires textual confirmation; open is normal. Adds a new axiom candidate (`P7. Architecture protection respected`) to PROTOCOLS.md.

## 2. Dependencies

- block-090 (frontmatter tags exist for AI to read)

## 3. Files

- **Read:** PROTOCOLS.md, code-header protocol (for style consistency), pointer-integrity (similar audit protocol), arch-v3 design
- **Modify:** PROTOCOLS.md (add P7 axiom under Group P)
- **Create:** `protocols/architecture-integrity.md` (full protocol: behavior per tier, override ceremony, log entry requirement)

## 4. Validation

- `protocols/architecture-integrity.md` has 3 sections (one per tier) with explicit AI behavior decision tree
- Override ceremony documented: confirmation phrase + `.governor/log.md` entry (D3)
- PROTOCOLS.md axiom P7 added in alphabetical order within Group P; numbering preserved for existing P1-P6
- Examples of compliant vs non-compliant AI responses provided in protocol

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI doesn't follow protocol despite documentation | Med | Protocol read at session boot via CLAUDE.md; axiom P7 makes it formally bindable |
| Override ceremony too cumbersome for legitimate work | Med | Confirmation phrase short ("CONFIRMO QUEBRAR..."); log entry single line |
| Protocol conflicts with existing axioms | Low | Cross-checked against P1-P6 and Group M during writing |

## 7. Out of Scope

- Enforcement at the OS level (chmod — out of scope per Phase 13)
- Automated detection of protocol violation (audit covers integrity, not AI-behavior compliance)
- Multi-user override approval (single-user)

## 8. New Abstraction

P7 axiom is new vocabulary in PROTOCOLS.md. Justification: governs behavior across all protected files; not specific to one file. Belongs in Group P.
