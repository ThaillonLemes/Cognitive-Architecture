# Command: integrity-bump

BRIEF: Regenerate `.integrity.lock` after a legitimate, approved change to an immutable file.

**Script:** `sdk/integrity_check.py --regenerate --arch-root .`
**Requires:** Human approval before running (see protocol below)

---

## When to use

Run this command ONLY when:

1. A block was explicitly approved (by the user) to modify a file tagged `protection: immutable`
2. The block has closed with all gates passing
3. The modification was intentional and reviewed — not accidental drift

Do NOT run if `audit.sh` check 10 warns unexpectedly. That warning is a signal to investigate, not to bump the lock.

---

## Protocol (human-approval required)

Before running `--regenerate`, the user must confirm:

```
INTEGRITY BUMP APPROVED
file: <relative path>
reason: <why the immutable file was changed>
block: <block-NNN that made the change>
approved_by: <user>
date: <YYYY-MM-DD>
```

Log this approval in `.governor/log.md` (or the equivalent governance log).

---

## Steps

1. Confirm all intended immutable-file changes are committed (or staged)
2. Record approval in governance log (see above)
3. Run: `python sdk/integrity_check.py --regenerate --arch-root .`
4. Verify output lists exactly the expected files
5. Commit `.integrity.lock` as part of the block close commit

---

## After bump

Run `python sdk/integrity_check.py --verify --arch-root .` to confirm the new lock matches the current state.

---

End of integrity-bump.md.
