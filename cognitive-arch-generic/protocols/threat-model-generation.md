# Threat Model Generation Protocol

BRIEF: Process guide for filling `templates/threat-model.md` before writing security-critical code. Required by axiom S4. Uses STRIDE with MMORPG-domain examples.

Template: `templates/threat-model.md`
Axiom: S4 — `PROTOCOLS.md § Security Axioms (S)`

---

## When to Create a Threat Model

Create a new `design/threat-model-<system>.md` before writing code for any of the following:

| Trigger | Example |
|---------|---------|
| New authentication system | Login flow, OAuth integration, session management |
| New cryptographic operation | Token signing, data encryption at rest, key exchange |
| New network-facing endpoint | REST API route, WebSocket message type, UDP game packet handler |
| Persistent storage for PII | Adding player profile storage, payment records, chat logs |
| Trust boundary change | Moving a service from internal-only to internet-facing; adding a third-party integration |
| Modification of existing security-critical code | Changing how session tokens are generated, validated, or revoked |

**When in doubt:** if the code you are about to write could allow an attacker to impersonate a user, access data they shouldn't, or disrupt service for others — create a threat model first.

Save the file at `design/threat-model-<system>.md`. The `<system>` slug must match the system name in the manifest and the Track/phase it belongs to.

---

## How to Identify Trust Boundaries

A trust boundary is any point where data or control crosses from a context with one level of trust to a context with a different level of trust. At a boundary, the receiving side cannot assume the incoming data is valid, well-formed, or honest.

**Plain language:** If something goes from "outside" to "inside" (or from one inside to another inside with different permissions), that is a boundary.

**MMORPG domain examples:**

| Boundary | Description |
|----------|-------------|
| Game client → Authoritative game server | The client is never trusted. Players may run modified clients. Every client-submitted action (move, attack, purchase) must be validated server-side before being applied to authoritative game state. |
| Unauthenticated request → Authenticated session | Before login: the caller is anonymous. After: the caller has a verified identity. The transition point (the login handler) is the most security-critical code in the auth system. |
| Player-writable game state → Server-authoritative state | Players may submit game actions that affect their own state (inventory use, movement) but must never be able to write directly to server-authoritative data without server validation. |
| Game server → Payment processor | The server calls an external service. The trust relationship is mutual — the server trusts the processor's responses up to the limits of the TLS/signature verification; the processor trusts the server's requests up to the limits of the API key. Both sides are trust boundaries. |
| Internal service → Database | An "internal" service calling a database is still a boundary. The database trusts the service to send only valid parameterized queries. SQL injection attacks exist because developers forget this boundary. |

To find boundaries in your system: draw a simple box-and-arrow diagram of data flows. Every arrow that crosses between boxes is a potential boundary.

---

## STRIDE in Practice

For each of the six STRIDE categories, here is what the threat looks like in an MMORPG context:

### S — Spoofing

An attacker impersonates a legitimate user, service, or process.

**MMORPG example:** A player crafts a WebSocket message with another player's `playerId` in the payload, attempting to perform actions (trade, attack, move items) on behalf of that player. The server must derive the acting player's identity from the authenticated session, never from the request payload.

**How to find Spoofing threats:** For every API or WebSocket endpoint, ask: "Could an attacker forge the sender identity? What would they gain?"

---

### T — Tampering

An attacker modifies data in transit or at rest without authorization.

**MMORPG example:** A cheating player intercepts the HTTPS response containing their character stats and replays a modified version with inflated values. Mitigation: the server is the authority; it never trusts client-reported state. All game state mutations are applied server-side from validated inputs.

**How to find Tampering threats:** For every data flow, ask: "What if the data is modified in transit? What if the stored record is modified directly?"

---

### R — Repudiation

A user denies performing an action, and the system cannot prove otherwise.

