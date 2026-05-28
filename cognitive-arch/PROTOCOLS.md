---
protection: immutable
protection_reason: "Core axiom set (P/Q/C/S). Changing axioms is an ADR event, not a block edit."
restore_command: "git checkout HEAD -- PROTOCOLS.md"
---

# PROTOCOLS — universal axioms for cognitive architecture

BRIEF: 24 axioms (P/Q/C/S) + Charter. Most are universal; some are marked `[code-only]` or `[code-leaning]`. Apply to every file, every block, every agent. Override only with explicit `axiom_override:` in manifest frontmatter.

---

## P — Principles (guiding ideals)

**P1. Determinism over creativity in structure.** Templates + protocols govern file generation. Content varies; structure does not.

**P2. Evidence over claims.** A block is not "done" because the agent says so. It is done when audit-checkable artifacts prove it.

**P3. Single source of truth.** Each fact lives in exactly one file. Other files point to it; they do not restate.

**P4. Pointer integrity.** Every reference to another file must resolve. Broken pointers are audit errors.

**P5. Slim boot.** HOT files (read at session start) are minimal. Detail lives in WARM/COLD files reached on demand via INDEX.md.

**P6. AI-first format for HOT files.** Vocabulary from `_syntax.md`. Dense key:value. No prose where data suffices.

**P7. Architecture protection respected.** Files tagged `protection: immutable` are never modified without an explicit override ceremony (confirmation phrase + log entry). Files tagged `protection: guarded` require textual confirmation before modification. Untagged files are `open` — normal modification. See `protocols/architecture-integrity.md`.

---

## Q — Quality (testable rules)

**Q1. Rule of Three for shared abstractions** *[code-leaning]*. Do not introduce a shared abstraction — trait, generic, base class, utility module, template, or protocol helper — on the first occurrence. Do not introduce one on the second occurrence. On the third, evaluate and justify in manifest section "New abstraction". Applies to: source code, template duplication, protocol fragmentation, repeated config patterns.

**Q2. File size budgets.** Each HOT file has a maximum size. Audit warns if exceeded. Default budgets:
- CLAUDE.md ≤ 60 lines
- STATE.md ≤ 60 lines
- NEXT.md ≤ 30 lines
- INDEX.md ≤ 250 lines
- board.md ≤ 150 lines
- AGENT.md ≤ 50 lines (per agent)

Token estimate (proxy): chars÷4. HOT boot target: **< 4,000 tok total**. Single HOT file soft cap: **1,000 tok**. Run `/token-audit` for breakdown. (SDK-exact measurement: Phase 5.)

**Q3. Manifests precede work artifacts.** No work artifact (code, document, config, asset, design) is produced before its manifest exists and validates against its tier schema.

**Q4. Gates pass before commit.** A block does not commit unless all declared gates pass OR the user explicitly applies a `forced_pass` flag with rationale.

**Q5. Dependencies must be Complete.** A block does not start if any block in `dependencies:` is not status `done`.

**Q6. Files declared exhaustively.** Manifest `files.read`, `files.modify`, `files.create` enumerate every file touched. No surprises.

**Q7. Out of scope is explicit.** Every manifest declares deferrals to prevent scope creep.

---

## C — Charter (documentation rules)

**C1. Code header is mandatory** *[code-only]*. Every code file (`.rs`, `.ts`, `.py`, `.go`, `.java`, `.cpp`, etc.) begins with a header per `protocols/code-header-protocol.md`. 3-5 lines: PURPOSE, INPUTS, OUTPUTS, DEPS, SEE. Doc-only / design-only / content projects skip this charter item.

**C2. No speculation in documentation.** Documentation (code comments, markdown docs, manifests, retrospectives) describes what IS, what WAS, or what WILL DEFINITELY BE. Not what "might" be, "could" be, or "should be refactored to" be. Speculation belongs in ADRs as Open Questions, not in canonical docs.

**C3. BRIEF on large markdown files.** Markdown files over 100 lines begin with a `BRIEF:` section (1-3 lines) summarizing the file. Allows scanning.

**C4. AI-only files use `_syntax.md` vocabulary.** STATE.md, NEXT.md, board.md, INDEX.md, AGENT.md follow the dense key:value format defined in `_syntax.md`. No prose.

**C5. ADR for non-obvious decisions.** Architectural decisions go in `decisions/ADR-NNN-<slug>.md`. The code/doc references the ADR ID, not the rationale.

**C6. Retrospectives are facts, not stories.** Block and phase retrospectives list what was built, what gates passed, what was deferred. Not narrative prose.

---

## S — Security Axioms

**S1: Untrusted Input.** Every input is untrusted until explicitly validated. Validate type, range, format, and origin before processing any external data. "External" includes HTTP requests, WebSocket messages, file uploads, environment variables read at runtime, and inter-service calls.

**S2: Auth Chain Integrity.** Authentication before authorization, authorization before action. Never skip or short-circuit this chain. Verify identity first, then check permissions against that identity, then execute the requested action. A missing link in this chain is a hard security violation regardless of context.

**S3: Sensitive Data Protection.** Sensitive data is never logged, never hardcoded, and never transmitted in plaintext. API keys, passwords, session tokens, and PII are always encrypted at rest and in transit. Violation of this axiom is grounds for immediate block rollback.

**S4: Threat Model First.** *[code-only]* A threat model must be documented in `design/` before writing any security-critical code. "Security-critical" means any code that handles authentication, cryptography, session management, inter-service trust, or network protocol implementation. No threat model means no code.

**S5: Security Gate Mandatory.** *[code-only]* Every block touching authentication, networking, or persistent data requires a security-review gate. This is not optional and cannot be deferred. A block with `security: true` in its manifest cannot be closed without a passing or warning-level security review result.

---

## Markers

- *[code-only]* — axiom applies ONLY to projects with source code. Doc-only / design-only / content projects skip these.
- *[code-leaning]* — axiom originated for code but the wording above generalizes to other artifact types (templates, protocols, configs).
- (no marker) — universal; applies to all project types.

Current markers:
- C1 → `[code-only]`
- Q1 → `[code-leaning]`
- S4 → `[code-only]`
- S5 → `[code-only]`

**P-TOK-1. Track actual token cost on every block.** Every block retrospective must record `tok_actual` (user-reported token count for the block). Budget overrun at phase level triggers a governance review. Advisory at phase level; hard enforcement at block-close (see `sdk/block_close.py`). Added Phase 18.

---

## Axiom override protocol

A block may override a single axiom for a justified reason. Add to manifest YAML frontmatter:

```yaml
axiom_override: "P-5 — slim boot violated because [reason]"
```

Audit logs the override. Override accumulation > 5 instances in last 30 days = audit warning (drift signal).

---

## Authority and modes

Agent behavior depends on its mode. See `protocols/modes.md`:
- **Guidance** (default, during block work): conversational, suggest, speculate
- **Guardrails** (block-start, block-close, phase transitions): check drift, validate vs axioms
- **Checklist** (audit, integrate, gate validation): strict yes/no on evidence; no speculation

The Governor agent uses guardrails/checklist permanently. Implementers default to guidance.

---

## Reading order at session start

1. PROTOCOLS.md (this file)
2. STATE.md
3. NEXT.md
4. INDEX.md (only if more context needed)
5. AGENT.md for your role (multi-agent only)
6. Active block manifest (when working a block)

End of PROTOCOLS.md.
