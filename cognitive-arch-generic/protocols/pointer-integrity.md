---
protection: immutable
protection_reason: "Pointer integrity audit protocol. Core document referenced by audit.sh check 3."
restore_command: "git checkout HEAD -- protocols/pointer-integrity.md"
---

# Protocol: Pointer integrity

BRIEF: Audit rule that validates every cross-file reference resolves. Broken pointers are CRITICAL audit failures. Run as part of `commands/audit.md`.

## What counts as a pointer

- Markdown links: `[text](path/to/file.md)`
- YAML frontmatter file paths: `manifest:`, `files.read`, `files.modify`, `files.create`
- Body-prose file references: `see <path>`, `path/to/file.md`
- INDEX.md catalog entries
- AGENT.md `worktree:` and `branch:` (verify branch exists)
- Manifest `dependencies:` (verify block IDs exist)

## What does NOT count

- External URLs (`https://`)
- Email addresses
- Code identifiers (`function_name()` is not a path)
- Path placeholders in templates (e.g., `<path>` literal)

## Check phases

### Phase 1: File existence

For each markdown link `[text](path)`:
1. Skip if `path` starts with `http://`, `https://`, `mailto:`, or `#` (anchor)
2. Resolve `path` relative to the file's directory
3. Check file exists on disk
4. If not → BROKEN POINTER warning

### Phase 2: YAML path resolution

For each manifest YAML field referencing a path:
- `files.read`: each entry must exist
- `files.modify`: each entry must exist (or marked as new-to-create)
- `files.create`: each entry should NOT exist yet (will be created)
- `manifest:` in NEXT.md: must exist

If a `files.modify` entry doesn't exist, that's a manifest error (creating instead of modifying).

### Phase 3: Block dependency resolution

For each manifest's `dependencies:`:
1. Each entry is a block ID (e.g., `block-031`)
2. Search BLOCK_LOG.md for `<id> done` line
3. If found → dependency is `done`
4. If not in BLOCK_LOG: search manifests/ for `block-<id>-*.md` with status `done` or `integrated`
5. If neither → BROKEN DEPENDENCY warning

### Phase 4: INDEX.md catalog

For each entry in INDEX.md tables:
1. The file/folder path mentioned should exist
2. The brief should be ≤ 1 line
3. If a file exists but is NOT in INDEX.md (and is large enough to warrant cataloging) → DOC-DRIFT warning

### Phase 5: Cross-reference consistency

Check that:
- Phase doc Block Index entries → matching manifest files exist
- Manifest `phase:` → matching phase doc exists with that ID
- Block retrospective `manifest:` field → matching manifest exists (in `manifests/` or `_archive/`)

## Severity

- **ERROR (audit fails):** broken pointer where the source file should know better (manifest's `files.modify` doesn't exist, block dep not found in BLOCK_LOG)
- **WARNING (audit passes with warnings):** broken markdown link in prose docs (less critical), missing INDEX.md entry, code file without header pointer

## Automated detection (audit.sh)

The `audit.sh` script implements Phase 1 (file existence) for `.md` links. The script outputs:

```
WARN: broken pointer in <file>: <path>
```

Phases 2-5 are more complex; typically the Governor agent (in checklist mode) or doc-keeper agent runs them.

## Fixing broken pointers

When audit reports a broken pointer:

1. **Identify cause:**
   - File was renamed → update referrer
   - File was deleted → either remove reference or restore file
   - Typo in path → fix typo

2. **Choose action:**
   - Fix the referring file (most common)
   - Restore the missing target (if deleted in error)
   - Add the file (if expected to exist but doesn't yet → mark as "to be created" in references)

3. **Re-run audit:** confirm pointer resolves now

## Adding pointers correctly

When you add a new pointer:

- Use relative paths from the referring file's directory
- Double-check the path BEFORE saving
- For new files referenced before creation: mark as "TBD" or add to a `planned` block manifest

Example:
```
See [combat design](design/combat.md) for damage rules.
```

If `design/combat.md` doesn't exist yet, either:
- Create the file first (even as placeholder)
- Or change the reference to `[combat design (TBD)](design/combat.md)` until file exists

## Why pointer integrity matters

Without enforced pointer integrity:
- AI misses critical context (jumped to broken link, got nothing, moved on)
- Refactors silently break navigation
- INDEX.md becomes misleading
- New agents can't find existing knowledge

Pointer integrity is the cheap, high-leverage hygiene rule. Don't skip.

End of pointer-integrity protocol.
