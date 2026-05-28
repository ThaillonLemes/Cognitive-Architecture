# security-review

BRIEF: Mandatory pre-close procedure for blocks with `security: true`. Produces PASS, WARN, or FAIL. A FAIL result blocks close — no exceptions.

**Axiom:** S5 — `PROTOCOLS.md § Security Axioms (S)`
**Conventions reference:** `protocols/stack-addenda/security.md`
**Threat model template:** `templates/threat-model.md`

---

## When to Run

Run this command **before closing** any block whose manifest frontmatter contains `security: true`. This includes blocks that:

- Implement or modify authentication or session management
- Handle WebSocket connections or network protocol logic
- Write to persistent storage (databases, file systems, caches)
- Process or store PII, credentials, tokens, or financial data
- Implement cryptographic operations

Running this review retroactively (after the block is already closed) is a FAIL on Check S5 — it does not count.

---

## Required Inputs

- **Block ID:** The ID of the block being reviewed (e.g., `block-042`)
- **Modified files:** The complete list of files modified by this block (from the manifest `files.modify` + `files.create`)
- **Reviewer:** The name of the person conducting this review (cannot be the sole implementer of the block)

---

## Pre-flight

Before running the five checks, confirm:

- [ ] The block's manifest has `security: true` in its frontmatter
- [ ] The list of modified files is final — no uncommitted changes pending
- [ ] You have read `protocols/stack-addenda/security.md` within the past 30 days (or are reading it now)
- [ ] You are NOT running this review retroactively — the block is still open

If any pre-flight item is not met, stop. Do not run the review until pre-flight passes.

---

## Check S1 — Input Validation

**Objective:** All external inputs handled by modified code are explicitly validated before use.

**Procedure:**
1. List every function or handler in the modified files that accepts data from an external source (HTTP request body, query parameter, path parameter, WebSocket message, file upload, inter-service call, environment variable, user-provided ID).
2. For each function/handler: confirm validation occurs **before** the data is used. Validation must address:
   - **Type** — is the value the expected type?
   - **Range / length** — is the value within acceptable bounds?
   - **Format** — does the value match the expected pattern (e.g., UUID, ISO date)?
   - **Origin** — is the caller authorized to supply this value?
3. Look specifically for:
   - Unvalidated query parameters passed to database queries
   - Client-supplied resource IDs used as database keys without ownership verification
   - File upload handlers that trust `Content-Type` header alone (not magic bytes)
   - Negative numbers, zero values, or extreme values that could cause server-side underflow/overflow
4. Identify whether validation uses **allowlist** (permitted values enumerated) or **blocklist** (forbidden values listed). Allowlist is correct; blocklist is a WARN.

**Classify each finding, then assign the check's result:**
- **FAIL (S1):** Any unvalidated external input reaches a database query, shell command, template engine, or privileged operation
- **WARN (S1):** Validation is present but uses a blocklist pattern, or misses one of the four validation dimensions (type/range/format/origin)
- **PASS (S1):** All external inputs are explicitly validated with allowlist logic before use

**Check S1 result:** `[ ] PASS  [ ] WARN  [ ] FAIL`

Findings:
```
[document each finding here, or "none"]
```

---

## Check S2 — Auth Chain Integrity

**Objective:** Authentication → Authorization → Action. Never skipped, never reordered, never combined.

**Procedure:**
1. Identify all code paths in modified files where an action requires authentication or authorization.
2. For each path: trace from entry point to action execution. Verify the sequence is:
   (a) verify identity (authentication) → (b) verify permissions for that identity (authorization) → (c) execute action
3. Look specifically for:
   - Endpoints that should require auth but do not check for a valid session
   - Authorization checks that run before authentication is confirmed
   - Auth + action logic combined in a single function with no separation
   - Commented-out auth checks or TODO/FIXME annotations on auth logic
   - "Fast path" code that bypasses auth "for performance" or "for internal calls"
4. If session token handling is present:
   - Tokens must be set as `httpOnly; Secure; SameSite=Strict` cookies
   - Server-side session invalidation must occur on logout (clearing the cookie alone is insufficient)
5. If this block contains no auth or authorization code: document this explicitly. The check still passes — the absence must be intentional and documented, not accidental.

**Classify each finding:**
- **FAIL (S2):** Any authenticated action reachable without authentication; authorization bypassed; session tokens in `localStorage`, `sessionStorage`, or URL parameters
- **WARN (S2):** Auth and authz logic interleaved in a single function but logically correct order preserved; no unit test coverage for auth path
- **PASS (S2):** Full auth → authz → action chain intact for all protected actions; OR no auth/authz code present in this block (documented)

**Check S2 result:** `[ ] PASS  [ ] WARN  [ ] FAIL`

Findings:
```
[document each finding here, or "none / no auth code in this block"]
```

---

## Check S3 — Sensitive Data Protection

**Objective:** No secrets hardcoded. No PII or credentials in logs. Sensitive data encrypted in transit and at rest.

**Procedure:**
1. **Scan for hardcoded secrets.** Search all modified files for:
   - API key patterns: `sk-ant-`, `sk-`, `AKIA`, `ghp_`, or similar
   - Credential assignments: `password=`, `passwd=`, `secret=`, `api_key=`, `token=` followed by a non-placeholder value
   - Private key markers: `-----BEGIN`
   - Connection strings with embedded credentials
   - Authorization headers with literal token values

