---
id: block-009
manifest: manifests/block-009-audit-token-estimation.md
status: done
gates_passed: 3/3
completed_at: 2026-05-21T00:00Z
agent: main-session
commit: -
duration_actual_days: 0
tok_estimated: ~350
tok_src: estimated
---

# Block 009 Retrospective — audit.sh token estimation INFO section

## 1. What was built

- Inserted `[INFO]` section in `audit.sh` between the Governor-only checks block and the AUDIT SUMMARY.
- Per-file loop over 7 HOT files (CLAUDE.md, PROTOCOLS.md, STATE.md, NEXT.md, INDEX.md, _syntax.md, board.md).
- Uses `wc -c` for exact character count (more accurate than estimating from line count).
- ⚠ symbol on files exceeding 1,000 tok; OVER BUDGET / within budget banner for total.
- Suggests `/token-audit` command when over budget.
- Exit code unchanged — INFO section is purely informational.

## 2. Tests added

None (script change is additive INFO only).

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| info-section-present | ✓ | `[INFO]` block iterates HOT files and prints total |
| exit-code-unchanged | ✓ | INFO section uses no `err()` / `warn()` calls; errors variable not touched |
| files-updated | ✓ | BLOCK_LOG.md updated at phase close |

## 4. Decisions made

- Used `wc -c` (bytes/chars) instead of estimating from `wc -l × avg_chars`. More accurate since the file is read anyway.
- Included `board.md` in the HOT list conditionally (present in multi-agent sessions).

## 5. Deferred to future blocks

- SDK-based exact token count → Phase 5
- Per-file token budget as a WARN gate (informational only for now)

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| audit.sh | ~3,600 | ~900 |
| INDEX.md | ~11,700 | ~2,925 |

```
tok_estimated: ~350  tok_src:estimated
```

## 7. Issues / surprises

None. The bash implementation was straightforward — `wc -c` handles binary-safe char counting.

## 8. Files actually touched

- Modified: audit.sh (INFO section inserted before Summary block)
- Otherwise as manifest.
