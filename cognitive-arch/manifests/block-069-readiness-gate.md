---
id: block-069
tier: S
kind: protocol
phase: phase-9
scope: phase-bound
status: planned
dependencies:
  - block-068
files:
  read:
    - protocols/phase-generation.md
  modify:
    - protocols/phase-generation.md
  create:
    - protocols/readiness-gate.md
    - templates/readiness-questionnaire.md
gates:
  - name: readiness-gate-protocol-exists
    type: file-changed
    paths: [protocols/readiness-gate.md]
  - name: readiness-questionnaire-template-exists
    type: file-changed
    paths: [templates/readiness-questionnaire.md]
  - name: phase-generation-references-gate
    type: file-changed
    paths: [protocols/phase-generation.md]
created_at: 2026-05-23
---

# block-069 — Readiness Gate

## Purpose

Generating a phase outline for a system that is poorly understood produces a skeleton that will be rewritten multiple times as understanding improves. This is a waste that compounds: later blocks reference the skeleton phase, manifests are written against vague goals, and the refactoring cost grows with each new dependency.

The Readiness Gate prevents this failure mode by requiring a minimum level of domain knowledge before any phase generation is permitted. If the gate fails, the AI executor does not attempt to generate a phase. Instead, it generates a structured questionnaire that targets the specific gaps that caused the gate to fail. The human fills the questionnaire, which fills the knowledge gaps, and the gate is retried.

This block delivers:

1. `protocols/readiness-gate.md` — the gate definition: four readiness criteria, the evaluation procedure for each, and the rule that a single failing criterion blocks phase generation.
2. `templates/readiness-questionnaire.md` — the template for the questionnaire document created when the gate fails.
3. A modification to `protocols/phase-generation.md` — adding Step 0 "Run readiness gate" before any other step.

## Dependencies

- **block-068** must be complete. The readiness gate references the domain-coverage-matrix protocol and the coverage-check command, because one of the readiness criteria requires that at least one design/ file beyond the domain overview exists (domain has depth), which is the same source of truth used by the coverage matrix.

## Files

### Read
- `protocols/phase-generation.md` — to understand the current step structure before adding Step 0.

### Modify
- `protocols/phase-generation.md` — prepend Step 0: readiness gate check.

### Create

**`protocols/readiness-gate.md`**

Must contain the following sections:

**Section 1 — Purpose and Rule**

The readiness gate is evaluated once before generating any new phase or roadmap. If any single criterion fails, phase generation is aborted. The executor generates a readiness questionnaire instead. The questionnaire is saved to `_brainstorm/readiness-questionnaire-YYYY-MM-DD.md`. The human fills the questionnaire. After the human indicates the questionnaire is complete, the gate is re-evaluated from scratch.

The executor MUST NOT attempt to infer missing answers from context or generate a "partial" phase. The gate is binary: pass or fail.

**Section 2 — Readiness Criteria**

