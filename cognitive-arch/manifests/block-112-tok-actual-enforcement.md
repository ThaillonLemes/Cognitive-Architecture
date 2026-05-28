---
id: block-112
tier: S
kind: small-fix
phase: phase-18
status: planned
security: false
files:
  read:
    - sdk/block_close.py
    - templates/block-retrospective.md
  modify:
    - sdk/block_close.py
  create: []
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
---

# Block 112 — tok_actual Enforcement

- **Tier:** S
- **Kind:** small-fix
- **Status:** planned

## 1. Purpose

Add tok_actual presence check to block_close.py. If a block's retro file exists but has no `tok_actual` field (or it is null/empty), emit a WARN and halt. The --force flag bypasses the halt. This makes tok_actual mandatory without breaking historical block-close flows.

## 2. Dependencies

None (first block of phase-18).

## 3. Files

- **Read:** sdk/block_close.py, templates/block-retrospective.md
- **Modify:** sdk/block_close.py — add `_check_tok_actual()` function and call it before step 2
- **Create:** None

## 4. Validation

- Close a test block with a retro missing tok_actual — confirm WARN + halt
- Close a test block with tok_actual: 1500 — confirm proceeds normally
- Close a test block with missing retro AND no --force — confirm existing WARN (unchanged)
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass: `python -m pytest sdk/tests/ -q` → "0 failed"
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md changed

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Check fires on historical blocks being re-closed | Low | Check reads retro file; historical retros get null — not zeroed — no false halt |
| Regex mismatch on tok_actual field variants | Low | Accept: tok_actual, tok-actual, tokens_actual (normalize via regex) |

## 7. Out of Scope

- Backfilling tok_actual on existing retros (token_tracker.py handles null gracefully)
- Validating tok_actual is a number (type check in token_tracker.py, block 113)

## 8. New Abstraction

`_check_tok_actual(arch_root, block_id, force)` — added to block_close.py. Returns (ok: bool, message: str). Consistent with existing `_check_retro()` pattern.
