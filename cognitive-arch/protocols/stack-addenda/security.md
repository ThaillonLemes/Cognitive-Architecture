# Security Conventions Addendum

**Scope: UNIVERSAL — applies to all projects and all technology stacks.**

This document translates the five Security Axioms (S1-S5) from `PROTOCOLS.md` into concrete, actionable conventions. Every implementer writing security-critical code and every reviewer running the security-review command uses this document as their primary reference.

**Canonical axiom definitions:** `PROTOCOLS.md § Security Axioms (S)`

**Security review command:** `commands/security-review.md`

**Threat model template:** `templates/threat-model.md`

---

## Section 1 — Input Validation (S1)

*All external input is untrusted until explicitly validated.*

- Validate all HTTP query parameters, path parameters, request body fields, and headers before use. Use schema validation libraries where available (e.g., Zod for TypeScript, Pydantic for Python, Cerberus for Python).
- Never trust client-provided resource IDs without verifying server-side ownership. A user submitting `itemId: 9999` must not be able to access items they do not own — verify that the authenticated session's identity owns or has permission on that resource.
- Use allowlists, not blocklists. Define explicitly what is permitted; reject everything else. Blocklists inevitably miss edge cases and novel attack vectors.
- File uploads must validate MIME type by content inspection (magic bytes), not by file extension or the `Content-Type` header alone. Both can be trivially forged.
- Sanitize inputs before they reach: database queries (use parameterized queries — never string concatenation), shell commands (avoid shell invocation entirely; if unavoidable, use argument arrays not strings), template engines (escape context-appropriate characters), and log sinks (see Section 3).
- Integer inputs must have explicit range checks. Game-specific risk: player-submitted quantities (items, gold amounts, coordinates) must be validated against server-authoritative limits before any game state mutation.

---

## Section 2 — Auth Chain (S2)

*Authentication → Authorization → Action. Never skip or reorder.*

- Session tokens must be opaque random values with a minimum of 128 bits of entropy, issued by the server, and stored as `httpOnly; Secure; SameSite=Strict` cookies. Never store session tokens or JWTs in `localStorage` or `sessionStorage` — these are accessible to JavaScript and vulnerable to XSS.
- Authentication and authorization must be implemented as separate, independently testable layers. Never implement "check credentials AND perform the action" in a single function.
- Logout must invalidate the session server-side. Clearing the client-side cookie alone is not sufficient — the token must be revoked in the session store.
- Privilege escalation paths (e.g., "remember me," "admin impersonation," "GM commands" in MMORPG context) must be explicitly documented in the threat model and must require re-authentication or a separate elevated-privilege token.
- Service-to-service calls within the backend must authenticate using short-lived tokens or mutual TLS, not static API keys embedded in source code or environment files committed to version control.
- WebSocket connections must authenticate at connection establishment (e.g., via a handshake token) AND re-validate session state at meaningful intervals. An expired or invalidated session must close the WebSocket connection.

---

## Section 3 — Data Handling (S3)

*Sensitive data is never logged, never hardcoded, never transmitted in plaintext.*

- All secrets (API keys, database credentials, private keys, SMTP passwords, signing secrets) must be sourced from environment variables or a dedicated secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault, Azure Key Vault). Never hardcode secrets in source files, configuration files in version control, or infrastructure-as-code templates.
- Log calls must never include request bodies or response bodies that may contain passwords, tokens, credit card numbers, or PII. Implement a field-scrubbing layer or use structured logging with an explicit field allowlist. Log the shape of the request, not its contents.
- PII at rest must be encrypted using AES-256-GCM or an equivalent authenticated encryption scheme. Encryption keys must be stored in a key management system, not alongside the encrypted data.
- Database backups must be encrypted before storage. Access to unencrypted backup files is treated as equivalent to a data breach — apply the same access controls and audit logging as production systems.
- Passwords must be hashed using bcrypt (work factor ≥ 12), scrypt, or Argon2id. MD5 and SHA-1 are not acceptable for password storage under any circumstances.
- Data transmitted between client and server, and between services, must use TLS 1.2 or higher. Plain HTTP must not be used for any authenticated endpoint or any endpoint that handles sensitive data.
- Game-specific: player inventory, currency balances, and transaction history are sensitive data — they are high-value targets for fraud. Apply the same protection level as financial data.

---

## Section 4 — Threat Modeling (S4)

*[code-only] A threat model is required before writing security-critical code.*

- Before writing any code for: an authentication system, a cryptographic operation, session management, a WebSocket or network protocol handler, or a financial/economy transaction system — create `design/threat-model-<system>.md` using `templates/threat-model.md`.
- The threat model must be reviewed and acknowledged by at least one other implementer before the security-critical code is written. Record the reviewer's acknowledgment in the threat model document.
- Use STRIDE as the baseline threat taxonomy: **S**poofing, **T**ampering, **R**epudiation, **I**nformation Disclosure, **D**enial of Service, **E**levation of Privilege. Every applicable STRIDE category must be addressed for each identified threat actor and trust boundary.
- Threat models must be updated when the system's trust boundaries, data flows, or authentication mechanisms change. A threat model for a system that has since been modified is treated as absent until updated.
- "We'll do it later" is not an acceptable mitigation. Mitigations that are not yet implemented must be listed under Residual Risks with an explicit owner and target date. These appear in the health report as open security debt.

---

## Section 5 — Security Gates (S5)

*[code-only] Security-critical blocks require a passing security review before close.*

- Any block whose implementation touches: authentication code, session management, network socket handling, cryptographic operations, persistent data access (especially write paths), or financial/economy transaction logic must declare `security: true` in its manifest frontmatter.
- Blocks with `security: true` must pass the `commands/security-review.md` procedure before the block can be marked closed. A FAIL result is a hard block — the block cannot close until all FAIL findings are resolved or the block is split.
- The security review result (PASS / WARN / FAIL) must be recorded in the block's retrospective under "Security Review."
- WARN results may close if all warnings are explicitly triaged and accepted with written justification in the retrospective. Unacknowledged warnings are treated as FAIL.
- Security gates apply to modifications of existing security-critical code, not only to new code. If a block modifies an existing auth function, that block must have `security: true` even if the block's primary purpose is not security-related.
- The `audit.sh` script checks that no open block with `security: true` is in `status: done` without a retrospective security review field. This is an automated audit error, not a warning.

---

## Quick Reference — Axiom IDs

| Axiom | Short name | When violated |
|-------|-----------|---------------|
| S1 | Untrusted Input | Any unvalidated external input reaches a sensitive code path |
| S2 | Auth Chain Integrity | Any auth/authz step is skipped or combined incorrectly |
| S3 | Sensitive Data Protection | Any secret logged, hardcoded, or transmitted in plaintext |
| S4 | Threat Model First | Security-critical code written before threat model exists |
| S5 | Security Gate Mandatory | Block with `security: true` closed without security review |

End of security.md.
