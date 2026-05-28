---
protection: immutable
protection_reason: "L-tier manifest schema. Changing this breaks all existing L-tier manifest validation."
restore_command: "git checkout HEAD -- templates/manifest-large.md"
---

# Template: Manifest Tier L (Large — gate / cross-system)

BRIEF: For phase soak gates, protocol changes, cross-repo coordination, large refactors, activation ramps. Extends Tier M with cross-repo, rollout, and activation sections.

Copy to `manifests/block-<NNN>-<slug>.md`.

---

```yaml
---
id: block-<NNN>
tier: L
kind: gate                            # gate | implementation | refactor
phase: phase-<N>
scope: phase-bound                    # phase-bound | cross-feature | cross-repo
status: pending
security: false                       # set to true for blocks touching auth, networking, or persistent data
dependencies:
  - block-<NNN>
  - <other-repo> block-<NNN>          # cross-repo if applicable
files:
  read:
    - <path>
  modify:
    - <path>                          # total modify + create ≤ 15 paths
  create:
    - <path>
gates:
  - name: tests-pass
    cmd: <test_cmd>
    expect: "0 failed"
  - name: lint-pass
    cmd: <lint_cmd>
    expect: "0 errors"
  - name: build-pass
    cmd: <build_cmd>
    expect: "exit 0"
  - name: integration-pass
    cmd: <integration_test_cmd>
    expect: "exit 0"
  - name: activation-criteria-met
    type: activation
    criteria: [<criterion-name>]
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-<NNN>-<slug>.md]

cross_repo_impact:                    # OPTIONAL — only if multi-repo
  affected_repos: [<repo1>, <repo2>]
  protocol_bump: false                # true if wire/API contract changes

rollout_plan:                         # OPTIONAL — for activation blocks
  stages:
    - <stage1>                        # e.g., Disabled
    - <stage2>                        # e.g., Enabled-In-Bench
    - <stage3>                        # e.g., Enabled-In-Soak
    - <stage4>                        # e.g., Enabled-Default

activation_criteria:                  # OPTIONAL — for gate blocks
  - name: <metric or behavior>
    threshold: <quantitative target>
    measurement: <how measured>
    evidence: <log path or output location>
    pass_fail: pending

created_at: YYYY-MM-DD
# Optional fields:
# parallel_with: [block-<NNN>]
# estimated_duration_days: <number>
# benchmarks, flags, tunables, metrics (see manifest-medium)
# axiom_override: "<axiom-id> — justification"
---
```

---

# Block <NNN> — <Title>

- **Tier:** L
- **Kind:** gate | implementation | refactor
- **Status:** pending

## 1. Purpose

One sentence describing the outcome.

## 2. Dependencies

All dependencies must be `done` before this block starts.

## 3. Files

- **Read:**
- **Modify:**
- **Create:**

## 4. Validation

Concrete validation steps for build, test, lint, integration.

## 5. Gates

See YAML frontmatter. Add custom gates here.

## 6. Risks

Risks table with mitigations.

## 7. Out of Scope

Explicit deferrals.

## 8. New Abstraction

Per Rule of Three. Justify or "None."

## 9. Cross-Repo Impact [if multi-repo]

| Repo | Files affected | Migration order |
|------|---------------|-----------------|
| <repo> | <list> | <description> |

For protocol/contract bumps: enumerate every consumer and follow-up block.

## 10. Rollout Plan [if activation block]

Stages of rollout:
- Step 1: Land code with flag at <initial state>.
- Step 2: Run benchmark harness; gate at <criteria>.
- Step 3: Promote flag to <next state>.
- Step 4: Soak duration; criteria; promotion or rollback.
- Step 5: <final state>.

## 11. Activation Criteria [if gate block]

Quantitative pass/fail criteria:

| Name | Threshold | Measurement | Evidence path | Pass/Fail |
|------|-----------|-------------|---------------|-----------|
| <metric> | <target> | <how> | <location> | pending |

## 12. Rollback Plan

If the block fails activation:
- Revert code to <state>.
- Reset flag to <state>.
- Notify <stakeholders>.

## 13. Benchmarks / Flags / Tunables / Metrics [OPTIONAL]

Same as Tier M, expanded for the larger scope.

---

Total file size target: ≤ 8 KB.

L-tier manifests are reviewed by the Governor before block start to verify cross-cutting coordination is sound.
