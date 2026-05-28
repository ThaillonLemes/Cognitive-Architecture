---
id: block-057
manifest: manifests/block-057-audit-checks-78.md
status: done
gates_passed: 3/3
completed_at: 2026-05-22T09:30Z
agent: implementer
commit: -
duration_actual_days: 0
tok_estimated: ~300
tok_src: estimated
---

# Block 057 Retrospective — audit.sh checks 7+8: conflict + drift detection

## 1. What was built

- Created `sdk/audit_helpers.py` (new Python helper, stdlib only):
  - `_load_done_blocks(arch_root)` — reads BLOCK_LOG.md, returns set of done block IDs
  - `check_conflicts(arch_root)` — scans pending (not done) manifests for files.modify path conflicts; prints OK:/WARN: lines
  - `check_drift(arch_root)` — scans BLOCK_LOG for entries with no corresponding `blocks/block-NNN-*.md`; prints OK:/WARN: lines
  - CLI: `--check conflicts|drift|all --arch-root PATH`; exits 0 (clean) or 1 (issues)

- Modified `audit.sh`:
  - Updated header comment and labels from "1–6 of 8; 7–8 stub" to "all 8 checks"
  - Replaced `[7-8/8] stubs` section with actual `[7/8]` and `[8/8]` blocks
  - Both checks detect `python3`/`python` in PATH and call `sdk/audit_helpers.py --check`
  - Output lines prefixed `OK:/WARN:/ERROR:` are routed to `ok()/warn()/err()` functions

## 2. Key design decisions

- **Pending = not in BLOCK_LOG**: initial version used `status: planned` to filter manifests, but blocks from earlier phases have stale `planned` status even after being done. Fixed to use BLOCK_LOG membership: a block is "pending" if its ID is NOT in BLOCK_LOG.md as done. This prevents false positives from completed blocks.
- **WARN not ERROR for conflicts**: cross-manifest conflicts are expected in sequential phases (e.g., block-058 and block-060 both plan to modify `sdk/dispatch.py`). Emitting WARN (not ERROR) keeps exit code 0 while flagging the issue for Governor review.

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| audit-check7 [7/8] | ✓ | `bash audit.sh` contains `[7/8] Checking file conflicts...` |
| audit-check8 [8/8] | ✓ | `bash audit.sh` contains `[8/8] Checking drift...` |
| audit-exits-0 | ✓ | `bash audit.sh` → `Errors: 0`, exits 0 |

## 4. Active warnings in audit output

| Warning | Type | Source |
|---------|------|--------|
| `sdk/dispatch.py` claimed by block-058, block-060 | check-7 | Both are sequential planned blocks (expected) |
| `_syntax.md` exceeds 100 lines | check-2 | Pre-existing |
| 4 broken pointers | check-3 | Pre-existing (decisions/README.md, protocols/pointer-integrity.md) |

## 5. Deferred

- Cycle detection in dependency graph (topological sort — v2.2)
- Automatic conflict resolution

## 6. Token estimate

```
tok_estimated: ~300  tok_src:estimated
```

## 7. Issues / surprises

- First version of `check_conflicts()` used `status: planned` as filter — gave false positives for 3 old blocks (009, 015, 016) with stale manifest status. Fixed in same block by switching to BLOCK_LOG-based pending detection.
- Drift check: all 56 done blocks have retros — `OK` on first run.

## 8. Files actually touched

- `sdk/audit_helpers.py` — created (2 check functions + CLI)
- `audit.sh` — checks 7+8 implemented (stubs replaced)