2. **Scan log calls.** For each `console.log`, `logger.info/warn/error/debug`, `log.`, `print()`, `println!()`, or equivalent in modified files:
   - Flag any call that includes: request body objects, user objects, error objects from auth failures
   - Flag any call that logs a field named `password`, `token`, `secret`, `key`, `credential`, `ssn`, `dob`, `email`, `card`, `cvv`, or similar
   - Flag any call that logs a full exception stack trace that might include credentials in the exception message

3. **New data fields.** If the block introduces new data fields in a database schema or data model:
   - Identify whether any new field contains PII or sensitive data
   - Confirm encryption, hashing, or masking requirements are documented and implemented

4. **Environment variable reads.** If the block reads environment variables:
   - Confirm the variable names are documented
   - Confirm the code has no fallback to a hardcoded value if the env var is absent (fail-closed, not fail-open)

**Classify each finding:**
- **FAIL (S3):** Any hardcoded secret, credential, or private key in modified files; log call that demonstrably outputs a password, token, or private key
- **WARN (S3):** Log call that might expose sensitive data depending on object contents (e.g., `log(requestBody)` without field scrubbing); new PII field with no documented encryption strategy
- **PASS (S3):** No hardcoded secrets; no sensitive field logging; all PII handling documented and implemented

**Check S3 result:** `[ ] PASS  [ ] WARN  [ ] FAIL`

Findings:
```
[document each finding here, or "none"]
```

---

## Check S4 — Threat Model Existence

**Objective:** A current threat model in `design/` covers the security-critical system this block modifies.

**Procedure:**
1. Identify which system(s) the modified files belong to (e.g., authentication service, game state synchronization, payment processing).
2. Check `design/` for `threat-model-<system>.md` or an equivalent threat model document.
3. If a threat model exists:
   - Confirm it covers the specific functionality modified by this block
   - If this block adds a new trust boundary, new attack surface entry point, or new data category: confirm the threat model was updated to reflect this
   - Check the `last_updated` date — if the model is over 6 months old and the system has changed, flag as WARN
4. If no threat model exists for a system classified as security-critical: this is a FAIL, regardless of code quality.

**Classify each finding:**
- **FAIL (S4):** No threat model in `design/` for the security-critical system this block modifies; OR threat model exists but does not cover the attack surface introduced or modified by this block
- **WARN (S4):** Threat model exists and covers the system, but has not been updated in over 6 months while the system has changed
- **PASS (S4):** Current, relevant threat model exists and covers this block's changes

**Check S4 result:** `[ ] PASS  [ ] WARN  [ ] FAIL`

Findings:
```
[document each finding here, or "threat model found at design/threat-model-<system>.md, covers this block's changes"]
```

---

## Check S5 — Gate Confirmation (Meta-Check)

**Objective:** Confirm this review is properly positioned (pre-close), its result will be recorded, and the manifest is correct.

**Procedure:**
1. Confirm the block's manifest file exists and contains `security: true` in its frontmatter
2. Confirm this review is being run **before** the block is marked closed — not retroactively
3. Confirm the reviewer's name and the review date will be recorded in the block's retrospective or closing notes
4. Confirm all four preceding checks (S1-S4) have been completed and findings documented in this review run

**Classify each finding:**
- **FAIL (S5):** Manifest does not have `security: true`; OR review is being run after the block was already closed
- **WARN (S5):** No retrospective file yet exists to record the result in (create it before closing)
- **PASS (S5):** Manifest correct, review pre-close, result will be recorded

**Check S5 result:** `[ ] PASS  [ ] WARN  [ ] FAIL`

Findings:
```
[document each finding here, or "manifest confirmed, review pre-close, retrospective ready"]
```

---

## Outcome Determination

Determine the overall outcome after all five checks are complete.

---

**PASS** — All five checks returned PASS.

The block may be closed. Record in closing notes:
```
security-review: PASS
reviewer: [name]
date: [YYYY-MM-DD]
findings: 0 — none
```

---

**WARN** — One or more checks returned WARN; no checks returned FAIL.

The block may be closed **only if** each WARN finding is explicitly triaged:
- Document the finding
- Provide written justification for why it is accepted at this time
- Assign a named owner for follow-up
- Set a target date or declare "permanent accept" with rationale

Unacknowledged WARNs are treated as FAIL. Record in closing notes:
```
security-review: WARN
reviewer: [name]
date: [YYYY-MM-DD]
findings: [N] — [brief description of each WARN and acceptance rationale]
```

---

**FAIL** — One or more checks returned FAIL.

The block **cannot be closed**. Do not record anything in closing notes.

Steps to resolve:
1. Fix every FAIL finding in the code
2. Re-run this entire review procedure from pre-flight
3. The review is complete only when re-run produces PASS or acknowledged WARN

Do not mark the block closed under any circumstances until a PASS or acknowledged WARN result is achieved.

---

## Recording Results

After a PASS or acknowledged WARN outcome, record the following in the block's retrospective or closing notes:

```
security-review: [PASS | WARN]
reviewer: [name]
date: [YYYY-MM-DD]
findings: [count] — [brief description or "none"]
s1-input-validation: [PASS | WARN | FAIL]
s2-auth-chain: [PASS | WARN | FAIL]
s3-data-protection: [PASS | WARN | FAIL]
s4-threat-model: [PASS | WARN | FAIL]
s5-gate-confirmation: [PASS | WARN | FAIL]
```

End of security-review.md.
