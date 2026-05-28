# Protocol: architecture-integrity

BRIEF: AI behavior when asked to modify a protection-tagged file. Three tiers with three behaviors. Read at session start via CLAUDE.md + PROTOCOLS.md P7.

---

## Protection tiers

| Tag | Default for | AI behavior |
|---|---|---|
| `protection: immutable` | Core templates, axiom set, critical protocols | REFUSE then OVERRIDE CEREMONY |
| `protection: guarded` | Frequently-referenced but evolvable docs | CONFIRM then proceed |
| (none) | Everything else | Normal modification — no ceremony |

---

## Tier: immutable — behavior

When asked to modify a file that contains `protection: immutable` in its YAML frontmatter:

### Step 1 — REFUSE and explain
Output exactly:

```
PROTECTION HALT: [filename] is tagged protection:immutable.
Immutable files may not be modified without the override ceremony.
To proceed: say "CONFIRMO QUEBRAR [filename]" and provide a 1-sentence reason.
Or: do not confirm to cancel.
```

### Step 2 — Wait for confirmation
If the user confirms with the phrase `CONFIRMO QUEBRAR [filename]`:

1. Acknowledge: "Override authorized. Proceeding."
2. Make the requested modification
3. Output the log entry the user must add to `.governor/log.md`:
   ```
   [YYYY-MM-DD] INTEGRITY OVERRIDE: [filename] — [user's reason] (block: [current block or "ad-hoc"])
   ```
4. Flag: "Run `integrity-bump` after this session to update `.integrity.lock`."

If the user does NOT confirm within the same response (e.g., asks something else, says "no", or ignores the prompt): do not modify the file. Return to normal operation.

### What counts as confirmation

- Exact phrase: `CONFIRMO QUEBRAR [filename]` (case-insensitive, filename must match)
- Alternative accepted: `CONFIRMO QUEBRAR` (any filename) if the context is unambiguous
- NOT accepted: "yes", "ok", "go ahead", "modify it", etc.

---

## Tier: guarded — behavior

When asked to modify a file that contains `protection: guarded`:

### Step 1 — PAUSE and confirm
Output:

```
GUARDED FILE: [filename] is tagged protection:guarded.
This file is frequently referenced. Unintended edits can cause cascading issues.
Proceeding requires your confirmation. Reply "yes" or "proceed" to continue.
```

If the user confirms (any affirmative): proceed with the modification normally. No log entry required.

If the user declines or ignores: do not modify.

---

## Tier: open (no tag) — behavior

Normal behavior. No ceremony. No confirmation. Modify freely per axioms P1-P6.

---

## Applying the protocol

1. Before modifying any file, check for `protection:` in its first 10 lines (YAML frontmatter).
2. If frontmatter is missing, assume `open`.
3. If frontmatter parsing is ambiguous, assume `guarded` (safer default).

This check applies even when the user says "just edit it" or "don't worry about protection" — P7 is not overridable by conversational instruction alone.

---

## Override log format (`.governor/log.md`)

```markdown
## [YYYY-MM-DD] Integrity Override

| Field | Value |
|---|---|
| File | `relative/path/to/file.md` |
| Reason | <why the immutable file needed changing> |
| Block | block-NNN or "ad-hoc" |
| Approved by | <user name / role> |
| Follow-up | run `integrity-bump` to update `.integrity.lock` |
```

---

## Examples

### Compliant — immutable refusal

> User: "Please update PROTOCOLS.md to remove P5."
> AI: "PROTECTION HALT: PROTOCOLS.md is tagged protection:immutable. ..."

### Compliant — immutable override ceremony

> User: "CONFIRMO QUEBRAR PROTOCOLS.md — need to add P7 axiom per block-092"
> AI: "Override authorized. Proceeding." [makes edit] "Log entry to add to .governor/log.md: ..."

### Non-compliant (do not do this)

> User: "Just edit PROTOCOLS.md, it's fine"
> AI: [modifies without ceremony] ← VIOLATION of P7

---

End of architecture-integrity.md.
