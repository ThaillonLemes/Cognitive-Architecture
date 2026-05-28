---
id: threat-model/[system-name]
system: [System Name]
created_at: YYYY-MM-DD
last_updated: YYYY-MM-DD
author: [Author]
reviewer: [Reviewer]
axiom: S4
status: draft
---

# Threat Model: [System Name]

BRIEF: S4-required threat analysis for [system]. Fill all sections before writing security-critical code.
Process guide: `protocols/threat-model-generation.md`.

---

## Section 1 — System Under Threat

**System name:** [exact system identifier, e.g., "networking/auth-handshake"]

**Description:**
> 1-2 paragraphs: what this system does, what security properties it must maintain (confidentiality, integrity, availability, authenticity), and why it is classified as security-critical.

**Data classification:** (check all that apply)
- [ ] Player PII (name, email, address, DOB)
- [ ] Authentication credentials (passwords, tokens, keys)
- [ ] Financial / payment data (card numbers, transaction records)
- [ ] Game state (inventory, currency, position, progress)
- [ ] Server infrastructure data (configs, internal addresses, credentials)
- [ ] Third-party service secrets (API keys, webhooks)

**Deployment context:**
> Where does this system run? (client-side, game server, auth service, background worker, etc.) What trust level does the runtime environment have? Who administers it?

---

## Section 2 — Trust Boundaries

List every boundary where data crosses from a less-trusted context to a more-trusted one, or between different trust zones.

| # | Boundary Name | What Crosses It | Direction | Notes |
|---|--------------|----------------|-----------|-------|
| B1 | [e.g., "Game client → Auth server"] | [e.g., "Login credentials, session requests"] | Client → Server | [Notes] |
| B2 | [e.g., "Auth server → Database"] | [e.g., "Parameterized queries, hashed credentials"] | Server → DB | [Notes] |
| B3 | | | | |

> Add rows for every boundary. Missing a boundary here is the most common cause of incomplete threat models. Include inter-service boundaries even for "internal" calls.

---

## Section 3 — Threat Actors

| Actor | Motivation | Capabilities | In Scope? | Rationale |
|-------|-----------|-------------|----------|-----------|
| Anonymous attacker | Data theft, disruption | External network access, scripting tools | Yes | Any internet-exposed system faces this |
| Authenticated cheater (player) | Unfair advantage, economy manipulation | Valid session token, client-side code modification | Yes | [Rationale] |
| Disgruntled ex-employee | Sabotage, data exfiltration | May have residual access or knowledge | Yes/No | [Rationale] |
| Competing service / scraper | Intelligence gathering | Automated requests | Yes/No | [Rationale] |
| Nation-state / APT | [Goal] | [Capabilities] | Yes/No | [Rationale] |

> Add or remove rows as appropriate. Do not include actors only to mark them "No" without justification — if they are not in scope, say why briefly.

---

## Section 4 — STRIDE Analysis

One row per identified threat instance. Be specific — "attacker sends malformed packet" is not a threat; "attacker sends a WebSocket message with a negative itemId to cause server-side integer underflow in the inventory service" is a threat.

| Threat ID | STRIDE Category | Description | Affected Component | Likelihood | Impact | Mitigation Ref | Status |
|-----------|----------------|-------------|-------------------|-----------|--------|----------------|--------|
| T01 | Spoofing | [Description] | [Component] | Low/Med/High | Low/Med/High | M01 | Open/Partial/Mitigated/Accepted |
| T02 | Tampering | [Description] | [Component] | | | M02 | |
| T03 | Repudiation | [Description] | [Component] | | | | |
| T04 | Information Disclosure | [Description] | [Component] | | | | |
| T05 | Denial of Service | [Description] | [Component] | | | | |
| T06 | Elevation of Privilege | [Description] | [Component] | | | | |

> Aim for at least one row per STRIDE category. A category with no threats is suspicious — justify it explicitly rather than leaving it empty.

**STRIDE reference:**
- **S**poofing — impersonating a user, service, or identity
- **T**ampering — unauthorized modification of data or code in transit or at rest
- **R**epudiation — denying an action occurred without the system being able to disprove it
- **I**nformation Disclosure — exposure of information to unauthorized parties
- **D**enial of Service — preventing legitimate users from using the system
- **E**levation of Privilege — gaining capabilities beyond what was granted

---

## Section 5 — Attack Surface

Every entry point that accepts external input is part of the attack surface.

| # | Entry Point | Protocol / Mechanism | Auth Required | Validation in Place |
|---|------------|---------------------|--------------|---------------------|
| E1 | [e.g., "POST /api/login"] | HTTPS/REST | No (pre-auth) | [e.g., "Schema validation via Pydantic; rate-limited 5 req/s"] |
| E2 | [e.g., "WebSocket game:action message"] | WSS | Yes (session token) | [e.g., "Session validated on connect; message schema checked"] |
| E3 | | | | |

> Include all externally reachable surfaces: HTTP endpoints, WebSocket message types, file upload handlers, environment variable reads, third-party webhook receivers.

---

## Section 6 — Mitigations

For every mitigation referenced in the STRIDE table (M01, M02, etc.):

| Mitigation ID | Description | Implementation Location | Verification Method |
|--------------|-------------|------------------------|---------------------|
| M01 | [e.g., "Session tokens are 256-bit random values, httpOnly, Secure cookies"] | `auth/session.py:generate_session_token()` | Unit test + manual curl inspection of Set-Cookie header |
| M02 | [e.g., "Input schema validation on all WebSocket messages"] | `networking/ws_handler.py:validate_message()` | Test suite: `tests/test_ws_validation.py` |

> For each mitigation: the description should be specific enough to verify independently. "We validate input" is not a mitigation. "All WebSocket messages are validated against a Pydantic schema before any handler is invoked — see `ws_handler.py:validate_message()`" is a mitigation.

---

## Section 7 — Residual Risks

Threats that are in-scope but not fully mitigated. An empty section here is suspicious — it likely means the analysis is incomplete, not that the system is perfectly secure. Every system has residual risk.

| Risk ID | Description | Why Accepted | Compensating Control | Owner | Target Date |
|---------|-------------|-------------|---------------------|-------|------------|
| R01 | [Description of unmitigated or partially mitigated threat] | [Justification: low likelihood + low impact + compensating control] | [What reduces the risk even without full mitigation] | [Named person or team] | YYYY-MM-DD or "permanent accept" |

> "We'll fix it later" without a named owner and date is not acceptance. It is a deferred decision masquerading as analysis. All residual risks appear in the health report as open security debt.

---

## Section 8 — Review

| Field | Value |
|-------|-------|
| Original author | [Name] |
| Created | YYYY-MM-DD |
| Reviewer | [Name] |
| Review date | YYYY-MM-DD |
| Next review trigger | [e.g., "Any change to session management code; or when a new auth provider is added; or annually"] |
| Axiom reference | S4 — `PROTOCOLS.md § Security Axioms (S)` |
| Generation guide | `protocols/threat-model-generation.md` |

End of threat model template.
