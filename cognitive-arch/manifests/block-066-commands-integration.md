---
id: block-066
tier: S
kind: implementation
phase: phase-8
scope: phase-bound
status: planned
dependencies:
  - block-061
  - block-062
  - block-063
  - block-064
  - block-065
files:
  read:
    - commands/block-start.md
    - commands/block-close.md
    - commands/phase-start.md
    - commands/phase-close.md
  modify:
    - commands/block-start.md
    - commands/block-close.md
    - commands/phase-start.md
    - commands/phase-close.md
gates:
  - name: block-start-updated
    type: file-changed
    paths: [commands/block-start.md]
  - name: block-close-updated
    type: file-changed
    paths: [commands/block-close.md]
  - name: phase-start-updated
    type: file-changed
    paths: [commands/phase-start.md]
  - name: phase-close-updated
    type: file-changed
    paths: [commands/phase-close.md]
  - name: block-start-references-sparc
    cmd: grep -qi "block-execution-sparc" commands/block-start.md
    expect: "exit 0"
  - name: block-start-references-estimator
    cmd: grep -qi "block-complexity-estimator" commands/block-start.md
    expect: "exit 0"
  - name: block-close-references-retro-rubric
    cmd: grep -qi "retrospective-rubric" commands/block-close.md
    expect: "exit 0"
  - name: phase-start-references-quality-rubric
    cmd: grep -qi "phase-quality-rubric" commands/phase-start.md
    expect: "exit 0"
  - name: phase-start-references-domain-bridge
    cmd: grep -qi "domain-phase-bridge" commands/phase-start.md
    expect: "exit 0"
  - name: phase-close-references-quality-rubric
    cmd: grep -qi "phase-quality-rubric" commands/phase-close.md
    expect: "exit 0"
created_at: 2026-05-23
---

# Block 066 — Commands Integration

- **Tier:** S
- **Kind:** implementation
- **Status:** planned

---

## 1. Purpose

Update the four primary command files to reference all Phase 8 protocols. Phase 8 introduces five new protocol files, but protocols are only effective if the workflow commands point to them at the right moment. Without this integration block, the protocols exist as documentation but are never invoked in practice.

This block performs purely additive modifications: no existing steps are removed, only new references and protocol invocation steps are added.

**Files to modify and what to add to each:**

---

### `commands/block-start.md`

Add two new protocol references:

**Reference 1 — Block Complexity Estimator (added before the manifest-writing step):**
> **Step: Assign Tier Using Complexity Estimator**
> Before writing or accepting a block manifest, consult `protocols/block-complexity-estimator.md` to assign the correct S/M/L tier. Use the decision tree: check S-criteria first (all 5 must be true); if not S, check L-criteria (any 1 triggers L); otherwise assign M. If the block would touch >8 files or require >12 hours, split it before writing the manifest.

**Reference 2 — SPARC Protocol (added after the manifest is confirmed open):**
> **Step: Apply SPARC Intra-Block Protocol**
> For M and L tier blocks, follow `protocols/block-execution-sparc.md` throughout this block. Work through the five phases in order: S (Specification) → P (Pseudocode) → A (Architecture) → R (Refinement) → C (Completion). For S tier blocks, SPARC is recommended; at minimum, always complete phase C (run all gates and write retrospective before closing).

---

### `commands/block-close.md`

Add one new protocol reference:

**Reference — Retrospective Rubric (added before the "mark block done" step):**
> **Step: Check Retrospective Quality**
> Before marking this block as done, verify the retrospective satisfies `protocols/retrospective-rubric.md`. The rubric has 5 criteria: (1) deviation acknowledged, (2) gate results referenced, (3) gate failures explained if any occurred, (4) at least one lesson captured, (5) tok_in and tok_out are non-zero. Rubric failures are warnings, not blockers — but if 3 or more criteria fail, revise the retrospective before closing. The SDK validator (`validate_rubric` in `sdk/return_validator.py`) checks these criteria automatically if the block data is passed through validation.

---

### `commands/phase-start.md`

Add two new protocol references:

**Reference 1 — Domain→Phase Bridge (added before the "generate phase draft" step):**
> **Step: Run Domain→Phase Bridge**
> Before generating a phase, follow `protocols/domain-phase-bridge.md`. Verify the readiness precondition: `design/02-domain-overview.md` must exist with at least one documented system. Then work through the 7 bridge steps: enumerate systems, identify user-visible features, group into vertical slices, order by dependency, verify observable outcomes, and run the Phase Quality Rubric on the generated phase draft.

