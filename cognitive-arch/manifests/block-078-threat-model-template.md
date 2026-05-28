---
id: block-078
tier: S
kind: protocol
phase: phase-10
scope: phase-bound
status: planned
security: false
dependencies:
  - block-077
files:
  read: []
  modify: []
  create:
    - templates/threat-model.md
    - protocols/threat-model-generation.md
gates:
  - name: template-created
    type: file-changed
    paths:
      - templates/threat-model.md
  - name: generation-guide-created
    type: file-changed
    paths:
      - protocols/threat-model-generation.md
created_at: 2026-05-23
last_updated: 2026-05-23
---

# block-078 — Threat Model Template

## Purpose

Create two files:

1. `templates/threat-model.md` — the fill-in template that must be completed before writing security-critical code for any system (per axiom S4).
2. `protocols/threat-model-generation.md` — a process guide explaining how to fill the template correctly, including STRIDE analysis guidance, trust boundary identification, and criteria for acceptable residual risk.

---

## Context

Axiom S4 mandates a documented threat model in `design/` before writing security-critical code. Without a standard template, "document a threat model" is ambiguous — implementers may produce documents that are superficially compliant but miss critical attack surfaces. The template enforces structural completeness. The generation guide ensures the template is filled with analytical rigor, not checkbox compliance.

This pair of files (template + guide) mirrors the pattern used elsewhere in the architecture: a `templates/` file defines structure; a `protocols/` file defines process.

---

## File 1: `templates/threat-model.md`

The template must contain the following eight sections. All section headers must be present in the template, populated with instructional placeholder text (in blockquotes or HTML comments) that guides the implementer. The template is not a blank form — it contains enough guidance inline that it can be filled without consulting the generation guide for routine cases.

**Section 1 — System Under Threat**
Fields: system name, one-paragraph description, data classification (what categories of data does this system handle: PII, credentials, financial, game state, etc.), and deployment context (client-side, server-side, embedded in game client, etc.).

**Section 2 — Trust Boundaries**
A list of boundaries where data crosses from an untrusted context to a trusted one, or between two different trust zones. Examples: "browser → API server," "game client → authoritative game server," "player input → database write." Each boundary entry includes: boundary name, what crosses it (data/commands), and direction.

**Section 3 — Threat Actors**
A table: Actor | Motivation | Capabilities | In-scope?
Typical actors for an MMORPG: anonymous attacker, authenticated cheater, disgruntled ex-employee, competing game studio, script kiddie, nation-state (if applicable). Each row must have a yes/no for in-scope and a rationale.

**Section 4 — STRIDE Analysis**
A table with one row per identified threat instance: Threat ID | STRIDE Category | Description | Affected Component | Likelihood (Low/Med/High) | Impact (Low/Med/High) | Mitigation Reference | Status (Mitigated/Partial/Accepted/Open).

**Section 5 — Attack Surface**
A numbered list of entry points that accept external input. For each entry point: name, protocol/mechanism (HTTP POST, WebSocket message, UDP packet, file read, etc.), authentication required (yes/no), and validation currently in place.

**Section 6 — Mitigations**
For each mitigation referenced in the STRIDE table: Mitigation ID | Description | Implementation location | Verification method (how do we know it works?).

**Section 7 — Residual Risks**
Threats that are in-scope but not fully mitigated. For each: Risk ID | Description | Why accepted | Owner | Target remediation date (or "permanent accept"). An empty residual risks section is suspicious — it likely means the analysis is incomplete, not that the system is perfectly secure.

**Section 8 — Review**
Fields: original author, review date, reviewer name(s), next review trigger (e.g., "on any change to session handling," "on addition of new payment provider," "annually").

---

## File 2: `protocols/threat-model-generation.md`

This process guide must cover the following topics, in a way that is actionable for an implementer who has never formally threat-modeled before:

**When to create a threat model**
List the triggers that require a new threat model. Reference S4 from `PROTOCOLS.md`. Include: starting a new auth system, adding a new network-facing endpoint, implementing any cryptographic operation, adding persistent storage for PII, modifying trust boundaries in an existing system.

**How to identify trust boundaries**
Explain the concept of a trust boundary in plain language. Provide examples from the MMORPG domain: client/server boundary, the authentication perimeter, the boundary between player-writable and server-authoritative game state, the boundary between the game server and third-party payment processor.

**STRIDE in practice**
For each of the six STRIDE categories, provide one concrete example of how that threat manifests in a multiplayer game context:
- Spoofing: a player spoofing another player's identity in a WebSocket message
- Tampering: a client modifying game state packets to report false positions or scores
- Repudiation: a player claiming they never made a purchase the server recorded
- Information Disclosure: an API endpoint leaking other players' email addresses or session tokens
- Denial of Service: a flood of unauthenticated connection requests exhausting server resources
- Elevation of Privilege: a regular player gaining GM/admin capabilities through a parameter injection

**Likelihood and impact scoring**
Define the three levels (Low / Med / High) for both likelihood and impact in project-specific terms. Do not use abstract definitions — anchor them to observable consequences for the project.

**Residual risk acceptance criteria**
Define what makes a residual risk acceptable vs. unacceptable. Acceptable: risk is low likelihood AND low impact AND has a compensating control AND has a named owner. Unacceptable: high impact risks, risks with no compensating control, risks with no named owner. Explain that "we'll fix it later" is not acceptance — acceptance requires explicit acknowledgment, justification, and owner assignment.

**Review cadence**
Explain when a threat model must be updated. Emphasize that a threat model is a living document. Describe how to diff a threat model against a system change to determine whether the model is still current.

---

## Implementation Steps

1. Verify `templates/` directory exists.
2. Write `templates/threat-model.md` with all eight sections, inline guidance, and appropriate placeholder text.
3. Verify `protocols/` directory exists.
4. Write `protocols/threat-model-generation.md` covering all topics listed above.
5. Ensure both files cross-reference each other (template links to generation guide; guide links to template).

---

## Acceptance Criteria

- `templates/threat-model.md` exists and contains all eight section headers.
- The STRIDE analysis section contains a table structure with the required columns.
- The residual risks section is present and explicitly notes that an empty section is suspicious.
- `protocols/threat-model-generation.md` exists and covers all six STRIDE categories with MMORPG-domain examples.
- Both files reference S4 from `PROTOCOLS.md`.
- Both files cross-reference each other.

---

## Notes

- This block may execute in parallel with block-077 once block-076 is closed.
- The template should be usable by a developer who has one hour to threat-model a new feature, not a security consultant writing a formal security assessment. Keep it practical and bounded.
- The generation guide should not be longer than necessary. The goal is actionable guidance, not a security textbook.
