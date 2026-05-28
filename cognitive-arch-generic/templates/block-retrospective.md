---
protection: immutable
protection_reason: "Block retrospective template. Changes here affect audit parsing of all existing and future retrospectives."
restore_command: "git checkout HEAD -- templates/block-retrospective.md"
---

# Template: Block Retrospective

BRIEF: Written at block close. Facts only (no narrative). Located at `blocks/block-<NNN>-<slug>.md`. Fill using `protocols/block-retrospective-generation.md`.

---

```yaml
---
id: block-<NNN>
manifest: manifests/block-<NNN>-<slug>.md
status: done                          # done | failed | forced | reverted
gates_passed: N/M
completed_at: YYYY-MM-DDTHH:MMZ
agent: <agent-id>
commit: <short-hash>
duration_actual_days: <number>        # vs estimated_duration_days in manifest
actual_duration_hours: <number>       # active implementation time in hours
duration_source: manual|auto-inferred|estimated   # manual=user typed; auto-inferred=git timestamps; estimated=guess
tok_estimated: ~<NNN>                 # chars÷4 estimate for files read during this block
tok_src: estimated                    # estimated | actual (actual requires Phase 5 SDK)
---
```

---

# Block <NNN> Retrospective — <Title>

## 1. What was built

Bullet list. Facts. Example:
- Added `<file>` with `<function>` that does <X>.
- Modified `<file>` to handle <Y>.
- Created test `<file>` covering <Z>.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| `<test_name>` | unit | pass |
| `<test_name>` | integration | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| tests-pass | ✓ | `<command output snippet>` |
| lint-pass | ✓ | clean |
| build-pass | ✓ | exit 0 |
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md modified |

## 4. Decisions made

If any non-obvious decision was taken, link to ADR.
- ADR-<NNN>: <decision title>

If no ADR-worthy decisions: write "None."

## 5. Deferred to future blocks

What this block touched on but did NOT complete:
- <item> → addressed in block-<NNN> or future phase

## 6. Token estimate

Estimate tokens consumed by this block (chars÷4 proxy):

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `<file>` | ~NNN | ~NNN |

```
tok_estimated: ~<NNN>  tok_src:estimated
```

(Sum chars of all files listed in `fread:`. Divide by 4. Use `/token-audit` command for help.)

## 7. Issues / surprises

Anything that diverged from the manifest plan:
- <description>

If no surprises: write "None."

## 8. Files actually touched

If different from manifest declared:
- Added unexpectedly: <list>
- Modified unexpectedly: <list>
- Did not touch as planned: <list>

If exactly as declared: write "As manifest."

---

End of retrospective.
