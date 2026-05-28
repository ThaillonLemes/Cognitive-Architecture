---
id: block-125
phase: phase-20
tier: M
status: done
actual_duration_hours: 1.0
duration_source: estimated
tok_actual: 5400
gates_passed: 2/3
created_at: 2026-05-28
---

# Block 125 Retrospective — proposal_resolver.py

## 1. What was built

- `sdk/proposal_resolver.py`: `ProposalResolver.accept(id, apply)` and `ProposalResolver.reject(id, note)`
- `_update_frontmatter_field(text, field, value)`: in-place YAML front matter update (replace or insert)
- `_get_frontmatter_field(text, field)`: extract field value from front matter
- `_update_index_status(index_path, id, status)`: regex-based status column update in index.md
- `_is_immutable(target_file, arch_root)`: checks PROTOCOLS.md mentions + file `protection: immutable` header
- `accept(apply=True)`: creates .bak backup, appends annotation, aborts on immutable/missing/placeholder target
- `reject(note)`: appends note section, updates file + index
- `sdk/tests/test_proposal_resolver.py`: 28 tests

## 2. Gates

- tests-pass: 634 passed, 0 failed ✓
- lint-pass: flake8 not installed — syntax verified with `py_compile` ✓ (skipped)
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- `accept(apply=True)` appends an HTML comment annotation to target_file — non-destructive; human edits the actual content
- `.bak` extension: `target.md.bak` (safe shutil.copy2, never overwrites existing content)
- Placeholder guard: aborts when `target_file` contains `<target>` — prevents silent no-op patches
- `already accepted/rejected` guard prevents double-resolution

## 4. DX updated

`sdk/proposal_resolver.py` created. CLI: `--accept ID [--apply]`, `--reject ID [--note "..."]`.
Referenced in `_render_proposal()` footer: `python sdk/proposal_resolver.py --accept <id>`.