**Reference 2 — Phase Quality Rubric (added after the "generate phase draft" step, ensuring it runs after both the domain bridge and the draft):**
> **Step: Score Phase Against Quality Rubric**
> After generating the phase draft, score it against `protocols/phase-quality-rubric.md`. Evaluate all 10 criteria. Record the score in a `## Rubric Check` comment at the top of the phase file. Do not begin block work if the score is below 8/10 unless owner sign-off is explicitly documented. If the score is 6–7/10 (CONDITIONAL band), document which criteria failed and why.

---

### `commands/phase-close.md`

Add one new protocol reference:

**Reference — Phase Quality Rubric for Exit Validation (added before the "mark phase done" step):**
> **Step: Validate Exit Criteria Against Phase Quality Rubric**
> Before marking this phase as complete, re-read the phase file's `## 7. Exit Criteria` section. Verify each criterion is satisfied: file paths exist, grep patterns match, test commands pass. Cross-check against `protocols/phase-quality-rubric.md` criterion 2 (all exit criteria must be measurable and verifiable). If any exit criterion is vague or unverifiable, do not close the phase — revise the criterion or document the gap explicitly.

---

## 2. Dependencies

- **block-061** — `protocols/phase-quality-rubric.md` must exist before `commands/phase-start.md` and `commands/phase-close.md` can reference it.
- **block-062** — `protocols/domain-phase-bridge.md` must exist before `commands/phase-start.md` can reference it.
- **block-063** — `protocols/block-execution-sparc.md` must exist before `commands/block-start.md` can reference it.
- **block-064** — `protocols/block-complexity-estimator.md` must exist before `commands/block-start.md` can reference it.
- **block-065** — `protocols/retrospective-rubric.md` must exist before `commands/block-close.md` can reference it.

---

## 3. Files

**Read:**
- `commands/block-start.md`
- `commands/block-close.md`
- `commands/phase-start.md`
- `commands/phase-close.md`

All four files must be read before modification to preserve existing step structure and match formatting conventions.

**Modify:**
- `commands/block-start.md` — add complexity estimator reference and SPARC reference.
- `commands/block-close.md` — add retrospective rubric reference.
- `commands/phase-start.md` — add domain-phase-bridge reference and phase-quality-rubric reference.
- `commands/phase-close.md` — add phase-quality-rubric exit validation reference.

---

## 4. Validation

- All four command files are modified (file-changed gates pass).
- `commands/block-start.md` contains both "block-execution-sparc" and "block-complexity-estimator".
- `commands/block-close.md` contains "retrospective-rubric".
- `commands/phase-start.md` contains both "phase-quality-rubric" and "domain-phase-bridge".
- `commands/phase-close.md` contains "phase-quality-rubric".
- No existing content is removed from any command file (diff shows only additions).

---

## 5. Gates

| Gate | Type | Check |
|---|---|---|
| `block-start-updated` | file-changed | `commands/block-start.md` modified |
| `block-close-updated` | file-changed | `commands/block-close.md` modified |
| `phase-start-updated` | file-changed | `commands/phase-start.md` modified |
| `phase-close-updated` | file-changed | `commands/phase-close.md` modified |
| `block-start-references-sparc` | content | `commands/block-start.md` contains "block-execution-sparc" |
| `block-start-references-estimator` | content | `commands/block-start.md` contains "block-complexity-estimator" |
| `block-close-references-retro-rubric` | content | `commands/block-close.md` contains "retrospective-rubric" |
| `phase-start-references-quality-rubric` | content | `commands/phase-start.md` contains "phase-quality-rubric" |
| `phase-start-references-domain-bridge` | content | `commands/phase-start.md` contains "domain-phase-bridge" |
| `phase-close-references-quality-rubric` | content | `commands/phase-close.md` contains "phase-quality-rubric" |

---

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| One or more command files use a format incompatible with additive insertion | Low | Medium | Read each file before modifying; match existing heading and step style |
| `commands/phase-start.md` already has a rubric reference from block-061 | Low | Low | Block-061 adds one step; block-066 adds a second step — both are valid; check for duplicates before inserting |
| Gates are too strict and fail due to filename case (sparc vs SPARC) | Low | Low | All grep gates use `-qi` (case-insensitive); this is already accounted for |
| An intermediate block (062–065) was skipped and its protocol file is missing | Low | High | All five blocks are listed as dependencies; do not begin block-066 until all five are closed |

---

## 7. Out of scope

- Creating new command files.
- Modifying any protocol file (all protocol files are finalized by block-065).
- Modifying `sdk/return_validator.py` or any test files.
- Adding Phase 8 protocol references to command files outside the four listed above.
- Retroactively adding protocol references to command files used in phases 1–7 execution history.
