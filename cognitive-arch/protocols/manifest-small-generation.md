# Protocol: Manifest Tier S generation

BRIEF: How to fill `templates/manifest-small-v2.md`. Tier S is for: investigation, doc-only, single-file fix, lint sweep, refactor ≤ 2 files. Read before generating Tier S manifest.

## Trigger

Tier S is appropriate when ALL:
- ≤ 2 files modified
- No new abstraction introduced
- No cross-module / cross-repo impact
- Purpose is: investigate, document, fix small bug, lint sweep, or trivial refactor

If ANY of those conditions are violated, escalate to Tier M.

## Mode

Switch to **guardrails** at start (verify Tier S is appropriate). Fill in **guidance**. Validate in **checklist**.

## Inputs required

1. `PROJECT.md` — for test_cmd, lint_cmd, build_cmd to populate gates
2. Phase doc declaring this block as `planned`
3. STATE.md — to know current phase
4. Block dependencies (if any) — to verify they're `done`

## Filling rules

### YAML frontmatter

- `id`: `block-<NNN>` with sequential numbering (continue from last in BLOCK_LOG)
- `tier`: `S`
- `kind`: pick exactly one — `investigation`, `refactor`, `doc-only`, `small-fix`
- `phase`: optional for Tier S (small tasks may not belong to a phase)
- `status`: starts as `pending`
- `files.read`: at least 1 path
- `files.modify`: 0-2 paths (empty for investigation)
- `files.create`: 0-1 paths typically
- `gates`: include the universal ones (tests-pass, files-updated)
- `created_at`: today's date

### Body sections

**§1 Purpose:** Exactly one sentence. If you need two, you probably need Tier M.

**§2 Files:** Repeat the YAML frontmatter file lists in human-readable form.

**§3 Validation:** Concrete verifications. For investigation: "finding doc committed at `<path>`". For fix: "tests passing + lint clean". For doc-only: "files updated AND brief sections present".

**§4 Out of Scope:** What this block is NOT doing. Even Tier S declares this.

## Gates for Tier S

Default gates (always include in `gates:`):
- `tests-pass`: cmd = PROJECT.md `test_cmd`, expect = "0 failed"
- `files-updated`: STATE.md, NEXT.md, BLOCK_LOG.md modified

Investigation-specific gates:
- `finding-doc-exists`: file at `<path>` exists

Refactor/fix-specific gates:
- `lint-pass`: cmd = PROJECT.md `lint_cmd`

## Validation before save

Switch to checklist:
- [ ] YAML frontmatter parseable
- [ ] Tier truly is S (≤ 2 files modify, no new abstraction)
- [ ] All file paths in `files.read/modify/create` exist OR are documented as "to be created"
- [ ] Dependencies (if any) reference real block IDs
- [ ] Gates list is realistic and runnable

## Output

Save to `manifests/block-<NNN>-<slug>.md`. Update STATE.md `next:` field. Update phase doc's block index to reflect status `pending`.

## When to escalate

If during filling you realize:
- A new abstraction is needed → upgrade to Tier M
- Files modify count goes above 2 → upgrade to Tier M
- Cross-module impact discovered → upgrade to Tier M

End of manifest-small-generation protocol.
