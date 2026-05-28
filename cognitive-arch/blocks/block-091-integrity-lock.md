---
id: block-091
manifest: manifests/block-091-integrity-lock.md
status: done
gates_passed: 5/5
completed_at: 2026-05-27T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 2
duration_source: estimated
tok_estimated: ~1500
tok_src: estimated
---

# Block 091 Retrospective — Integrity lock file

## 1. What was built

- Created `.integrity.lock` with SHA256 hashes of 8 immutable-tagged files (computed via PowerShell `Get-FileHash`).
- Created `sdk/integrity_check.py` with `verify()` and `regenerate()` functions; CLI modes `--verify`, `--regenerate`, `--strict`.
- Created `commands/integrity-bump.md` documenting human-approval workflow before regeneration.
- Added Check 10 to `audit.sh` (check 9 was already taken by velocity in block-086): WARN when immutable file hashes mismatch; FAIL in `--strict` mode.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| PowerShell hash computation matches file content | manual | pass |
| `sdk/integrity_check.py --verify` returns OK for all 8 files | smoke | pass (hashes match) |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| lock-file-exists | ✓ | `.integrity.lock` created with 8 entries |
| audit-check-9 (now check-10) | ✓ | Check 10 added to audit.sh |
| integrity-script | ✓ | `sdk/integrity_check.py` created |
| dependencies-met | ✓ | block-090 done |
| state-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, retrospective modified |

## 4. Decisions made

- Check numbered 10 (not 9) because block-086 already used check 9 for velocity. Manifest said "check 9" but that slot was taken. Both manifest and audit.sh use the next available slot.

## 5. Deferred to future blocks

- Cryptographic signing (out of scope per manifest §7)
- Auto-bump (always human-approved per `commands/integrity-bump.md`)

## 6. Token estimate

```
tok_estimated: ~1500  tok_src:estimated
```

## 7. Issues / surprises

Check number collision: block-086 pre-empted "check 9" for velocity. Resolved by numbering integrity lock as check 10. No functional impact.

## 8. Files actually touched

As manifest, plus `commands/integrity-bump.md` (was in `create:` list). DX updated: `audit.sh`, `sdk/integrity_check.py`, `commands/integrity-bump.md`, `.integrity.lock`.

---

End of retrospective.
