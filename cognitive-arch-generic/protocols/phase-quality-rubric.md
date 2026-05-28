# Phase Quality Rubric

BRIEF: 10 measurable criteria to evaluate a generated phase before work begins. A phase that scores below 8/10 must be revised. No block work starts until the rubric is passed.

**When to run:** After generating a phase draft (Step 4 of `commands/phase-start.md`) and before confirming the phase to the user.

**How to run:** Score the phase against each criterion below. Record results in the phase file under a `## Rubric Check` comment block. Do not begin block work until score ≥ 8/10 or owner sign-off is on record.

---

## Criteria

### 1. Block count in range [5, 12]

A phase with fewer than 5 blocks is under-scoped (probably a single block or two). A phase with more than 12 blocks is too large to track coherently and must be split into two phases.

**Check:** Count rows in the phase's `## 8. Block Index` table. Must be ≥ 5 and ≤ 12.

---

### 2. All exit criteria are measurable

Each exit criterion in `## 7. Exit Criteria` must be verifiable by reading a file, running a command, or inspecting output. Criteria that rely solely on vague language fail this check.

**Failing examples:** "the system works correctly", "feature is complete", "code is clean."

**Passing examples:** "`pytest sdk/tests/ -q` exits 0", "`protocols/phase-quality-rubric.md` exists with ≥10 criteria", "`audit.sh` exits 0."

**Check:** Read each exit criterion. If any criterion has no checkable artifact or command, FAIL.

---

### 3. Tier distribution includes at least one M or L block

A phase composed entirely of S-tier blocks either underestimates complexity or contains no meaningful implementation. At least one M or L block must be present.

**Check:** Scan the Block Index table tier column. At least one row must be `M` or `L`.

---

### 4. No single block touches more than 6 files

If a block's manifest lists more than 6 entries across `files.read + files.modify + files.create`, it must be split before the phase is accepted.

**Check:** For each block manifest already generated (if any), count total file entries. Flag any block exceeding 6.

**Note:** If manifests are not yet written, apply this check when each manifest is first drafted.

---

### 5. At least 20% of blocks have a test gate

A gate is a "test gate" if its `cmd` runs `pytest`, a test script, or any automated test suite. Phases without test gates produce untested code.

**Formula:** minimum test-gate blocks = ⌈block_count × 0.2⌉

**Check:** Count blocks with a gate whose `cmd` contains `pytest` or equivalent. Must meet or exceed formula result.

---

### 6. No circular dependencies

The block dependency graph must be a DAG (directed acyclic graph). Any cycle — block A depends on block B which depends on block A — is a hard failure.

**Check:** Trace the dependency chain for each block. If any cycle exists, REJECT.

---

### 7. Each block has a single, clearly stated responsibility

A block's title and Purpose section must describe exactly one deliverable. Titles containing "and" where both sides are distinct deliverables are a rejection signal.

**Failing examples:** "Add auth module and write tests and update docs" (three deliverables).

**Passing examples:** "Add JWT validation middleware", "Write return_validator tests."

**Check:** Read each block's Purpose. If more than one distinct deliverable is present, flag for split.

---

### 8. Phase has a defined user-visible outcome

The phase BRIEF must contain a statement of the form "After this phase, a user/developer can [do/observe X]." The outcome must be concrete and externally observable.

**Failing examples:** "Refactoring is complete", "Internal architecture improved."

**Passing examples:** "After this phase, running `audit.sh` reports all 8 checks", "After this phase, `--parallel N` flag dispatches blocks concurrently."

**Check:** Read the phase BRIEF. Locate the user-visible outcome sentence. If absent: FAIL.

---

### 9. All listed dependency files exist or are created within the phase

Every file listed as a dependency in block manifests must either: (a) already exist on disk, or (b) be created by an earlier block in the same phase's execution order.

**Check:** For each block's `dependencies:` list, verify each item is either on disk or produced by a block with a lower sequence number in the same phase.

---

### 10. Estimated duration is plausible given tier mix

Apply the standard tier estimates: S = 0.5 day, M = 1 day, L = 2 days. Sum all blocks. If the sum exceeds `estimated_duration_days × 1.5`, the phase estimate is flagged for revision.

**Formula:** computed_days = (count_S × 0.5) + (count_M × 1.0) + (count_L × 2.0). Flag if computed_days > estimated_duration_days × 1.5.

**Check:** Run the formula. Emit WARN if exceeded; do not hard-fail (schedule estimates are advisory).

---

## Scoring Table

| Score | Band | Action |
|-------|------|--------|
| 8–10 | **ACCEPT** | Phase may proceed. Record score in `## Rubric Check`. |
| 6–7 | **CONDITIONAL** | Document which criteria failed and why. Proceed only with explicit owner sign-off recorded in the phase file. |
| 0–5 | **REJECT** | Do not begin phase. Revise and re-run rubric. |

---

## Rubric Check block (paste into phase file)

```
## Rubric Check

Score: X/10  Band: ACCEPT | CONDITIONAL | REJECT
Checked: YYYY-MM-DD

| # | Criterion | Result | Note |
|---|-----------|--------|------|
| 1 | Block count [5,12] | PASS/FAIL | count=N |
| 2 | Measurable exit criteria | PASS/FAIL | |
| 3 | ≥1 M or L block | PASS/FAIL | |
| 4 | ≤6 files per block | PASS/FAIL | |
| 5 | ≥20% test gates | PASS/FAIL | N/total |
| 6 | No circular deps | PASS/FAIL | |
| 7 | Single responsibility | PASS/FAIL | |
| 8 | User-visible outcome | PASS/FAIL | |
| 9 | Dep files exist | PASS/FAIL | |
| 10 | Duration plausible | PASS/WARN | computed=Nd, declared=Nd |

Owner sign-off (CONDITIONAL only): ___
```

---

## Out of scope

- Automating this check as a CLI script (that is a future block).
- Applying retroactively to phases 1–7.
- Block-level quality rubric (see `protocols/block-complexity-estimator.md`).

End of phase-quality-rubric.md.
