---
id: block-050
manifest: manifests/block-050-readme-update.md
status: done
gates_passed: 2/2
completed_at: 2026-05-22T07:00Z
agent: implementer
commit: -
duration_actual_days: 0
tok_estimated: ~1500
tok_src: estimated
---

# Block 050 Retrospective — Update README.md for new adopters (v2.0)

## 1. What was built

- Rewrote `README.md` with Governor v2 capabilities and Phase 6 additions
- New sections added: "Quick start" (new project + retrofit paths), "Governor v2 (optional SDK tier)" (install + enable steps), "Stack addenda" (table with all 3 files)
- Updated: "What it provides" (added Governor v2 line + stack addenda line), "File map" (added sdk/), "Quick concepts" (added governor_mode: manual + sdk bullets)
- Removed: stale "via worktrees" language; replaced with accurate two-tier description
- Final line count: ~103 lines (within 130-line gate)

## 2. Tests added

None (doc-only).

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| readme-updated | ✓ | README.md modified; contains "governor_mode", all 3 stack addenda linked, BOOTSTRAP.md + RETROFIT.md linked |
| file-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md modified |

## 4. Decisions made

- Governor v2 section kept to 10 lines (well under 15-line gate) by pointing to Appendix A in BOOTSTRAP/RETROFIT for detail
- Quick start uses short paths (no `cd` hell) matching existing format

## 5. Deferred to future blocks

- Folder map section (kept from original; not updated — would make README too long)
- Badges (CI, version) — when there's something to badge

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `README.md` (original) | ~3200 | ~800 |
| `RETROFIT.md` (Appendix A, verify consistency) | ~600 | ~150 |

```
tok_estimated: ~950  tok_src:estimated
```

## 7. Issues / surprises

Removed the `## Folder map` section from original README (it was 14 lines and largely duplicated the File map). Kept File map focused on top-level files only. This reduced line count while improving clarity.

## 8. Files actually touched

As manifest (README.md only).
