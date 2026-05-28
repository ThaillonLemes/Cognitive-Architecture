---
id: block-063
tier: S
kind: protocol
phase: phase-8
scope: phase-bound
status: planned
dependencies:
  - block-061
files:
  read:
    - commands/block-start.md
  modify:
    - commands/block-start.md
  create:
    - protocols/block-execution-sparc.md
gates:
  - name: sparc-file-exists
    type: file-changed
    paths: [protocols/block-execution-sparc.md]
  - name: block-start-references-sparc
    cmd: grep -qi "sparc" commands/block-start.md
    expect: "exit 0"
  - name: sparc-has-five-phases
    cmd: grep -c "^## [SPARC]" protocols/block-execution-sparc.md
    expect: "exit 0 with count >= 5"
created_at: 2026-05-23
---

# Block 063 — SPARC Intra-Block Protocol

- **Tier:** S
- **Kind:** protocol
- **Status:** planned

---

## 1. Purpose

Create `protocols/block-execution-sparc.md`, a five-phase execution protocol for use within each block. Without an intra-block protocol, implementation proceeds ad hoc: the AI reads the manifest once, writes files, and declares the block done — often without verifying architectural consistency, testing incrementally, or capturing lessons. The SPARC protocol enforces a structured sequence that reduces scope creep, catches architecture violations early, and ensures every block ends with a meaningful retrospective.

Also update `commands/block-start.md` to reference this protocol explicitly.

**Target file to create:** `protocols/block-execution-sparc.md`

**The five SPARC phases must be defined as follows:**

---

### S — Specification

**Entry condition:** Block manifest is open and unread.

**Actions:**
1. Re-read the full block manifest, including all sections (purpose, dependencies, files, gates, risks).
2. Confirm scope: identify exactly which files will be read, modified, and created. Verify the list matches the manifest's `files:` section.
3. Write a 3-line plan in a scratch comment or internal note:
   - Line 1: What is being created or changed.
   - Line 2: What constraint or design rule must be respected.
   - Line 3: How success will be verified (which gate or test).
4. If the manifest's files or gates are ambiguous, resolve ambiguity before continuing. Do not proceed to Pseudocode with unresolved scope questions.

**Exit condition:** Scope is confirmed, 3-line plan is written, no unresolved ambiguities.

---

### P — Pseudocode

**Entry condition:** Specification phase complete.

**Actions:**
1. For each file to be created or modified, write the intended logic as comments or pseudocode before writing any real code.
2. For protocol files (.md), sketch the section headings and key points in bullet form before writing prose.
3. For code files (.py, etc.), write function signatures and docstrings with inline pseudocode steps (`# step 1: ...`, `# step 2: ...`).
4. Do not write implementation code in this phase. The output of Pseudocode is a set of annotated stubs.

**Exit condition:** Every file to be created or modified has a pseudocode or outline stub.

---

### A — Architecture

**Entry condition:** Pseudocode phase complete.

**Actions:**
1. Read the relevant `design/` files and any existing modules or protocols referenced by the block.
2. Verify that the planned approach (from Pseudocode) is consistent with the documented architecture.
3. Check for conflicts: does the new file introduce naming conventions that differ from existing files? Does the new function duplicate an existing function? Does the new protocol contradict an existing protocol?
4. If a conflict is found, document it explicitly and either (a) adjust the approach to align with existing architecture, or (b) flag it as a deliberate deviation in the block retrospective.
5. Do not proceed to Refinement if an unresolved architecture conflict exists.

**Exit condition:** Approach verified against architecture; conflicts resolved or explicitly deferred.

---

### R — Refinement

**Entry condition:** Architecture phase complete.

**Actions:**
1. Implement the planned changes: write the actual file content, replacing pseudocode stubs with real content.
2. After each file is written, re-read it briefly to verify it matches the intent from Specification.
3. Run applicable gates incrementally — do not wait until all files are written. If a gate fails early, fix it before continuing.
4. Iterate: write → check → fix → write → check until all files are complete and consistent.

**Exit condition:** All files written; no known gate failures remaining.

---

### C — Completion

**Entry condition:** Refinement phase complete; all files written.

**Actions:**
1. Run all gates defined in the block manifest. Record each result (pass/fail).
2. If any gate fails, return to Refinement to fix the issue. Do not write the retrospective until all gates pass.
3. Write the block retrospective. The retrospective must satisfy the criteria in `protocols/retrospective-rubric.md` (Phase 8, block-065).
4. Update the block manifest `status:` field from `planned` to `done`.
5. Record `tok_in` and `tok_out` with actual values.

**Exit condition:** All gates pass; retrospective written; block status set to `done`.

---

**Applicability:**

| Block Tier | SPARC Status |
|---|---|
| L (Large) | Mandatory |
| M (Medium) | Mandatory |
| S (Small) | Recommended |

For S-tier blocks, the implementer may compress S+P into a single mental step and A+R into a single pass, but must not skip gate verification (R→C transition) or the retrospective (C phase).

---

## 2. Dependencies

- **block-061** — Phase Quality Rubric must exist first, as the SPARC protocol references the broader quality framework.

---

## 3. Files

**Read:**
- `commands/block-start.md` — to understand existing step structure before adding SPARC reference.

**Modify:**
- `commands/block-start.md` — add the following section after the "open manifest" step:
  > **Protocol: SPARC Intra-Block Execution**
  > For M and L tier blocks, follow `protocols/block-execution-sparc.md` (SPARC) throughout this block.
  > S = Specification, P = Pseudocode, A = Architecture, R = Refinement, C = Completion.
  > For S tier blocks, SPARC is recommended. At minimum, always complete phase C (run gates + write retrospective).

**Create:**
- `protocols/block-execution-sparc.md` — the full SPARC protocol with all 5 phases, entry/exit conditions, tier applicability table.

---

## 4. Validation

- `protocols/block-execution-sparc.md` exists on disk.
- File defines all 5 phases (S, P, A, R, C) with entry conditions and actions.
- Each phase section header is clearly labeled (e.g., `## S — Specification`).
- `commands/block-start.md` contains the word "SPARC" (case-insensitive).
- Tier applicability table is present.

---

## 5. Gates

| Gate | Type | Check |
|---|---|---|
| `sparc-file-exists` | file-changed | `protocols/block-execution-sparc.md` modified/created |
| `block-start-references-sparc` | content | `commands/block-start.md` contains "sparc" |
| `sparc-has-five-phases` | content | file contains ≥5 lines matching `^## [SPARC]` |

---

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| SPARC overhead makes S-tier blocks feel bureaucratic | Low | Low | SPARC is recommended, not mandatory, for S blocks; phases can be compressed |
| Architecture phase (A) reveals design gaps that block progress | Medium | Medium | Explicitly allowed to defer deviations to retrospective rather than blocking |
| `commands/block-start.md` format differs from expected | Low | Low | Read file before modifying; match existing section style |

---

## 7. Out of scope

- Automating SPARC phase transitions as a script or workflow engine.
- Applying SPARC retroactively to closed blocks.
- Modifying `commands/block-close.md` (that is block-066's responsibility).
- Defining the retrospective quality criteria (that is block-065's responsibility).
