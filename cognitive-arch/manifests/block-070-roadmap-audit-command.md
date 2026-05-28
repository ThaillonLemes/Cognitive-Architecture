---
id: block-070
tier: S
kind: protocol
phase: phase-9
scope: phase-bound
status: planned
dependencies:
  - block-068
  - block-069
files:
  read:
    - protocols/domain-coverage-matrix.md
  modify: []
  create:
    - commands/roadmap-audit.md
gates:
  - name: roadmap-audit-command-exists
    type: file-changed
    paths: [commands/roadmap-audit.md]
created_at: 2026-05-23
---

# block-070 — Roadmap Audit Command

## Purpose

The coverage-check command (block-068) answers "what gaps exist right now?" The readiness gate (block-069) answers "is the project ready to generate new phases?" But neither answers the higher-order question: "is the project's roadmap healthy as a whole?"

A project can have zero coverage gaps and still have a structurally unsound roadmap — phases that depend on each other in a cycle, user journeys with no phase coverage, or perpetual systems that lack a Track. These macro health issues are invisible to point-in-time coverage checks.

This block delivers `commands/roadmap-audit.md` — a command that audits four dimensions of macro roadmap health and produces a structured markdown report with explicit OK/WARN/ERROR status for each dimension.

The four audit dimensions are:

1. **Coverage** — are all design/ systems assigned to phases, with no drift or staleness?
2. **Sequencing** — do phase dependencies form a valid DAG (no cycles, correct ordering)?
3. **Completeness** — does every major user journey from PROJECT.md map to at least one phase?
4. **Forever Tracks** — do all systems designated as perpetual have a corresponding Track?

## Dependencies

- **block-068** must be complete. The roadmap-audit command invokes the coverage-check command as its Coverage dimension. The `protocols/domain-coverage-matrix.md` file must exist.
- **block-069** must be complete. The readiness gate is referenced in the audit as a pre-condition check.

## Files

### Read
- `protocols/domain-coverage-matrix.md` — to reference the gap type definitions used in the Coverage dimension.

### Modify
None.

### Create

**`commands/roadmap-audit.md`**

Must contain:

**Command name**: `roadmap-audit`

**Trigger phrase**: "Run roadmap audit" or "Audit the roadmap."

**Purpose**: Evaluate macro roadmap health across four dimensions. Output a markdown report. Do not modify any project files.

**Pre-conditions**:
- ROADMAP.md must exist. If it does not, report: "ERROR: ROADMAP.md not found. Run roadmap-generation protocol first." Stop.
- phases/ directory must contain at least one phase file.
- PROJECT.md must exist.

---

**Dimension 1 — Coverage**

Step 1.1: Run the coverage-check command (defined in `commands/coverage-check.md`). Collect the summary counts: OK, UNCOVERED, DRIFT, STALE, UNKNOWN.

Step 1.2: Determine status:
- OK if: UNCOVERED = 0, DRIFT = 0, STALE = 0.
- WARN if: STALE > 0 or UNKNOWN > 0, but UNCOVERED = 0 and DRIFT = 0.
- ERROR if: UNCOVERED > 0 or DRIFT > 0.

Step 1.3: Output Coverage section:
```
## Dimension 1 — Coverage [OK|WARN|ERROR]

| Metric | Count |
|--------|-------|
| Systems covered (OK) | N |
| UNCOVERED | N |
| DRIFT | N |
| STALE | N |
| UNKNOWN | N |

[If WARN or ERROR: list each gap with system name and gap type.]
```

---

**Dimension 2 — Sequencing**

Step 2.1: Build the phase dependency graph. For each phase file, extract the `prev_phase` frontmatter field and any `dependencies` listed in the Dependencies section. Build a directed graph: phase → list of phases it depends on.

Step 2.2: Cycle detection. Perform a depth-first traversal of the graph. If any cycle is found (phase A depends on phase B which depends on phase A, directly or transitively), record each cycle as an ERROR.

Step 2.3: Ordering validation. For each phase in the phases/ list, verify that every phase it depends on has a lower phase number (or an earlier created_at date if phase IDs are non-numeric). Phases out of order are WARN (not ERROR, because manual reordering may be intentional).

Step 2.4: Determine status:
- OK if: no cycles and no out-of-order phases.
- WARN if: no cycles but one or more out-of-order phases detected.
- ERROR if: any cycle detected.

