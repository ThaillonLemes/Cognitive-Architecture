---
id: block-076
tier: S
kind: protocol
phase: phase-10
scope: phase-bound
status: planned
security: false
dependencies: []
files:
  read:
    - PROTOCOLS.md
    - INDEX.md
  modify:
    - PROTOCOLS.md
    - INDEX.md
  create: []
gates:
  - name: s1-axiom-present
    type: command
    cmd: "grep -q \"S1:\" PROTOCOLS.md"
    expect: exit 0
  - name: s5-axiom-present
    type: command
    cmd: "grep -q \"S5:\" PROTOCOLS.md"
    expect: exit 0
  - name: protocols-changed
    type: file-changed
    paths:
      - PROTOCOLS.md
created_at: 2026-05-23
last_updated: 2026-05-23
---

# block-076 — Security Axioms (S1-S5)

## Purpose

Add five security axioms to `PROTOCOLS.md` as a new "S" category alongside the existing P (Principles), Q (Quality), and C (Charter) categories. These axioms define the non-negotiable security posture of the architecture and serve as the normative reference for all subsequent security protocol work in Phase 10.

Also update `INDEX.md` to record the addition of the S-category axioms.

---

## Context

Prior to Phase 10, `PROTOCOLS.md` contains only P, Q, and C axioms. Security concerns are addressed ad hoc in individual stack addenda, if at all. For a project that includes authentication, real-time multiplayer networking, persistent player data, and in-game economy transactions, this is insufficient. The S axioms establish a shared vocabulary and set of hard constraints that every implementer and reviewer can reference by shorthand (e.g., "this violates S3" or "S4 gate required here").

---

## Axioms to Add

The following five axioms must be added to `PROTOCOLS.md` under a new `## Security Axioms (S)` section, formatted consistently with existing axiom categories.

**S1 — Untrusted Input**
Every input is untrusted until explicitly validated. Validate type, range, format, and origin before processing any external data. "External" includes HTTP requests, WebSocket messages, file uploads, environment variables read at runtime, and inter-service calls.

**S2 — Auth Chain Integrity**
Authentication before authorization, authorization before action. Never skip or short-circuit this chain. Verify identity first, then check permissions against that identity, then execute the requested action. A missing link in this chain is a hard security violation regardless of context.

**S3 — Sensitive Data Protection**
Sensitive data is never logged, never hardcoded, and never transmitted in plaintext. API keys, passwords, session tokens, and PII are always encrypted at rest and in transit. Violation of this axiom is grounds for immediate block rollback.

**S4 — Threat Model First**
A threat model must be documented in `design/` before writing any security-critical code. "Security-critical" means any code that handles authentication, cryptography, session management, inter-service trust, or network protocol implementation. No threat model means no code.

**S5 — Security Gate Mandatory**
Every block touching authentication, networking, or persistent data requires a security-review gate. This is not optional and cannot be deferred. A block with `security: true` in its manifest cannot be closed without a passing or warning-level security review result.

---

## Implementation Steps

1. Read `PROTOCOLS.md` to understand the existing axiom format and section structure.
2. Locate the end of the last axiom category (C — Charter, or whichever comes last).
3. Append a new `## Security Axioms (S)` section with all five axioms formatted to match existing style.
4. Read `INDEX.md` to find where protocol changes are logged.
5. Add an entry noting that Phase 10 / block-076 introduced the S-category security axioms.

---

## Acceptance Criteria

- `PROTOCOLS.md` contains a `## Security Axioms (S)` section with entries for S1 through S5.
- Each axiom entry includes the axiom ID, a short name, and a full description.
- The formatting is consistent with existing P, Q, and C axiom entries.
- `INDEX.md` references the S-category addition.
- `grep -q "S1:" PROTOCOLS.md` exits 0.
- `grep -q "S5:" PROTOCOLS.md` exits 0.

---

## Notes

- This block has no dependencies. It is the foundation of the entire Phase 10 dependency chain.
- Do not modify the wording of S1-S5 during implementation. The exact language matters for downstream references in block-077 through block-080.
- If `PROTOCOLS.md` already has a security section from prior work, reconcile rather than duplicate, but ensure all five axiom IDs S1-S5 are present in the final file.
