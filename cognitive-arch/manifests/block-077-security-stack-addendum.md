---
id: block-077
tier: S
kind: protocol
phase: phase-10
scope: phase-bound
status: planned
security: false
dependencies:
  - block-076
files:
  read:
    - PROTOCOLS.md
  modify: []
  create:
    - protocols/stack-addenda/security.md
gates:
  - name: addendum-created
    type: file-changed
    paths:
      - protocols/stack-addenda/security.md
created_at: 2026-05-23
last_updated: 2026-05-23
---

# block-077 — Security Stack Addendum

## Purpose

Create `protocols/stack-addenda/security.md` — a universal security conventions addendum that applies to all projects regardless of technology stack. Unlike other stack addenda (which are stack-specific), this addendum is universal: every project in the architecture must comply with it.

The document translates the five S axioms from `PROTOCOLS.md` into concrete, actionable conventions. It is the primary reference document for developers writing security-critical code and for reviewers running the security-review command.

---

## Context

The existing `protocols/stack-addenda/` directory contains stack-specific guidance (e.g., for TypeScript, Rust, Python). Security concerns cut across all stacks. An MMORPG project may have a TypeScript game client, a Rust networking layer, and a Python analytics service — all of which must follow the same input validation rules, the same secrets handling policy, and the same auth chain discipline.

Placing this document in `stack-addenda/` with a "universal" designation makes it discoverable alongside other addenda while signaling that its applicability is not scoped to a single stack.

---

## Document to Create

**Path:** `protocols/stack-addenda/security.md`

The document must contain the following five sections, each linked to its corresponding axiom:

### Section 1 — Input Validation (S1)

Concrete conventions derived from S1:

- Validate all HTTP query parameters, path parameters, request body fields, and headers before use. Use schema validation libraries where available (e.g., Zod for TypeScript, Pydantic for Python).
- Never trust client-provided resource IDs without verifying ownership server-side. A user submitting `itemId: 9999` must not be able to access items they do not own.
- Use allowlists, not blocklists. Define what is permitted; reject everything else. Blocklists inevitably miss edge cases.
- File uploads must validate MIME type by content inspection (magic bytes), not by file extension or `Content-Type` header alone.
- Reject or sanitize inputs before they reach database queries, shell commands, template engines, or log sinks.

### Section 2 — Auth Chain (S2)

Concrete conventions derived from S2:

- Session tokens must be opaque random values (minimum 128 bits of entropy), set as `httpOnly; Secure; SameSite=Strict` cookies. Never store session tokens or JWTs in `localStorage` or `sessionStorage`.
- Never implement "check credentials AND do the thing" in a single function. Authentication and authorization must be separate, independently testable layers.
- Implement proper logout: invalidate the session server-side on logout. Clearing the client-side cookie alone is not sufficient.
- Privilege escalation paths (e.g., "remember me," "admin impersonation") must be explicitly documented and require re-authentication.
- Service-to-service calls must authenticate with short-lived tokens or mutual TLS, not static API keys embedded in code.

### Section 3 — Data Handling (S3)

Concrete conventions derived from S3:

- All secrets (API keys, database credentials, private keys, SMTP passwords) must be sourced from environment variables or a secrets manager. Never hardcode secrets in source files, configuration files committed to version control, or infrastructure-as-code templates.
- Log calls must never include request bodies or response bodies if those payloads may contain passwords, tokens, credit card numbers, or PII. Implement a field-scrubbing layer or structured logging with explicit field allowlists.
- PII at rest must be encrypted using AES-256-GCM or an equivalent authenticated encryption scheme. Encryption keys must themselves be stored in a key management system, not alongside the encrypted data.
- Database backups must be encrypted before storage. Access to unencrypted backups must be treated as equivalent to a data breach.
- Prefer hashing with bcrypt, scrypt, or Argon2 for passwords. MD5 and SHA-1 are not acceptable for password storage.

### Section 4 — Threat Modeling (S4)

Concrete conventions derived from S4:

- Before writing any code for an auth system, cryptographic operation, session management feature, or network protocol: create a `design/threat-model-<system>.md` file using the `templates/threat-model.md` template.
- The threat model must be reviewed and acknowledged by at least one other implementer before the security-critical code is written.
- Use STRIDE as the baseline threat taxonomy: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege. Every applicable STRIDE category must be addressed for each identified threat actor.
- Threat models must be updated when the system's trust boundaries, data flows, or authentication mechanisms change. A stale threat model is not a threat model.
- "We'll do it later" is not an acceptable mitigation. Mitigations that are not yet implemented must be listed under Residual Risks with an explicit owner and target date.

### Section 5 — Security Gates (S5)

Concrete conventions derived from S5:

- Any block whose implementation touches authentication code, session management, network socket handling, cryptographic operations, persistent data access, or financial transaction logic must have `security: true` in its manifest frontmatter.
- Blocks with `security: true` must pass the `commands/security-review.md` procedure before the block can be marked closed. A FAIL result is a hard block.
- The security-review result (PASS / WARN / FAIL) must be recorded in the block's retrospective notes.
- WARN results may close if all warnings are triaged and accepted with explicit written justification. Unacknowledged warnings are treated as FAIL.
- Security gates apply to modifications of existing security-critical code, not just new code. Changing an existing auth function in a block that would otherwise have `security: false` requires elevating the block to `security: true`.

---

## Implementation Steps

1. Read `PROTOCOLS.md` to confirm S1-S5 are present (gate: block-076 must be closed first).
2. Verify `protocols/stack-addenda/` directory exists; create it if absent.
3. Write `protocols/stack-addenda/security.md` with all five sections as described above.
4. Ensure the document opens with a header declaring its universal scope and a reference to `PROTOCOLS.md` for the canonical axiom definitions.

---

## Acceptance Criteria

- `protocols/stack-addenda/security.md` exists and is non-empty.
- The document contains all five sections, each referencing its corresponding S-axiom.
- No placeholder text remains in the file.
- The document explicitly states it applies to all stacks/projects.

---

## Notes

- This block may execute in parallel with block-078 once block-076 is closed.
- The audience for this document is implementers writing code, not architects designing systems. Language should be direct, specific, and prescriptive.
- Avoid generic security advice that any developer already knows. Every sentence should be something that, if violated, would constitute a concrete security defect in this project's context.
