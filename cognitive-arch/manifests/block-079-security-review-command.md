---
id: block-079
tier: S
kind: protocol
phase: phase-10
scope: phase-bound
status: planned
security: false
dependencies:
  - block-078
files:
  read:
    - protocols/stack-addenda/security.md
    - templates/threat-model.md
  modify: []
  create:
    - commands/security-review.md
gates:
  - name: command-created
    type: file-changed
    paths:
      - commands/security-review.md
  - name: outcomes-present
    type: command
    cmd: "grep -q \"PASS\\|WARN\\|FAIL\" commands/security-review.md"
    expect: exit 0
created_at: 2026-05-23
last_updated: 2026-05-23
---

# block-079 — Security Review Command

## Purpose

Create `commands/security-review.md` — the step-by-step procedure that must be run before closing any block with `security: true` in its manifest. The command produces one of three outcomes: PASS, WARN, or FAIL.

---

## Context

Axiom S5 mandates a security-review gate for all blocks touching auth, networking, or persistent data. Without a defined procedure, "run a security review" is not actionable. This command document provides a deterministic checklist that any implementer can execute, with clear criteria for each check and explicit rules for what constitutes a passing, warning, or failing result.

The command is not automated tooling — it is a structured manual review procedure. Future phases may introduce automated static analysis that supplements this review, but the human-executed procedure remains the canonical gate.

---

## Document to Create

**Path:** `commands/security-review.md`

The document must contain the following components:

### Header

- Command name: `security-review`
- When to run: before closing any block with `security: true` in its manifest
- Required inputs: the block ID being reviewed, the list of files modified by the block
- Output: PASS, WARN, or FAIL with a list of findings

### Pre-flight

Before beginning the five checks, confirm:
- The block's manifest has `security: true`
- The list of modified files is complete and final (no uncommitted changes pending)
- The reviewer has read `protocols/stack-addenda/security.md` within the past 30 days (or is doing so now)

### Check S1 — Input Validation

**Objective:** Verify that all external inputs handled by modified code are explicitly validated before use.

**Procedure:**
1. List every function or handler in the modified files that accepts data from an external source (HTTP request, WebSocket message, file upload, inter-service call, user-provided parameter).
2. For each: confirm that validation occurs before the data is used. Validation must check type, range/length, format, and origin where applicable.
3. Look specifically for: unvalidated query parameters passed to database queries, unvalidated user IDs used as resource keys, file upload handlers that trust the `Content-Type` header.
4. Check for blocklist-based validation (suspicious) vs. allowlist-based validation (correct).

**Findings classification:**
- FAIL: any external input reaches a database query, shell command, or privileged operation without validation
- WARN: validation is present but uses a blocklist pattern or misses one of the four validation dimensions (type/range/format/origin)
- PASS (S1): all external inputs are explicitly validated with allowlist logic

### Check S2 — Auth Chain Integrity

**Objective:** Verify that authentication, authorization, and action execution are distinct, sequential, and never short-circuited.

**Procedure:**
1. Identify all code paths in modified files where an action requires authentication or authorization.
2. For each path: trace from the entry point to the action execution. Confirm the sequence is: (a) verify identity, (b) verify permissions for that identity, (c) execute action.
3. Look for: missing authentication on endpoints that should require it, authorization checks that run before authentication is confirmed, combined auth+action functions with no separation, commented-out auth checks, TODO/FIXME annotations on auth logic.
4. If session token handling is present: confirm tokens are set as `httpOnly; Secure; SameSite=Strict`. Confirm server-side session invalidation on logout.
5. If this block has no auth or authorization code: document that explicitly and skip to S3.

**Findings classification:**
- FAIL: any action reachable without authentication when auth is required, or authorization bypassed
- FAIL: session tokens stored in localStorage or transmitted in URL parameters
- WARN: auth and authz logic interleaved in a single function but logically correct
- PASS (S2): full auth→authz→action chain intact, or no auth/authz code present (documented)

### Check S3 — Sensitive Data Protection

**Objective:** Verify that secrets, credentials, tokens, and PII are never hardcoded, logged, or transmitted in plaintext.

**Procedure:**
1. Scan all modified files for hardcoded secret patterns. Check for: `sk-ant-`, `sk-`, `password=`, `passwd=`, `secret=`, `api_key=`, `apikey=`, `token=`, `-----BEGIN`, `Authorization: Bearer [A-Za-z0-9]`, connection strings containing credentials.
2. Scan all log calls (`console.log`, `logger.info`, `log.debug`, `print`, `println`, etc.) in modified files. Flag any log call that includes: request body objects, user objects, auth-related fields, anything named `password`, `token`, `secret`, `key`, `credential`, `ssn`, `dob`, `email` in a context suggesting PII.
3. If the block introduces new data fields: confirm whether any new fields contain PII or sensitive data, and verify encryption/hashing requirements are addressed.
4. If the block introduces environment variable reads: confirm the variable names are documented and the code has no fallback to a hardcoded value.

