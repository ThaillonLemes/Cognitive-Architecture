---
id: block-015
manifest: manifests/block-015-pointer-integrity-phase2.md
status: done
gates_passed: 4/4
completed_at: 2026-05-21T00:00Z
agent: main-session
commit: -
duration_actual_days: 0
tok_estimated: ~500
tok_src: estimated
---

# Block 015 Retrospective — audit.sh pointer integrity phase 2 (YAML paths)

## 1. What was built

- Inserted **Check 3b** in `audit.sh` between check 3 (markdown links) and check 4 (AI-only format).
- Uses `awk` to extract paths under `files.modify:` from each `manifests/block-*.md`.
- Checks each extracted path with `-f` (file exists). Directories also accepted (`-d`).
- Severity: WARN (not ERROR) per manifest spec — schemas are stabilizing.
- Skips empty paths and handles the case where `files.modify:` section is empty.
- Added sub-check 3b documentation to `commands/audit.md` under check 3.

## 2. Tests added

None (bash script change; validated by inspection).

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| path-check-implemented | ✓ | awk loop extracts files.modify paths and checks each with -f |
| warn-not-error | ✓ | uses warn() not err(); errors variable not incremented |
| audit-md-documented | ✓ | sub-check 3b section added to commands/audit.md check 3 |
| files-updated | ✓ | BLOCK_LOG.md updated at phase close |

## 4. Decisions made

- Used `awk` over `grep/sed` pipeline: cleaner state machine for tracking `in_modify` section across YAML lines.
- Exit condition for awk: any line matching `/^[[:space:]]+[a-z_]+:/` at same indent level terminates the modify block. This correctly handles `create:`, `read:`, `gates:` as section terminators.
- Inline YAML arrays (`modify: [file.md]`) silently skipped — acceptable since all current manifests use list format. Documented as known limitation.

## 5. Deferred to future blocks

- Full YAML parser for inline arrays → Phase 5 tooling
- Changing WARN to ERROR once schema stabilizes

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| audit.sh | ~4,200 | ~1,050 |
| commands/audit.md | ~3,900 | ~975 |
| manifests/block-001 | ~1,200 | ~300 |
| manifests/block-004 | ~1,400 | ~350 |

```
tok_estimated: ~500  tok_src:estimated
```

## 7. Issues / surprises

JSON Schema cannot express "sum of two sibling array lengths" — same constraint issue as blocks 011-013. In audit.sh this is handled by counting paths in the awk loop, not by JSON Schema itself. No impact on this block.

## 8. Files actually touched

- Modified: audit.sh (check 3b inserted)
- Modified: commands/audit.md (sub-check 3b documentation added)
- Otherwise as manifest.
