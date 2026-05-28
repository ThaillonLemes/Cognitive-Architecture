---
id: block-016
manifest: manifests/block-016-dep-graph-check.md
status: done
gates_passed: 3/3
completed_at: 2026-05-21T00:00Z
agent: main-session
commit: -
duration_actual_days: 0
tok_estimated: ~350
tok_src: estimated
---

# Block 016 Retrospective — audit.md dep-graph check improvement

## 1. What was built

- Rewrote check 6 in `commands/audit.md` from a 3-bullet placeholder to a full actionable manual validation procedure.
- Added: valid ID format spec (`^block-\d{3}$`), file resolution check (`ls manifests/block-NNN-*.md`), Q5 status check (dep must be done), manual cycle detection (3-hop trace), severity table (BROKEN DEP = ERROR, DEP NOT DONE = WARN, CYCLE = ERROR).
- Explicit "Automated (Governor-only)" note: full topological sort remains a Governor responsibility.

## 2. Tests added

None (doc-only block).

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| dep-graph-check-documented | ✓ | Check 6 has concrete manual validation steps (4 steps) |
| resolution-steps-clear | ✓ | Valid ID format, file existence check, ls command given |
| files-updated | ✓ | BLOCK_LOG.md updated at phase close |

## 4. Decisions made

- Added DEP NOT DONE (WARN not ERROR) as a severity distinct from BROKEN DEP (ERROR). Q5 violation is a process issue, not a structural corruption.
- Kept the 3-hop manual cycle detection limit explicit — beyond 3 hops, automated tooling is required.

## 5. Deferred to future blocks

- Automated cycle detection in bash → Governor-only / Phase 5
- Cross-phase dependency validation

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| commands/audit.md | ~3,900 | ~975 |
| phases/phase-3.md | ~3,500 | ~875 |

```
tok_estimated: ~350  tok_src:estimated
```

## 7. Issues / surprises

None.

## 8. Files actually touched

- Modified: commands/audit.md (check 6 rewritten; check 3 sub-check 3b added as part of block-015 coordination)
- Otherwise as manifest.