**Findings classification:**
- FAIL: any hardcoded secret, credential, or private key found in modified files
- FAIL: log call that demonstrably outputs a password, token, or private key
- WARN: log call that might output sensitive data depending on object contents (e.g., `log(requestBody)` without field scrubbing)
- WARN: new PII field with no documented encryption strategy
- PASS (S3): no hardcoded secrets, no sensitive field logging, PII handling documented

### Check S4 — Threat Model Existence

**Objective:** Verify that a threat model exists in `design/` for the system this block touches, per axiom S4.

**Procedure:**
1. Identify which system(s) the modified files belong to (e.g., authentication service, game state synchronization, payment processing, player data API).
2. Check `design/` for a file matching `threat-model-<system>.md` or equivalent.
3. If a threat model exists: confirm it covers the specific functionality modified by this block. If the block adds a new trust boundary, new attack surface entry point, or new data category, the threat model must have been updated.
4. If no threat model exists for a security-critical system: this is a FAIL regardless of the quality of the code.

**Findings classification:**
- FAIL: no threat model exists in `design/` for the security-critical system this block modifies
- FAIL: threat model exists but does not cover the attack surface introduced or modified by this block
- WARN: threat model exists and covers the system, but has not been updated in over 6 months and the system has changed
- PASS (S4): current, relevant threat model exists and covers this block's changes

### Check S5 — Gate Confirmation (Meta-Check)

**Objective:** Confirm that this review is being run, that its result will be recorded, and that the block's manifest correctly declares `security: true`.

**Procedure:**
1. Confirm the block's manifest file exists and contains `security: true`.
2. Confirm this review is being performed before the block is marked closed (not retroactively).
3. Confirm the reviewer's name and the review date will be recorded in the block's retrospective or closing notes.
4. Confirm all four preceding checks (S1-S4) have been completed and findings documented.

**Findings classification:**
- FAIL: manifest does not have `security: true` (block should not be in this review)
- FAIL: review is being run after the block was already closed
- WARN: no retrospective file exists to record the result in
- PASS (S5): manifest correct, review pre-close, result will be recorded

---

### Outcome Determination

After all five checks are complete, determine the overall outcome:

**PASS** — All five checks returned PASS. The block may be closed. Record "security-review: PASS" in the block's closing notes with the reviewer name and date.

**WARN** — One or more checks returned WARN, no checks returned FAIL. The block may be closed only if each WARN finding is explicitly triaged: documented with a written justification for acceptance and a named owner responsible for follow-up. Unacknowledged WARNs are treated as FAIL. Record "security-review: WARN — [count] finding(s) accepted" in closing notes.

**FAIL** — One or more checks returned FAIL. The block cannot be closed. The FAIL finding(s) must be resolved and the review re-run. Do not mark the block as closed under any circumstances until a PASS or acknowledged WARN result is achieved. Record nothing in closing notes until the re-run produces a non-FAIL result.

---

### Recording Results

After the review, record the following in the block's retrospective or closing notes section:

```
security-review: [PASS | WARN | FAIL]
reviewer: [name]
date: [YYYY-MM-DD]
findings: [count] — [brief description or "none"]
```

---

## Implementation Steps

1. Read `protocols/stack-addenda/security.md` to ensure the five checks accurately reflect the conventions defined there.
2. Read `templates/threat-model.md` to ensure the S4 check correctly references the template's expected location and structure.
3. Write `commands/security-review.md` with all sections as described above.
4. Ensure the document contains the words PASS, WARN, and FAIL in the outcome section (gate requirement).

---

## Acceptance Criteria

- `commands/security-review.md` exists and contains a procedure with five checks (S1-S5).
- Each check has explicit PASS, WARN, and FAIL criteria.
- The document contains an outcome determination section with PASS, WARN, and FAIL outcomes defined.
- The document specifies that FAIL blocks cannot be closed.
- `grep -q "PASS\|WARN\|FAIL" commands/security-review.md` exits 0.
- The document references `protocols/stack-addenda/security.md` and `templates/threat-model.md`.

---

## Notes

- The command is a manual procedure, not a script. Future automation is possible but this block establishes the human-executable baseline.
- Check S5 (the meta-check) may seem circular, but its purpose is to prevent the gate from being silently skipped. An automated system cannot skip a check that explicitly asks "is this review being run?"
- The WARN outcome exists to avoid a binary PASS/FAIL dynamic that would incentivize reviewers to ignore real issues rather than surface them as non-blocking concerns.