Criterion R1 — PROJECT.md completeness.
- Check: PROJECT.md exists at the project root.
- Check: PROJECT.md contains values for all 10 required fields (as defined in the project's PROJECT.md template).
- Check: No field contains placeholder text matching the patterns: "[TBD]", "[placeholder]", "[TODO]", "TBD", "TODO", or an empty string.
- Pass condition: All 10 fields present, none contain placeholder patterns.
- Fail message: "PROJECT.md is incomplete. Missing or placeholder fields: [list fields]."

Criterion R2 — Domain overview depth.
- Check: `design/02-domain-overview.md` exists.
- Check: The file contains at least 3 named systems. A named system is a section heading (##) or table row that names a system and provides at least one sentence of description.
- Pass condition: File exists and contains at least 3 named systems with descriptions.
- Fail message: "Domain overview has fewer than 3 named systems. Document more systems before generating phases."

Criterion R3 — Design corpus depth.
- Check: At least one design/ file beyond `design/02-domain-overview.md` exists. This file must be non-empty and must describe a specific system or subsystem in detail (more than 50 words).
- Pass condition: At least one qualifying design/ file (beyond the overview) exists.
- Fail message: "No detailed design/ files found beyond the domain overview. At least one system must be documented in depth before generating a phase."

Criterion R4 — Target user specificity.
- Check: PROJECT.md contains a `target_users` field (or equivalent section).
- Check: The value is specific. Fail patterns: "everyone", "users", "all users", "general users", "people", "anyone", or any value shorter than 10 characters.
- Pass condition: Target users description is specific (does not match fail patterns and is at least 10 characters long).
- Fail message: "Target users description is not specific enough. Describe who uses this project and why."

**Section 3 — Evaluation Procedure**

Step 1: Evaluate R1. If fail, record failure. Do not stop — evaluate all criteria before generating the questionnaire.
Step 2: Evaluate R2. If fail, record failure.
Step 3: Evaluate R3. If fail, record failure.
Step 4: Evaluate R4. If fail, record failure.
Step 5: If any failures recorded, generate questionnaire from `templates/readiness-questionnaire.md`. Save to `_brainstorm/readiness-questionnaire-YYYY-MM-DD.md`. Report: "Readiness gate failed. [N] criteria failed. Questionnaire saved to _brainstorm/readiness-questionnaire-YYYY-MM-DD.md. Please fill it and retry."
Step 6: If no failures, report: "Readiness gate passed. Proceeding to phase generation." Continue with phase-generation Step 1.

**Section 4 — Retry Policy**

After the human fills the questionnaire, they signal readiness by saying "Readiness questionnaire complete" or "Retry readiness gate." The executor re-evaluates all four criteria from scratch. Criteria that previously failed and now pass are cleared. If any criterion still fails, a new questionnaire is generated (with today's date in the filename). Previous questionnaires are not modified.

---

**`templates/readiness-questionnaire.md`**

Must contain the following structure:

```
---
type: readiness-questionnaire
project: [PROJECT NAME]
gate_date: YYYY-MM-DD
failing_criteria: []
created_at: YYYY-MM-DD
---

# Readiness Questionnaire — [PROJECT NAME]

This questionnaire was generated because the Readiness Gate failed on [DATE].
Fill in every section marked with [ANSWER HERE] before retrying phase generation.

---

## Criterion R1 — PROJECT.md Completeness

[This section appears only if R1 failed.]

The following fields in PROJECT.md are missing or contain placeholder text:

[LIST OF FAILING FIELDS]

For each field below, provide a complete, non-placeholder answer:

**Field: [field_name]**
[ANSWER HERE]

---

## Criterion R2 — Domain Overview Depth

[This section appears only if R2 failed.]

Your domain overview currently has [N] named systems. At least 3 are required.

Please describe [3 - N] additional systems:

**System [N+1] Name:**
[ANSWER HERE]

**System [N+1] Description (what it does, who uses it, why it matters):**
[ANSWER HERE]

[Repeat for each missing system.]

---

## Criterion R3 — Design Corpus Depth

[This section appears only if R3 failed.]

No detailed design/ file exists beyond the domain overview. Choose one system from your domain overview and answer:

**System to document in depth:**
[ANSWER HERE]

**Responsibilities (what does this system do?):**
[ANSWER HERE]

**Key interfaces (what does it expose to other systems?):**
[ANSWER HERE]

**Constraints (performance, security, compatibility, etc.):**
[ANSWER HERE]

**Open questions (what is not yet decided about this system?):**
[ANSWER HERE]

---

## Criterion R4 — Target User Specificity

[This section appears only if R4 failed.]

The current target_users value is: "[CURRENT VALUE]"

This is too generic. Answer the following:

**Who are your primary users? (role, context, technical level):**
[ANSWER HERE]

**What problem are they solving when they use this project?**
[ANSWER HERE]

**What would they lose if this project did not exist?**
[ANSWER HERE]

---

## Completion Checklist

- [ ] All [ANSWER HERE] fields are filled.
- [ ] No field still contains placeholder text.
- [ ] I have updated PROJECT.md and/or design/ files with the answers above.
- [ ] I am ready to retry the readiness gate.

When all boxes are checked, say: "Readiness questionnaire complete."
```

---

**Modification to `protocols/phase-generation.md`**

Prepend the following text to the file, before the current Step 1:

```
## Step 0 — Readiness Gate (REQUIRED)

Before generating any phase, the readiness gate must pass. Run the readiness gate evaluation defined in `protocols/readiness-gate.md`.

- If the gate PASSES: continue to Step 1.
- If the gate FAILS: stop. Generate the readiness questionnaire. Do not proceed to Step 1. Wait for human to complete the questionnaire and signal retry.

This step is mandatory and cannot be skipped. A phase generated without passing the readiness gate is invalid and must be deleted.
```

## Validation

- `protocols/readiness-gate.md` exists and defines all four criteria (R1, R2, R3, R4) with explicit pass conditions and fail messages.
- `protocols/readiness-gate.md` contains the binary rule: "single failing criterion blocks phase generation."
- `protocols/readiness-gate.md` contains a Retry Policy section.
- `templates/readiness-questionnaire.md` exists and contains sections for all four criteria.
- `protocols/phase-generation.md` contains "Step 0" text referencing the readiness gate.
- `protocols/phase-generation.md` contains the phrase "mandatory and cannot be skipped."

## Gates

| Gate | Type | Path(s) | Condition |
|------|------|---------|-----------|
| readiness-gate-protocol-exists | file-changed | protocols/readiness-gate.md | File must exist and define ≥4 criteria |
| readiness-questionnaire-template-exists | file-changed | templates/readiness-questionnaire.md | File must exist and be non-empty |
| phase-generation-references-gate | file-changed | protocols/phase-generation.md | File must contain "Step 0" and "readiness gate" |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Gate too strict — legitimate projects with minimal design/ are blocked | Medium | Medium | R3 requires only one detailed design/ file (50+ words); threshold is intentionally low |
| Placeholder detection regex causes false positives on legitimate content | Low | Low | Fail patterns are limited to well-known placeholder strings; partial matches are not flagged |
| Human fills questionnaire superficially to pass the gate | Low | Medium | Gate evaluates PROJECT.md and design/ files directly, not the questionnaire; superficial answers that are not propagated to source files will not pass |
| phase-generation.md modification breaks its existing step numbering | Low | Low | Step 0 is prepended; existing steps are renumbered N+1 in a separate editing pass if needed |

## Out of Scope

- Automated updating of PROJECT.md or design/ files from questionnaire answers. The human must transfer answers manually.
- Readiness criteria for specific domains (game development, finance, etc.). The four criteria are domain-agnostic.
- A UI for the readiness gate. This is a markdown-only protocol.
- Versioning of questionnaire responses over time.
