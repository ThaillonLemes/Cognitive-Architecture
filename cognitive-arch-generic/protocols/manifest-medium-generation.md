# Protocol: Manifest Tier M generation

BRIEF: How to fill `templates/manifest-medium.md`. Tier M is the DEFAULT for implementation blocks. Read before generating Tier M manifest.

## Trigger

Tier M is appropriate when:
- 3-8 files modified/created
- Implementation work (not just investigation or doc-only)
- Single-module OR clear interface to other modules
- No cross-repo coordination, no activation criteria

Default to Tier M unless you have specific reason for S (smaller) or L (larger).

## Mode

Switch to **guardrails** at start. Fill in **guidance**. Validate in **checklist**.

## Inputs required

1. `PROJECT.md` — for stack/build/test/lint commands and constraints
2. Phase doc declaring this block as `planned`
3. STATE.md
4. Block dependencies (verify all are `done` in board.md)
5. Relevant `design/` docs for domain context
6. Previous similar manifests for naming consistency

## Filling rules

### YAML frontmatter

- `id`: sequential `block-<NNN>`
- `tier`: `M`
- `kind`: `implementation` (default), `refactor`, or `gate`
- `phase`: REQUIRED for Tier M (e.g., `phase-2`)
- `scope`: `phase-bound` (default), `independent`, or `cross-feature`
- `status`: `pending`
- `dependencies`: list of block IDs that must be `done` first
- `files.read`: files this block needs as context (be thorough — avoid surprises)
- `files.modify`: files modified (≤ 8 total with `create`)
- `files.create`: new files
- `gates`: see below
- `created_at`: today

### Gates (universal — always include)

```yaml
gates:
  - name: tests-pass
    cmd: <PROJECT.md test_cmd>
    expect: "0 failed"
  - name: lint-pass
    cmd: <PROJECT.md lint_cmd>
    expect: "0 errors"
  - name: build-pass
    cmd: <PROJECT.md build_cmd>
    expect: "exit 0"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-<NNN>-<slug>.md]
  - name: dependencies-met
    type: deps-complete
    deps: [<dep_block_ids>]
```

### Custom gates (add if needed)

- Performance gate: bench command + threshold
- Integration test: command + expected outcome
- Coverage threshold: tool + minimum %

### Body sections

**§1 Purpose:** 1-2 sentences. The outcome of this block.

**§2 Dependencies:** Repeat YAML deps in prose form. Each must reference a real block ID.

**§3 Files:** Repeat YAML file lists. Be exhaustive — `files.modify` should match what audit.sh sees after commit.

**§4 Validation:** Concrete tests with expected outcomes. Reference commands from gates.

**§5 Gates:** Reference the gates declared in frontmatter. List custom gates here with full detail.

**§6 Risks:** Table. ≥ 1 row if block is non-trivial. Each risk: description + impact + mitigation.

**§7 Out of Scope:** Always fill. ≥ 1 deferral typically (prevents scope creep).

**§8 New Abstraction:** Always fill. If introducing a new trait/class/utility, justify per Rule of Three (Axiom Q1). If none: write "None."

**§9 Benchmarks (OPTIONAL):** Project-specific. Include if performance matters AND benchmarks exist.

**§10 Feature Flags (OPTIONAL):** Project-specific. Include if project uses feature flag system.

**§11 Tunables (OPTIONAL):** Project-specific. Runtime configuration values.

**§12 Metrics (OPTIONAL):** Project-specific. Observability counters/gauges.

**§13 Integration Boundaries (OPTIONAL):** Include if block touches a clear API boundary with another module.

## Validation before save

Switch to checklist:
- [ ] YAML frontmatter parseable
- [ ] Tier truly is M (3-8 files modify+create)
- [ ] Dependencies all reference real block IDs that exist in BLOCK_LOG or are `planned`
- [ ] Gates include the 5 universal gates
- [ ] All file paths resolve (or marked "to be created")
- [ ] §1, §2, §3, §4, §5, §7, §8 are filled (not placeholders)
- [ ] §6 Risks has ≥ 1 entry if block is non-trivial
- [ ] OPTIONAL sections (§9-§13) included only if relevant

## Parallel-with consideration

If this block can run in parallel with others (same parallel group in phase doc):
- Add `parallel_with: [<block-id>]` to frontmatter
- Verify `files.modify` is disjoint with the parallel block's `files.modify`
- Document in body: "Parallel-with: block-<NNN> — disjoint file sets verified."

## Output

Save to `manifests/block-<NNN>-<slug>.md`. Update STATE.md, NEXT.md if this is the next active block.

## When to upgrade to Tier L

During filling, if you realize:
- Files modify+create exceeds 8 → consider Tier L
- Cross-repo (multi-repo) coordination needed → Tier L
- Block is a gate with activation criteria → Tier L
- Rollout plan with multiple stages → Tier L

End of manifest-medium-generation protocol.
