---
id: block-071
tier: S
kind: protocol
phase: phase-9
scope: phase-bound
status: planned
dependencies:
  - block-070
files:
  read:
    - commands/roadmap-audit.md
  modify: []
  create:
    - commands/roadmap-refresh.md
gates:
  - name: roadmap-refresh-command-exists
    type: file-changed
    paths: [commands/roadmap-refresh.md]
  - name: proposal-keyword-present
    type: cmd
    cmd: "grep -q \"PROPOSAL\" commands/roadmap-refresh.md"
    expect: exit 0
  - name: human-review-clause-present
    type: cmd
    cmd: "grep -q \"Human must review\" commands/roadmap-refresh.md"
    expect: exit 0
created_at: 2026-05-23
---

# block-071 — Roadmap Refresh Command

## Purpose

Design/ grows. New systems are documented, existing systems are revised, and some planned phases become obsolete. Without a structured process for keeping the roadmap current, the gap between the design space and the execution plan widens silently until a major restructuring is required.

The roadmap-refresh command addresses this by periodically re-evaluating the roadmap against the current state of design/ and producing a set of proposals. The key constraint is that this command is advisory only: it proposes changes, it never applies them. Every proposal requires human review and explicit confirmation before any file is created or modified.

This constraint is not cosmetic. An AI that silently restructures the roadmap destroys the human's ability to reason about the project's direction. The roadmap is a planning artefact, not a cache — it encodes decisions, not just data.

The deliverable is `commands/roadmap-refresh.md`.

## Dependencies

- **block-070** must be complete. The roadmap-refresh command begins by running the roadmap-audit command. The audit output drives what proposals are generated. `commands/roadmap-audit.md` must exist.

## Files

### Read
- `commands/roadmap-audit.md` — to understand the audit output structure that refresh consumes.

### Modify
None.

### Create

**`commands/roadmap-refresh.md`**

Must contain:

**Command name**: `roadmap-refresh`

**Trigger phrase**: "Run roadmap refresh" or "Refresh the roadmap."

---

**CRITICAL CONSTRAINT — READ BEFORE EXECUTING**

This command PROPOSES changes. It does NOT auto-apply any change. No phase file is created, modified, or deleted as a result of running this command. No ROADMAP.md section is modified beyond the Domain Coverage Summary.

All output is written to `_brainstorm/roadmap-refresh-YYYY-MM-DD.md` as a proposals document. Every item in that document is explicitly marked as PROPOSAL.

**Human must review and confirm each proposal before any phase file is created or modified.**

Executing a proposal means: the human reads it, decides it is correct, and explicitly instructs the AI to implement that specific proposal. The AI does not act on proposals autonomously.

---

**Pre-conditions**:

- ROADMAP.md must exist. If not: "ERROR: ROADMAP.md not found. Run roadmap-generation protocol first." Stop.
- phases/ must contain at least one phase file.
- The _brainstorm/ directory must exist. If it does not, create it before writing the output document.

---

**Step 1 — Run roadmap audit**

Execute the full roadmap-audit procedure (defined in `commands/roadmap-audit.md`). Collect the audit report output. Note the overall status (PASS, WARN, or FAIL) and the per-dimension statuses.

If the overall audit status is PASS, report: "Roadmap audit passed. No gaps detected. Roadmap is current. No proposals generated." Stop.

---

**Step 2 — Generate proposals for UNCOVERED gaps**

For each system marked UNCOVERED in Dimension 1 (Coverage):

2a. Read the design/ file for this system.
2b. Assess whether this system is large enough to merit its own phase, or whether it could be an additional block in an existing phase.
2c. Generate one of:
  - PROPOSAL: NEW PHASE — "Create phase-[N] for system [SYSTEM NAME] based on design/[file].md. Suggested title: [title]. Suggested dependencies: [phases]. Estimated duration: [N days]."
  - PROPOSAL: EXTEND EXISTING PHASE — "Add [SYSTEM NAME] coverage to phase-[N] by adding [N] blocks. Rationale: [reason it belongs in the existing phase rather than a new one]."

Each proposal must be self-contained: a human reading only that proposal must understand what to do without consulting any other document.

---

**Step 3 — Generate proposals for DRIFT gaps**

For each phase marked DRIFT in Dimension 1 (Coverage):

3a. Read the phase file. Identify the design/ concept it references that no longer exists.
3b. Search design/ for concepts that may have been renamed or refactored from the original concept.
3c. Generate one of:
  - PROPOSAL: RETIRE PHASE — "Retire phase-[N]. The design concept it implements ([concept name]) no longer exists in design/. Move to archive section of ROADMAP.md."
  - PROPOSAL: RE-ANCHOR PHASE — "Update phase-[N] to reference design/[new-file].md instead of the now-defunct [concept name]. The new concept [new concept name] is the current equivalent."

---

**Step 4 — Generate proposals for STALE gaps**

For each phase marked STALE in Dimension 1 (Coverage):

4a. Read the phase file and the corresponding design/ file.
4b. Identify which parts of the design/ file have changed since the phase was last updated (by comparing headings, system descriptions, and constraint lists).
4c. Generate:
  - PROPOSAL: UPDATE PHASE — "Update phase-[N] to reflect changes in design/[file].md (last updated [date], phase last updated [date]). Key changes in design/: [list 1-3 specific changes]. Suggested phase changes: [list what needs updating]."

