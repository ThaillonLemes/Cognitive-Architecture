# Command: scan-quality

Mode required: guardrails

BRIEF: One-off code quality scan. Reviewer agent runs this OR any agent triggered manually. Produces findings report.

## Usage

- Manual: "run scan-quality" or "follow scan-quality"
- Auto-triggered: after every N blocks closed (configurable; default 10)
- Auto-triggered: at phase-close

## What to scan

### 1. Code smells
- Functions > 50 lines (consider splitting)
- Files > 500 lines (consider splitting)
- Cyclomatic complexity > 10 in any function
- Deep nesting (> 4 levels)

### 2. Duplication
- Identical or near-identical functions (≥ 80% similarity)
- Repeated patterns that warrant abstraction (Rule of Three triggered?)
- Copy-paste detection across files

### 3. Comment hygiene
- Per `protocols/code-header-protocol.md`: every code file has the standard header
- Stale comments (refer to removed code, outdated references)
- Missing comments on non-obvious logic

### 4. Test coverage
- Functions without tests (if testing framework exists)
- Tests that don't actually assert anything
- Skipped tests (`@skip`, `it.skip`, `#[ignore]`) left in code

### 5. Dependency / import hygiene
- Unused imports
- Circular dependencies
- Imports from deprecated modules

### 6. Naming consistency
- Variables that violate stack conventions
- Inconsistent terminology (e.g., `user_id` in one file, `userId` in another)

## What to skip

- Code formatting (lint handles that)
- Performance optimization opportunities (separate `scan-perf` if needed)
- Security issues (separate `scan-security` if needed)

## Output

Generate `governance/scan-quality-<YYYY-MM-DD>.md`:

```yaml
---
id: scan-quality-<YYYY-MM-DD>
ran_at: <ts>
ran_by: <agent-id>
files_scanned: <count>
findings_total: <count>
blockers: <count>
majors: <count>
minors: <count>
nits: <count>
---
```

Body:

```markdown
# Quality scan — <YYYY-MM-DD>

## Summary
- Files scanned: <count>
- Findings: <count> (<blockers> blocker, <majors> major, <minors> minor, <nits> nit)

## Blockers

[Each: file, line, description, suggested fix]

## Majors

[Same format]

## Minors

[Same format]

## Nits

[Same format, brief]

## Suggested next actions

If any findings:
- Generate manifest(s) to address blockers/majors
- Add to phase backlog or future phase
```

## Trigger blocks from findings

For each blocker/major finding, optionally:
- Create `manifests/block-<NNN>-fix-<slug>.md` with status `planned`
- Add it to current phase's Block Index OR a future phase

User decides whether to spawn blocks; agent only proposes.

## Cost

Per scan: ~5K-20K tokens (depends on codebase size and depth).

## Project-specific quality scans

This is the GENERIC scan. Projects may add `scan-quality-rust.md`, `scan-quality-web.md`, etc., for stack-specific checks (memory safety patterns, accessibility, etc.).

End of scan-quality command.
