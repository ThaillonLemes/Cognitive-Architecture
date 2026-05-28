---
id: block-065
tier: M
kind: implementation
phase: phase-8
scope: phase-bound
status: planned
dependencies:
  - block-064
files:
  read:
    - sdk/return_validator.py
    - sdk/tests/test_return_validator.py
  modify:
    - sdk/return_validator.py
    - sdk/tests/test_return_validator.py
  create:
    - protocols/retrospective-rubric.md
gates:
  - name: rubric-protocol-exists
    type: file-changed
    paths: [protocols/retrospective-rubric.md]
  - name: validator-updated
    type: file-changed
    paths: [sdk/return_validator.py]
  - name: tests-pass
    cmd: python -m pytest sdk/tests/test_return_validator.py -q
    expect: "exit 0"
  - name: validate-rubric-function-exists
    cmd: grep -q "def validate_rubric" sdk/return_validator.py
    expect: "exit 0"
created_at: 2026-05-23
---

# Block 065 — Retrospective Rubric Semantic

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

---

## 1. Purpose

Create `protocols/retrospective-rubric.md` defining 5 semantic quality criteria for block retrospectives, then implement those criteria as automated checks in `sdk/return_validator.py`. Add at least 5 tests to `sdk/tests/test_return_validator.py` to cover the new function.

Currently retrospectives are checked for presence only: did the block produce a retro? This block adds a second tier of validation — was the retro useful? A retro that says "everything went fine" contributes nothing. A retro that explains what failed, what was fixed, and what to do differently next time is a learning asset.

**Target file to create:** `protocols/retrospective-rubric.md`

**Target file to modify:** `sdk/return_validator.py`

**Target file to modify:** `sdk/tests/test_return_validator.py`

---

### Protocol: `protocols/retrospective-rubric.md`

The protocol file must define exactly 5 semantic criteria. Each criterion must be expressed in two forms: (a) a human-readable description of what is required, and (b) a detectable text pattern or structural heuristic that the validator can check.

**Criterion 1 — Deviation Acknowledged**
The retrospective must mention at least one thing that went differently than planned. Acceptable forms include: "I expected X but found Y", "the original plan was X, but I had to do Y", "this took longer than expected because", "the gate failed because". A retro that contains only affirmations ("all steps went smoothly", "completed as planned") fails this criterion.
Detectable pattern: presence of any of the phrases ["differently", "unexpected", "had to", "failed", "longer than", "instead", "changed approach", "pivot"].