---

**Step 5 — Generate proposals for Sequencing issues**

For each cycle or ordering issue found in Dimension 2 (Sequencing):

5a. If cycle: PROPOSAL: BREAK CYCLE — "Phases [list] form a dependency cycle. Suggested resolution: [remove edge X→Y because Z]."
5b. If out-of-order: PROPOSAL: REORDER — "phase-[N] depends on phase-[M] (M > N). Consider renumbering or adjusting dependencies. Suggested action: [specific action]."

---

**Step 6 — Generate proposals for Completeness gaps**

For each uncovered user journey from Dimension 3 (Completeness):

6a. Identify which existing phases are closest in scope to this journey.
6b. Generate:
  - PROPOSAL: COVER USER JOURNEY — "User journey '[journey description]' is not covered by any phase. Suggested phase to add coverage: phase-[N] (existing) or new phase-[N+1]. Rationale: [why this phase is the right home]."

---

**Step 7 — Generate proposals for missing Tracks**

For each perpetual system with no Track from Dimension 4 (Forever Tracks):

7a. Generate:
  - PROPOSAL: CREATE TRACK — "Create tracks/[system-name].md for system [SYSTEM NAME]. This system is designated as perpetual improvement. Use the track template at templates/track.md."

---

**Step 8 — Write proposals document**

Assemble all proposals into `_brainstorm/roadmap-refresh-YYYY-MM-DD.md` using the following structure:

```
---
type: roadmap-refresh-proposals
date: YYYY-MM-DD
audit_status: [PASS|WARN|FAIL]
proposal_count: N
status: awaiting-human-review
---

# Roadmap Refresh Proposals — YYYY-MM-DD

> IMPORTANT: These are PROPOSALS only. No changes have been made to any phase or roadmap file.
> Human must review and confirm each proposal before any phase file is created or modified.
> To act on a proposal, tell the AI: "Implement proposal [N]."

## Audit Summary

[paste audit summary from Step 1]

---

## Proposals

### PROPOSAL 1 — [type]: [short title]

**Type**: [NEW PHASE | EXTEND EXISTING | RETIRE PHASE | RE-ANCHOR | UPDATE PHASE | BREAK CYCLE | REORDER | COVER USER JOURNEY | CREATE TRACK]
**Addresses**: [UNCOVERED | DRIFT | STALE | CYCLE | ORDERING | COMPLETENESS | MISSING TRACK]
**System/Phase affected**: [name]

**Description**:
[Full description of what should be done.]

**Rationale**:
[Why this change is recommended.]

**Human action required**:
[Exact instruction for what to tell the AI to implement this proposal, e.g., "Implement proposal 1."]

---

[Repeat for each proposal.]

---

## Completion

After reviewing all proposals:
- Tell the AI "Implement proposal [N]" for each proposal you approve.
- Tell the AI "Reject proposal [N]" for each proposal you decline (the AI will note the rejection but take no action).
- Tell the AI "All proposals reviewed" when done.
```

---

**Step 9 — Report to human**

After writing the proposals document, output:

"Roadmap refresh complete. [N] proposals generated. Review them at `_brainstorm/roadmap-refresh-YYYY-MM-DD.md`. No changes have been made to any project file. Human must review and confirm each proposal before implementation."

## Validation

- `commands/roadmap-refresh.md` exists.
- File contains the exact string "PROPOSAL" (in the context of marking proposals, not just as a word).
- File contains the exact phrase "Human must review and confirm each proposal before any phase file is created or modified."
- File contains "CRITICAL CONSTRAINT" section.
- File defines all 9 steps.
- File defines a proposal document template with frontmatter and status field.
- No step in the command creates, modifies, or deletes a phase file, template, or protocol file.

## Gates

| Gate | Type | Path(s) / Command | Condition |
|------|------|-------------------|-----------|
| roadmap-refresh-command-exists | file-changed | commands/roadmap-refresh.md | File must exist |
| proposal-keyword-present | cmd | `grep -q "PROPOSAL" commands/roadmap-refresh.md` | exit 0 |
| human-review-clause-present | cmd | `grep -q "Human must review" commands/roadmap-refresh.md` | exit 0 |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Human interprets "Implement proposal N" as permission to implement all proposals | Low | High | Each proposal requires a separate explicit instruction; the command uses singular "Implement proposal [N]" not "Implement all proposals" |
| AI generates proposals that contradict each other (e.g., retire phase-N and extend phase-N) | Low | Medium | Step 8 assembles all proposals before writing; if contradictory proposals are detected, flag them in the document with a CONFLICT note |
| Proposals document grows very large (50+ proposals) and becomes unmanageable | Low | Low | The proposals document includes a count in frontmatter; if count > 20, prepend a warning: "Large number of proposals. Consider breaking this refresh into multiple sessions." |
| _brainstorm/ directory does not exist and cannot be created | Very Low | Low | Pre-conditions section includes creation of _brainstorm/ if absent |

## Out of Scope

- Auto-implementing any proposal, even if the human previously approved a "similar" proposal.
- Diffing two roadmap-refresh proposals documents to detect proposal evolution over time.
- Ranking or prioritising proposals. All proposals are presented flat; prioritisation is the human's decision.
- Generating roadmap-refresh proposals on a schedule. This is a manually triggered command.