**MMORPG example:** A player completes an in-game purchase, then disputes the charge claiming they never initiated it. Without server-side transaction logging with timestamps, player IDs, and immutable records, the dispute cannot be resolved in the operator's favour.

**How to find Repudiation threats:** For every action with legal, financial, or irreversible consequences, ask: "What evidence would we produce if a player denied doing this?"

---

### I — Information Disclosure

Sensitive information is exposed to parties who should not have access.

**MMORPG example:** An API endpoint that returns a player's profile also returns the player's email address and IP address in a JSON field. An attacker enumerating player IDs can harvest PII for phishing or doxing campaigns.

**How to find Information Disclosure threats:** For every API response and log output, ask: "What data is included? Is all of it appropriate for the caller to see?"

---

### D — Denial of Service

An attacker prevents legitimate users from using the system.

**MMORPG example:** A botnet sends 50,000 unauthenticated WebSocket connection requests per second to the game server. Without connection rate limiting and authentication at the handshake, the server runs out of file descriptors and drops all player connections.

**How to find DoS threats:** For every resource the system allocates on incoming requests (connections, memory, database queries), ask: "What if an attacker sends 10,000 of these per second?"

---

### E — Elevation of Privilege

An attacker gains capabilities beyond what they were granted.

**MMORPG example:** A regular player discovers that appending `?admin=true` to an API request grants them access to GM (Game Master) command endpoints. The server checked the `admin` query parameter instead of the session's role, which the player could not forge — but the query parameter was not protected.

**How to find EoP threats:** For every privileged action (admin panel, GM commands, payment initiation, ban/kick), ask: "Could a regular authenticated user access this by manipulating any parameter, header, or cookie?"

---

## Likelihood and Impact Scoring

Use these anchored definitions, not generic "high/medium/low" intuitions:

### Likelihood

| Level | Definition |
|-------|-----------|
| **High** | A non-expert attacker could exploit this within an hour using freely available tools. The attack path is well-documented. |
| **Med** | Exploitation requires some skill or knowledge of the system internals. Attackers with moderate capability (script kiddies, competitive cheaters) could succeed. |
| **Low** | Exploitation requires significant expertise, privileged access, or a combination of multiple independent vulnerabilities. Nation-state level effort. |

### Impact

| Level | Definition |
|-------|-----------|
| **High** | Loss of PII for >100 users, financial loss, full service outage for >30 minutes, complete account takeover, or irreversible data corruption. |
| **Med** | Individual account affected, minor data exposure (no PII), partial service degradation, or recoverable data corruption. |
| **Low** | Nuisance-level: no data loss, no account compromise, limited service disruption affecting <1% of users. |

---

## Residual Risk Acceptance

A residual risk is an in-scope threat that is not fully mitigated. Every system has them. The question is not whether residual risks exist but whether they are consciously accepted.

**Acceptable residual risk criteria (ALL must be met):**
1. Likelihood is Low or Medium
2. Impact is Low
3. A compensating control exists (something that reduces the risk even without full mitigation)
4. A named owner is assigned
5. A review date or "permanent accept" rationale is documented

**Unacceptable residual risks:**
- High impact threats regardless of likelihood
- Any threat with no compensating control
- Any threat with no named owner ("the team" is not a named owner)
- Any threat where the justification is "we'll fix it later"

Unacceptable residual risks become items in the project health report. They do not block the block from closing, but they are visible to the project owner as open security debt.

---

## Review Cadence

A threat model is a living document. Update it when any of the following occur:

- A trust boundary changes (new service, new integration, new deployment target)
- A new authentication or session mechanism is introduced
- The data classification changes (e.g., the system now handles payment data it didn't before)
- A new entry point is added (new API endpoint, new WebSocket message type)
- A security incident reveals a gap in the model
- Annually for any active security-critical system

To check if a threat model is current: diff the trust boundary diagram and the entry point table against the current code. If they diverge, the model is stale — treat a stale model as absent and update it before writing new security-critical code.

End of threat-model-generation.md.
