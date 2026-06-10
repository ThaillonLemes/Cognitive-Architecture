# Protocol: Block retrospective generation

BRIEF: How to fill `templates/block-retrospective-v2.md`. Written at block close. Facts only — no narrative.

## Trigger

Generate a block retrospective when:
- Block manifest gates have all passed (or `forced` flag applied)
- About to commit and close the block
- Per `protocols/block-close-checklist.md` step 5

## Mode

**checklist** — strict yes/no on every section. Facts, not stories.

## Inputs required

- Block manifest (`manifests/block-<NNN>-<slug>.md`)
- Actual files modified (from `git diff --name-only`)
- Gate results (each gate ran with output captured)
- Any ADRs created during the block (in `decisions/`)

## Filling rules

### YAML frontmatter

- `id`: matches block ID
- `manifest`: path to the source manifest
- `status`: `done` (if gates passed) | `forced` (if user overrode) | `failed` (rare — typically halt before this)
- `gates_passed`: N/M based on actual gate run
- `completed_at`: timestamp of commit
- `agent`: who closed the block (from AGENT.md)
- `commit`: short hash of the closing commit
- `duration_actual_days`: actual wall-clock from block-start to block-close

### Body sections

**§1 What was built:**
- Bullet list of CONCRETE artifacts
- Files added, files modified (with what changed conceptually — not line-by-line)
- Functions/classes/modules introduced
- Tests added (functional summary, not test names)
- NO storytelling ("we struggled with X then figured out Y")

**§2 Tests added:**
- Table: test name | type (unit/integration/e2e) | result (pass/fail)
- If 0 tests added (e.g., doc-only block): write "None."

**§3 Gates passed:**
- Table: gate | result | evidence (snippet or pointer)
- Every gate from manifest enumerated

**§4 Decisions made:**
- If ADR(s) created: list ADR IDs and titles
- If none: "None."

**§5 Deferred to future blocks:**
- What was touched on but not completed
- Each item: brief + target block (or "future phase" if unscoped)

**§6 Issues / surprises:**
- Anything that diverged from the manifest plan
- Format: brief description + how it was handled
- If clean execution: "None."

**§7 Files actually touched:**
- If matches manifest declared: write "As manifest."
- If diverged: list (a) added unexpectedly, (b) modified unexpectedly, (c) NOT touched as planned

## Validation before save

- [ ] YAML frontmatter parseable
- [ ] §1-§3 always filled
- [ ] §4-§7 always filled (with "None" or "As manifest" when applicable)
- [ ] No narrative paragraphs (this is facts only)
- [ ] All gate names match those in the source manifest
- [ ] If `status: forced`, rationale captured (see Forced flag rules)

## Forced flag rules

If a gate failed but user overrode:
- `status: forced` in frontmatter
- Add YAML field: `forced_rationale: "<user-provided reason>"`
- §3 Gates table: list the failed gate with `result: forced` and evidence of override
- §6 Issues: describe what failed and why user chose to proceed

This creates an auditable record. Future audit detects accumulation of `forced` blocks as drift signal.

## Output

Save to `blocks/block-<NNN>-<slug>.md`. Note: this is in `blocks/` (retrospectives), not `manifests/` (planning artifacts).

## Use by future blocks

Retrospectives are read when:
- A future block depends on this one and needs context
- Reviewer agent scans for patterns
- Audit detects drift indicators (forced count, surprise count)
- Phase retrospective synthesizes all block retros

End of block-retrospective-generation protocol.
