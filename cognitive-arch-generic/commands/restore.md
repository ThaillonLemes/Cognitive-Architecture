# Command: restore

BRIEF: Recover a file to its canonical version from git history. Backs up current state first. Requires RESTORE confirmation.

**Script:** `sdk/restore_canonical.py`
**See also:** `protocols/architecture-integrity.md`, `commands/integrity-bump.md`

---

## Usage

```
/restore <relative-file-path>
```

Examples:
```
/restore protocols/block-close-checklist.md
/restore templates/block-retrospective.md
/restore PROTOCOLS.md
```

---

## What it does

1. **Backs up current state** → `_backups/<filename>-<ISO-timestamp>.<ext>` (always, regardless of confirmation outcome)
2. **Fetches canonical version** from `git show HEAD:<relative-path>` (or the most recent commit that touched the file before any current drift)
3. **Displays diff** — current vs canonical
4. **Requires confirmation** — user must type `RESTORE <filename>` to proceed
5. **Writes canonical** to the original path on confirmation

---

## Confirmation phrase

```
RESTORE <relative-file-path>
```

For example: `RESTORE protocols/block-close-checklist.md`

Without this exact phrase, the command shows the diff and exits without changing anything.

---

## After restore

- If the restored file is `protection: immutable`: the `.integrity.lock` hash for it is now correct again. No integrity-bump needed.
- If you restored to a version that differs from HEAD: run `integrity-bump` if the lock is now mismatched.
- The backup file in `_backups/` can be discarded once the restore is confirmed correct.

---

## Script

```bash
python sdk/restore_canonical.py <relative-path> [--arch-root .]
```

For interactive use in a Claude Code session, the AI follows this command's procedure using its file tools (Read, Edit, diff display) rather than running the script directly.

---

End of restore.md.
