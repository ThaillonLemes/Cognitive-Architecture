---
id: block-064
tier: S
kind: protocol
phase: phase-8
scope: phase-bound
status: planned
dependencies:
  - block-063
files:
  create:
    - protocols/block-complexity-estimator.md
gates:
  - name: estimator-file-exists
    type: file-changed
    paths: [protocols/block-complexity-estimator.md]
  - name: estimator-has-three-tiers
    cmd: grep -c "^## Tier [SML]" protocols/block-complexity-estimator.md
    expect: "exit 0 with count >= 3"
  - name: estimator-has-split-rule
    cmd: grep -qi "split" protocols/block-complexity-estimator.md
    expect: "exit 0"
created_at: 2026-05-23
---

# Block 064 — Block Complexity Estimator

- **Tier:** S
- **Kind:** protocol
- **Status:** planned

---

## 1. Purpose

Create `protocols/block-complexity-estimator.md`, a heuristic decision tree for assigning S/M/L tier to a block before writing its manifest. Without an estimator, tier assignment is a guess. Guessing leads to S-tier blocks that take a full day and L-tier blocks that finish in an hour — both of which distort project tracking and make phase duration estimates unreliable.

The estimator answers: "Given what I know about what this block will do, what tier should I assign?"

**Target file to create:** `protocols/block-complexity-estimator.md`

**The protocol must define three tiers with at least 3 criteria each:**

---

### Tier S — Small

Assign S when ALL of the following are true:

1. **File count:** The block creates or modifies a single file, or modifies an existing file with additions only (no structural rewrites). Maximum 2 files total across read/modify/create.
2. **No tests required:** The block does not produce or modify any test file, and no gate runs `pytest` or equivalent.
3. **No SDK or executable code:** All output files are documentation (.md), configuration, or protocol files. No `.py`, `.js`, `.ts`, or other code files are created or modified.
4. **Estimated effort:** The implementer judges the work can be completed in under 2 hours with no research required.
5. **No cross-module impact:** The block's changes are contained within one functional area (e.g., one command, one protocol). No other existing block or protocol needs to change as a consequence.

**Typical examples:** Writing a new protocol file, adding a step to a command file, creating a manifest for a well-understood task.

---

### Tier M — Medium

Assign M when at least 3 of the following are true (and S criteria are NOT all met):

1. **File count:** The block touches 2–5 files across read/modify/create. At least one file is created new.
2. **Tests required:** At least one gate runs a test command (`pytest`, `go test`, etc.), or the block explicitly creates a test file.
3. **Mixed output types:** The block produces both protocol/documentation files (.md) and executable code files (.py, .js, etc.).
4. **Estimated effort:** The implementer judges the work requires 2–6 hours, including research into existing patterns or architecture.
5. **Moderate cross-module impact:** One or two other files outside the block's primary scope need minor updates (e.g., a command file adds a reference to a new protocol).

**Typical examples:** Adding a new validator function with tests, creating a protocol and updating a command to reference it, implementing a feature with a corresponding test suite.

---

### Tier L — Large

Assign L when ANY of the following are true:

1. **File count:** The block touches 6 or more files across read/modify/create.
2. **Tests + code + protocol:** The block produces all three output types: test files, executable code, and protocol/documentation.
3. **Cross-module impact:** Three or more existing files outside the block's primary scope require modification as a consequence of this block.
4. **Estimated effort:** The implementer judges the work requires 6–12 hours, including non-trivial research, design decisions, or iterative debugging.
5. **Architectural change:** The block introduces a new architectural pattern, changes a shared interface, or modifies a file that multiple other blocks depend on.

**Typical examples:** Implementing a new SDK module with tests, refactoring a core module with downstream effects, introducing a new runtime protocol that changes how existing commands behave.

---

**Decision tree (quick reference):**

```
START
  ├─ All 5 S-criteria met? ─→ YES ─→ Assign S
  └─ NO
      ├─ Any L-criterion met? ─→ YES ─→ Assign L
      └─ NO
          ├─ ≥3 M-criteria met? ─→ YES ─→ Assign M
          └─ NO ─→ Re-examine: you may have missed a criterion. Default to M if uncertain.
```

---

**When to SPLIT a block:**

A block must be split into two blocks with an explicit dependency if ANY of the following are true:

- The block touches more than 8 files total (across all read/modify/create combined). At that scale, two reviewers cannot hold the change in mind simultaneously.
- The estimated effort exceeds 12 hours. Blocks longer than 12 hours are effectively mini-projects and lose the tracking benefits of the block structure.
- The block has two distinct "deliverables" that could each satisfy a user-visible outcome independently. If deliverable A could be shipped without deliverable B, they belong in separate blocks.
- The block would change two or more shared protocols or interfaces simultaneously. Shared changes compound risk; isolate them.

**How to split:** Identify the minimal first deliverable (call it block-N). The remaining work becomes block-N+1 with `block-N` in its `dependencies:`. Write both manifests before beginning work on either.

---

**Calibration guidance:**

If you find yourself consistently assigning S to blocks that take 4+ hours, your S criteria are being applied too loosely. Revisit and reassign. The tier is an input to phase duration estimation; systematic misassignment makes the estimation tool useless.

---

## 2. Dependencies

- **block-063** — SPARC protocol must exist so the estimator can reference "blocks where SPARC is mandatory (M, L)" without that being a forward reference.

---

## 3. Files

**Create:**
- `protocols/block-complexity-estimator.md` — the full estimator with tier definitions, decision tree, split rules, and calibration guidance.

---

## 4. Validation

- `protocols/block-complexity-estimator.md` exists on disk.
- File defines all three tiers (S, M, L) with at least 3 criteria each.
- File contains a "split a block" section with at least 2 split triggers.
- File contains a decision tree or equivalent quick-reference section.
- No circular references: estimator does not require any file created after block-064 in this phase.

---

## 5. Gates

| Gate | Type | Check |
|---|---|---|
| `estimator-file-exists` | file-changed | `protocols/block-complexity-estimator.md` modified/created |
| `estimator-has-three-tiers` | content | file contains ≥3 lines matching `^## Tier [SML]` |
| `estimator-has-split-rule` | content | file contains the word "split" |

---

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Tier criteria overlap and make assignment ambiguous | Medium | Medium | Decision tree provides explicit precedence order (L overrides M overrides S) |
| Implementer ignores the estimator and assigns by gut feeling | Medium | Low | Block-066 wires the estimator into block-start command; it becomes part of the workflow |
| Split rules are too aggressive and create trivially small blocks | Low | Low | Split triggers have concrete thresholds (8 files, 12 hours) rather than subjective language |

---

## 7. Out of scope

- Automating tier assignment as a script.
- Defining tier criteria for phases (the Phase Quality Rubric covers phases).
- Retroactively reassigning tiers on closed blocks.
- Enforcing split rules via a CI gate.
