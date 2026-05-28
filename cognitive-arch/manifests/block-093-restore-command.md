---
id: block-093
tier: S
kind: implementation
phase: phase-13
status: pending
security: false
dependencies: [block-091, block-092]
files:
  read:
    - protocols/architecture-integrity.md
    - sdk/integrity_check.py
    - design/arch-v3.md
  modify: []
  create:
    - commands/restore.md
    - sdk/restore_canonical.py
gates:
  - name: command-created
    type: file-changed
    paths: [commands/restore.md, sdk/restore_canonical.py]
  - name: dependencies-met
    type: deps-complete
    deps: [block-091, block-092]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-093-restore-command.md]
created_at: 2026-05-23
---

# Block 093 — Restore canonical command

- **Tier:** S
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Implement `/restore <file>` command that recovers any file from its canonical source (git history or backup) with safety: automatic backup of current state to `_backups/` (D2), diff display, RESTORE textual confirmation required.

## 2. Files

- **Read:** architecture-integrity protocol, integrity_check.py, arch-v3 design
- **Modify:** —
- **Create:** `commands/restore.md` (procedure), `sdk/restore_canonical.py` (logic)

## 3. Validation

- `/restore <file>` shows: current vs canonical diff, backup path, RESTORE prompt
- Backup auto-created at `_backups/<filename>-<ISO-timestamp>.md` before any change
- Command refuses without explicit RESTORE confirmation phrase
- Works for both immutable (with override registered) and open files

## 4. Out of scope

- Bulk restore (one file at a time for v1)
- Restore from arbitrary git revision (always HEAD or canonical)
- Cross-repo restore (single-repo today)
