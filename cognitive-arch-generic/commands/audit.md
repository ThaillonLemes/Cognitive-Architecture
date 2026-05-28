# Command: audit

Mode required: checklist

BRIEF: Run a comprehensive audit of the cognitive architecture. Validate structure, pointers, drift indicators. Generate `governance/audit-<YYYY-MM-DD>.md` if findings warrant.

## Usage

- Manual: "follow commands/audit.md" or "run audit"
- Auto-triggered by Governor: every 30 blocks integrated, every phase close
- Auto-triggered by `audit.sh` (shell script version of basic checks)

## What it does

Run 8 audit checks in order:

| Checks | Tool |
|--------|------|
| 1–4 | `audit.sh` (script-executable; run `./audit.sh`) |
| 5–8 | Governor agent only (LLM reasoning required; run this command) |

### 1. HOT files exist (script)
- CLAUDE.md, PROTOCOLS.md, STATE.md, NEXT.md, INDEX.md, board.md, _syntax.md, PROJECT.md
- ERROR if missing

### 2. File size budgets (script)
Per Axiom Q2:
- CLAUDE.md ≤ 60 lines
- STATE.md ≤ 60 lines
- NEXT.md ≤ 30 lines
- INDEX.md ≤ 250 lines
- board.md ≤ 150 lines
- AGENT.md per agent ≤ 50 lines
- WARN if exceeded

### 3. Pointer integrity (script, partial — markdown links only)
Per `protocols/pointer-integrity.md`:
- All markdown links resolve
- All YAML file paths exist (or marked as to-be-created)
- All block dependency IDs in BLOCK_LOG.md or planned manifests
- All INDEX.md catalog entries match actual files
- WARN per broken link; ERROR for critical broken paths (manifest's files.modify)

**Sub-check 3b (script): YAML path existence — files.modify** *(Phase 3 addition)*
- For each manifest in `manifests/`, extract paths listed under `files.modify`
- Verify each path exists on disk (`-f` check)
- Paths under `files.create` are NOT checked (they don't exist yet by design)
- Severity: WARN (not ERROR — schemas stabilizing)
- Implemented in `audit.sh` between check 3 and check 4

### 4. AI-only file format + bootstrap consistency (script)
- STATE.md, NEXT.md, board.md follow `_syntax.md` vocabulary
- No prose paragraphs
- Key:value format
- WARN per non-conforming line

### 5. Manifest schema validation (Governor-only)
- Every manifest in `manifests/` has valid YAML frontmatter
- Tier matches schema (S/M/L)
- Required fields present per tier
- ERROR per invalid manifest

### 6. Dependency graph (Governor-only, partially manual)

**What a valid dependency ID looks like:**
- Format: `block-NNN` (three-digit zero-padded number)
- Must resolve to an existing manifest file: `manifests/block-NNN-*.md`

**Manual validation steps:**
1. List all manifests with non-empty `dependencies:` field:
   - Grep: `grep -l "dependencies:" manifests/block-*.md`
   - For each, read the `dependencies:` list
2. For each dependency ID `block-NNN`:
   - Check: `ls manifests/block-NNN-*.md` — if no match → **BROKEN DEP** (ERROR)
   - Check status field in that manifest: if not `done` and the dependent block is `wip` → **DEP NOT DONE** (WARN per Q5)
3. Cycle detection (manual, 3 levels deep):
   - For block A depending on block B: check if B depends on A → **CYCLE** (ERROR)
   - Trace up to 3 hops. Full cycle detection is Governor-only (automated graph traversal).

**Automated (Governor-only):**
Full topological sort and cycle detection are Governor responsibilities.
Script checks: only ID format validation and file existence (not cycles).

**Findings:**
- BROKEN DEP → ERROR
- DEP NOT DONE (wip block depending on non-done block) → WARN
- CYCLE detected manually → ERROR

### 7. File-conflict detection (Governor-only)
- For all `pending`+`wip` manifests: pairwise check `files.modify` overlap
- ERROR per overlapping pair

### 8. Drift indicators (Governor-only)
- Axiom overrides accumulated in last 30 days (WARN if > 5)
- Blocks closed with `forced` status (WARN if > 3 in last 30 days)
- Manifests modified after closing (WARN — should be append-only after `done`)
- Lock stuck `in-progress` > 1h (WARN — stale)

## Output format

Generate report at `governance/audit-<YYYY-MM-DD>.md` per `templates/audit-report.md`.

If audit is part of `audit.sh` run: also output to stdout (the shell script handles this).

## Exit codes

- 0: pass (no errors, possibly warnings)
- 1: fail (≥1 error)
- 2: pass with significant drift indicators

## Mode behavior

In checklist mode, the agent:
- Does NOT speculate ("this might be an issue")
- Outputs definitive pass/fail per check
- Cites evidence for each finding
- Does NOT auto-fix (only Governor or implementer can fix; this is detection only)

## After audit

If audit detects fixable issues:
- Doc-keeper agent can be triggered to fix doc-drift
- Implementer can be tasked with manifest fixes
- Governor records findings in governance/

If audit passes clean:
- Update STATE.md with audit timestamp
- Move on

End of audit command.