**Criterion 2 — Gate Results Referenced**
The retrospective must reference at least one gate result explicitly. It must name a gate (by the gate's `name:` field, or by an action like "grep", "pytest", "file-changed") and state whether it passed or failed. Vague statements ("all gates passed") do not satisfy this criterion — at least one gate must be named.
Detectable pattern: presence of at least one gate-like term ["gate:", "grep", "pytest", "passed", "failed", "exit 0", "exit 1", "file-changed"].

**Criterion 3 — Gate Failure Explained (conditional)**
If any gate is described as having failed (the retro contains "failed" or "exit 1" adjacent to a gate reference), the retro must also contain an explanation of what was done to fix it. A failure mentioned without a resolution is incomplete.
Detectable pattern: if "failed" or "exit 1" appears in the retro, then "fixed", "resolved", "corrected", "adjusted", or "changed" must also appear.

**Criterion 4 — Lesson Captured**
The retrospective must contain at least one "next time" lesson — something the implementer would do differently. Acceptable forms: "next time", "in future", "for the next block", "lesson:", "going forward". A retro without a lesson is an observation log, not a retrospective.
Detectable pattern: presence of any of the phrases ["next time", "in future", "for the next", "lesson:", "going forward", "should have", "would do differently"].

**Criterion 5 — Token Counts Are Real**
The retrospective (or its associated block data) must include `tok_in` and `tok_out` fields with non-zero integer values. A value of 0 indicates the field was not populated, which undermines cost tracking.
Detectable pattern: `tok_in` field is present and value > 0; `tok_out` field is present and value > 0. If fields are absent, this criterion fails.

**Scoring:**
- 5/5 criteria satisfied: HIGH QUALITY — retro is complete and useful.
- 3–4/5 criteria satisfied: ACCEPTABLE — warnings issued for missing criteria.
- 0–2/5 criteria satisfied: LOW QUALITY — warnings issued for each missing criterion; a summary warning is added.

**Important:** All rubric failures are warnings, not errors. A rubric failure does not prevent a block from being closed or a gate from passing. The purpose of the rubric is to surface quality gaps, not to block progress.

---

### SDK changes: `sdk/return_validator.py`

Add a new function `validate_rubric(retro_text: str, tok_in: int = 0, tok_out: int = 0) -> list[str]` that:

1. Accepts a retrospective as a string and (optionally) tok_in/tok_out as integers.
2. Checks each of the 5 criteria using the detectable patterns defined above.
3. Returns a list of warning strings. An empty list means all criteria passed. Each warning string should be prefixed with `"[RUBRIC WARNING]"` and name the specific criterion that failed.
4. The function must NOT raise exceptions for missing or empty input — return a single warning instead: `["[RUBRIC WARNING] Retrospective text is empty or missing."]`.
5. The function must be integrated into the existing `ValidationResult` flow: if the block data includes a retrospective field, `validate_rubric` is called automatically and its warnings are appended to `ValidationResult.warnings`.

---

### Tests: `sdk/tests/test_return_validator.py`

Add at least 5 new test functions, each testing a specific rubric criterion or edge case:

1. `test_rubric_deviation_acknowledged_present` — retro with "had to change approach" passes criterion 1.
2. `test_rubric_deviation_acknowledged_absent` — retro with only "completed as planned" fails criterion 1 with a warning.
3. `test_rubric_gate_results_referenced` — retro mentioning "pytest passed" satisfies criterion 2.
4. `test_rubric_gate_failure_without_resolution` — retro mentioning "gate failed" without "fixed" or "resolved" fails criterion 3.
5. `test_rubric_lesson_captured` — retro containing "next time I will" satisfies criterion 4.
6. `test_rubric_token_counts_zero` — tok_in=0, tok_out=0 fails criterion 5 with a warning.
7. `test_rubric_empty_retro` — empty string returns the "empty or missing" warning.
8. `test_rubric_all_criteria_pass` — a well-formed retro returns an empty warning list.

(Minimum 5; 8 are specified here for robustness. Implement as many as time allows, with 5 as the floor.)

---

## 2. Dependencies

- **block-064** — Block Complexity Estimator must exist so the rubric can reference tier-based expectations (e.g., M/L blocks are expected to have richer retros) without forward references.

---

## 3. Files

**Read:**
- `sdk/return_validator.py` — to understand existing `ValidationResult` structure and validation patterns before adding `validate_rubric`.
- `sdk/tests/test_return_validator.py` — to understand existing test patterns, fixtures, and naming conventions.

**Modify:**
- `sdk/return_validator.py` — add `validate_rubric` function and integrate it into `ValidationResult` flow.
- `sdk/tests/test_return_validator.py` — add ≥5 new test functions covering rubric criteria.

**Create:**
- `protocols/retrospective-rubric.md` — the full rubric protocol with 5 criteria, detectable patterns, and scoring table.

---

## 4. Validation

- `protocols/retrospective-rubric.md` exists with exactly 5 numbered criteria.
- `sdk/return_validator.py` contains `def validate_rubric`.
- `python -m pytest sdk/tests/test_return_validator.py -q` passes with no failures.
- At least 5 new test functions exist in the test file (check by counting `def test_rubric_` prefixed functions).
- No existing tests in `test_return_validator.py` are broken by the changes.

---

## 5. Gates

| Gate | Type | Check |
|---|---|---|
| `rubric-protocol-exists` | file-changed | `protocols/retrospective-rubric.md` modified/created |
| `validator-updated` | file-changed | `sdk/return_validator.py` modified |
| `tests-pass` | cmd | `python -m pytest sdk/tests/test_return_validator.py -q` exits 0 |
| `validate-rubric-function-exists` | content | `sdk/return_validator.py` contains `def validate_rubric` |

---

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `sdk/return_validator.py` has a different structure than expected | Medium | Medium | Read the file first (SPARC phase A); adapt function signature to match existing patterns |
| New tests break existing tests via import side effects | Low | High | Run full test suite before and after changes; use pytest -q to catch regressions |
| Detectable patterns for criteria 1 and 4 produce false positives | Medium | Low | Patterns are warnings only; false positives cause noise but not failures |
| `tok_in`/`tok_out` field names differ in actual block data schema | Medium | Medium | Read existing block data samples before implementing criterion 5 |

---

## 7. Out of scope

- Making rubric failures hard errors that block gate passage.
- Implementing NLP-based semantic analysis (pattern matching is sufficient).
- Applying the rubric check to retrospectives from phases 1–7.
- Modifying any file other than the three listed above.