Step 2.5: Output Sequencing section:
```
## Dimension 2 — Sequencing [OK|WARN|ERROR]

Phase dependency graph: [N] phases, [N] dependency edges.

[If cycles found:]
ERRORS — Cycles detected:
- [phase-X → phase-Y → phase-X]

[If out-of-order found:]
WARNINGS — Out-of-order dependencies:
- phase-N depends on phase-M (M > N)

[If OK:]
No cycles. All phase dependencies are correctly ordered.
```

---

**Dimension 3 — Completeness**

Step 3.1: Extract user journeys from PROJECT.md. Look for a section named "User Journeys", "Key Flows", "Core Use Cases", or a bullet list under "target_users" that describes what users do. If no such section exists, note: "No user journeys section found in PROJECT.md" and mark this dimension UNKNOWN.

Step 3.2: For each identified user journey, search all phase files' Purpose and Goals sections for coverage of that journey. A journey is covered if at least one phase explicitly mentions implementing, enabling, or supporting it.

Step 3.3: Determine status:
- UNKNOWN if: no user journeys section found in PROJECT.md.
- OK if: every journey is covered by at least one phase.
- WARN if: 1–2 journeys have no phase coverage.
- ERROR if: 3 or more journeys have no phase coverage.

Step 3.4: Output Completeness section:
```
## Dimension 3 — Completeness [OK|WARN|ERROR|UNKNOWN]

User journeys found in PROJECT.md: [N]
Covered by at least one phase: [N]
Uncovered: [N]

[List uncovered journeys, if any.]
```

---

**Dimension 4 — Forever Tracks**

Step 4.1: Identify perpetual systems. Read all design/ files. A system is perpetual if its frontmatter contains `perpetual: true`, or if its description contains the phrases "performance-sensitive", "scalability-sensitive", "core game-feel", or "perpetual improvement."

Step 4.2: For each perpetual system, check whether a Track file exists in tracks/. A Track file is any .md file in tracks/ (except README.md, PRIORITY.md, and _placeholder.md) that references the system by name or ID in its frontmatter.

Step 4.3: Determine status:
- OK if: every perpetual system has a corresponding Track file.
- WARN if: some perpetual systems have no Track file (Tracks not yet created).
- ERROR if: no Tracks directory exists but perpetual systems are documented.
- UNKNOWN if: no systems are marked as perpetual (Track system not yet in use).

Step 4.4: Output Forever Tracks section:
```
## Dimension 4 — Forever Tracks [OK|WARN|ERROR|UNKNOWN]

Perpetual systems identified: [N]
Systems with a Track: [N]
Systems without a Track: [N]

[List systems without Tracks, if any.]
```

---

**Final Report**

After all four dimensions, output a summary:

```
---

## Audit Summary — [DATE]

| Dimension | Status |
|-----------|--------|
| Coverage | [OK|WARN|ERROR] |
| Sequencing | [OK|WARN|ERROR] |
| Completeness | [OK|WARN|ERROR|UNKNOWN] |
| Forever Tracks | [OK|WARN|ERROR|UNKNOWN] |

Overall: [PASS if all OK or UNKNOWN | WARN if any WARN | FAIL if any ERROR]

[If FAIL or WARN: "Run `commands/roadmap-refresh.md` to generate proposals for addressing the issues above."]
[If PASS: "Roadmap is healthy. No immediate action required."]
```

## Validation

- `commands/roadmap-audit.md` exists and defines all four audit dimensions.
- Each dimension has explicit OK/WARN/ERROR status definitions.
- The command references `commands/coverage-check.md` in Dimension 1.
- The Final Report section exists and defines an overall PASS/WARN/FAIL determination.
- The command does not modify any project files.

## Gates

| Gate | Type | Path(s) | Condition |
|------|------|---------|-----------|
| roadmap-audit-command-exists | file-changed | commands/roadmap-audit.md | File must exist and define all 4 dimensions |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Cycle detection algorithm produces false positives on valid diamond dependencies | Low | Medium | Diamond dependencies (A→B, A→C, B→D, C→D) are valid DAG patterns; the algorithm checks for true back-edges only |
| User journey extraction fails on non-standard PROJECT.md structures | Medium | Low | Step 3.1 includes multiple heading aliases; if none are found, dimension is UNKNOWN (not ERROR) |
| Perpetual system detection misses systems described informally | Medium | Low | Detection is advisory; UNKNOWN status is not a failure and prompts human review rather than blocking action |

## Out of Scope

- Automated fixing of any issue found by the audit. The audit is read-only. Fixes are proposed by roadmap-refresh (block-071).
- Auditing Track Block execution quality. The audit checks whether Tracks exist; it does not evaluate whether Track Blocks are well-written.
- Scheduled or automated audit runs. The audit is triggered manually.
