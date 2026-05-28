---
id: block-061
tier: S
kind: protocol
phase: phase-8
scope: phase-bound
status: planned
dependencies: []
files:
  read:
    - commands/phase-start.md
  modify:
    - commands/phase-start.md
  create:
    - protocols/phase-quality-rubric.md
gates:
  - name: rubric-file-exists
    type: file-changed
    paths: [protocols/phase-quality-rubric.md]
  - name: phase-start-updated
    type: file-changed
    paths: [commands/phase-start.md]
  - name: rubric-has-eight-criteria
    cmd: grep -c "^[0-9]\+\." protocols/phase-quality-rubric.md
    expect: "exit 0 with count >= 8"
created_at: 2026-05-23
---

# Block 061 — Phase Quality Rubric

- **Tier:** S
- **Kind:** protocol
- **Status:** planned

---

## 1. Purpose

Create `protocols/phase-quality-rubric.md` containing at least 8 measurable criteria that must be satisfied before any generated phase is accepted and work begins. Without a rubric, phase quality depends on the AI's intuition, which produces inconsistent results — vague exit criteria, unrealistic block counts, missing test gates, or phases with no user-visible outcome.

This block also modifies `commands/phase-start.md` to add an explicit step that invokes the rubric check as part of the phase acceptance workflow.

**Target file to create:** `protocols/phase-quality-rubric.md`

**Content of `protocols/phase-quality-rubric.md` must include:**

1. **Block count in range [5, 12]** — A phase with fewer than 5 blocks is likely under-scoped or could be a single block; more than 12 blocks is too large to track and should be split.
2. **All exit criteria are measurable** — Each exit criterion must be verifiable: it references a file path, a grep pattern, a test result, or a command output. Criteria containing only vague language ("the system works," "the feature is done") are rejected.
3. **Tier distribution includes at least one M or L block** — A phase composed entirely of S-tier blocks either underestimates complexity or contains no implementation work. At least one M or L block must be present.
4. **No single block touches more than 6 files** — If a block's manifest lists more than 6 files across read/modify/create, it must be split before the phase is accepted.
5. **At least 20% of blocks have a test gate** — A gate that runs `pytest` or any test command. Phases without test gates produce untested code. Minimum: ceil(block_count * 0.2) blocks with a test gate.
6. **No circular dependencies** — The dependency graph must be a DAG. If block-062 depends on block-063 and block-063 depends on block-062, the phase is rejected until the cycle is resolved.
7. **Each block has a single, clearly stated responsibility** — The block title and purpose must describe one thing. Titles containing "and" are a warning sign; titles containing "and" where both sides are distinct deliverables are a rejection criterion.
8. **Phase has a defined user-visible outcome** — The phase BRIEF must contain a sentence of the form "After this phase, a user/developer can [do/observe X]." The outcome must be concrete and observable, not internal ("refactoring is complete" does not count; "the CLI accepts `--dry-run` without crashing" does).
9. **All listed dependency files exist on disk** — Every file listed in `dependencies:` of each block manifest must already exist or be created by an earlier block in the same phase. Forward references to files outside the phase are flagged.
10. **Estimated duration is plausible given tier mix** — S blocks = 0.5 day each; M blocks = 1 day each; L blocks = 2 days each. If sum of estimates exceeds `estimated_duration_days * 1.5`, the phase estimate is flagged for revision.

**Rubric scoring:**
- 0–5 criteria satisfied: REJECT — do not begin phase; revise and re-check.
- 6–7 criteria satisfied: CONDITIONAL — document which criteria failed and why; proceed only with explicit owner sign-off.
- 8–10 criteria satisfied: ACCEPT — phase may proceed.

---

## 2. Dependencies

None. This is the foundation block for Phase 8.

---

## 3. Files

**Read:**
- `commands/phase-start.md` — to understand current step structure before adding rubric invocation step.

**Modify:**
- `commands/phase-start.md` — add the following step after the existing "generate phase draft" step:
  > **Step: Run Phase Quality Rubric**
  > Before accepting the generated phase, evaluate it against `protocols/phase-quality-rubric.md`.
  > Score the phase against all 10 criteria. Record the score and any failures in a comment block at the top of the phase file under `## Rubric Check`. Do not begin block work until the phase scores ≥8/10 or owner sign-off is on record.

**Create:**
- `protocols/phase-quality-rubric.md` — the full rubric document with all 10 criteria, scoring table, and usage instructions.

---

## 4. Validation

- `protocols/phase-quality-rubric.md` exists on disk.
- File contains at least 10 numbered criteria (spec calls for ≥8; 10 are provided for safety margin).
- `commands/phase-start.md` contains the text "phase-quality-rubric" (case-insensitive).
- Each criterion in the rubric is verifiable: it can be checked by reading the phase file or running a command.

---

## 5. Gates

| Gate | Type | Check |
|---|---|---|
| `rubric-file-exists` | file-changed | `protocols/phase-quality-rubric.md` modified/created |
| `phase-start-updated` | file-changed | `commands/phase-start.md` modified |
| `rubric-has-eight-criteria` | content | file contains ≥8 lines matching `^[0-9]+\.` |

---

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Rubric criteria are too strict and reject Phase 8 itself retroactively | Low | Medium | Rubric applies only to phases generated after Phase 8 completes |
| `commands/phase-start.md` uses a different step format than expected | Low | Low | Read the file before modifying; match existing formatting style |
| 10 criteria is too many and creates friction | Low | Low | Scoring table includes a CONDITIONAL band (6–7) for pragmatic acceptance |

---

## 7. Out of scope

- Automating the rubric check as a CLI command or script.
- Applying the rubric retroactively to phases 1–7.
- Defining rubric criteria for block manifests (that is block-064's responsibility).
- Modifying any file other than `commands/phase-start.md` and the new protocol file.
