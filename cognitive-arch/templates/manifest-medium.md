---
protection: immutable
protection_reason: "M-tier manifest schema (default). Changing this breaks all existing M-tier manifest validation."
restore_command: "git checkout HEAD -- templates/manifest-medium.md"
---

# Template: Manifest Tier M (Medium — default)

BRIEF: Default tier for implementation blocks. Up to 8 files modified/created. Sections marked OPTIONAL are project-specific (include only if applicable).

Copy to `manifests/block-<NNN>-<slug>.md`.

---

```yaml
---
id: block-<NNN>
tier: M
kind: implementation                  # implementation | refactor | gate
phase: phase-<N>
scope: phase-bound                    # phase-bound | independent | cross-feature
status: pending
security: false                       # set to true for blocks touching auth, networking, or persistent data
dependencies:
  - block-<NNN>                       # same-project
files:
  read:
    - <path>
  modify:
    - <path>                          # total modify + create ≤ 8 paths
  create:
    - <path>
gates:
  - name: tests-pass
    cmd: <test_cmd from PROJECT.md>
    expect: "0 failed"
  - name: lint-pass
    cmd: <lint_cmd from PROJECT.md>
    expect: "0 errors"
  - name: build-pass
    cmd: <build_cmd from PROJECT.md>
    expect: "exit 0"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-<NNN>-<slug>.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-<NNN>]
created_at: YYYY-MM-DD
# Optional fields:
# parallel_with: [block-<NNN>]
# estimated_duration_days: <number>
# benchmarks: [<bench_name>]
# flags: [<flag_name>]
# tunables: [<tunable_name>]
# metrics: [<metric_name>]
# axiom_override: "<axiom-id> — justification"
---
```

---

# Block <NNN> — <Title>

- **Tier:** M
- **Kind:** implementation | refactor | gate
- **Status:** pending
- **Parallel-with:** <block IDs that can run concurrently; omit if none>

## 1. Purpose

One or two sentences describing the outcome.

## 2. Dependencies

Prior block IDs (must be `done`). Format: `block-<NNN>`.

## 3. Files

- **Read:** <list of files this block reads as context>
- **Modify:** <list of files this block modifies>
- **Create:** <list of files this block creates>

## 4. Validation

Concrete validation steps. At minimum:
- Build succeeds: `<build_cmd>`
- All tests pass: `<test_cmd>`
- Lint clean: `<lint_cmd>`
- [Additional project-specific tests]

## 5. Gates

Reference to declared gates in YAML frontmatter. Add custom gates here if needed.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| <description> | <high/med/low> | <plan> |

## 7. Out of Scope

Explicit deferrals (prevents scope creep).
- <deferral 1>
- <deferral 2>

## 8. New Abstraction

If introducing a new trait, generic, class, base, or utility: name + justification per Rule of Three (Axiom Q1).

If no new abstraction: write "None."

## 9. Benchmarks [OPTIONAL — project-specific]

Named benches with target thresholds. Example:
- `bench_<name>`: p50 < <target>, p99 < <target>

## 10. Feature Flags [OPTIONAL — project-specific]

Flags introduced or modified.
- `<flag_name>` — <state transition, e.g., Disabled → Enabled-In-Bench>

## 11. Tunables [OPTIONAL — project-specific]

Tunables introduced or modified.

## 12. Metrics [OPTIONAL — project-specific]

Metrics introduced or modified.

## 13. Integration Boundaries [OPTIONAL — if cross-module]

Touchpoints with other systems.

---

Total file size target: ≤ 5 KB.

If block needs cross-repo coordination, rollout planning, or activation criteria → upgrade to Tier L.
