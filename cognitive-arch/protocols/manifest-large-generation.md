# Protocol: Manifest Tier L generation

BRIEF: How to fill `templates/manifest-large.md`. Tier L is for: phase gates, cross-repo coordination, activation ramps, large refactors. Read before generating Tier L manifest.

## Trigger

Tier L is appropriate when ANY:
- Cross-repo coordination needed (≥ 2 repos affected)
- Phase soak gate or activation gate (with quantitative pass/fail criteria)
- Rollout plan with multiple stages (e.g., Disabled → Bench → Soak → Default)
- Large refactor touching >8 files OR introducing new abstraction with broad reach
- Protocol/API contract change with downstream consumers

If those don't apply, prefer Tier M.

## Mode

Switch to **guardrails** at start (Tier L is high-risk). Fill in **guidance**. Validate in **checklist** with extra rigor.

## Inputs required

Same as Tier M, plus:
- Other affected repos / modules / consumers
- Activation criteria (if gate block) — quantitative
- Rollout plan stages (if activation block)
- Cross-repo dependency clarification

## Filling rules

### YAML frontmatter — additional sections

Beyond Tier M's frontmatter:

```yaml
cross_repo_impact:                    # if multi-repo
  affected_repos: [<repo1>, <repo2>]
  protocol_bump: false                # true if API/contract changes

rollout_plan:                         # if activation block
  stages:
    - <stage1>
    - <stage2>
    - <stage3>
    - <stage4>

activation_criteria:                  # if gate block
  - name: <metric or behavior>
    threshold: <quantitative>
    measurement: <how>
    evidence: <where logged>
    pass_fail: pending
```

### Gates — universal + Tier L additions

Same 5 universal gates as Tier M, plus:

- `integration-pass` — full integration test suite
- `activation-criteria-met` — for gate blocks: each criterion in `activation_criteria` must reach `pass`

### Body sections

All Tier M sections PLUS:

**§9 Cross-Repo Impact:** Table — each affected repo, files touched, migration order. For protocol bumps: every consumer enumerated with follow-up block.

**§10 Rollout Plan:** Step-by-step stages with:
- What changes per stage
- What flags are flipped
- What metrics are watched
- Promotion criteria to next stage
- Rollback trigger at each stage

**§11 Activation Criteria:** Quantitative pass/fail table:
- Name (specific metric or behavior)
- Threshold (numeric or measurable)
- Measurement (how the value is obtained)
- Evidence path (where the result is logged)
- Pass/fail status (filled at gate evaluation)

**§12 Rollback Plan:** Steps if activation fails:
- What gets reverted
- What flags reset
- Who gets notified
- What deferrals trigger (e.g., phase exit delayed)

## Special validation for Tier L

Switch to checklist:
- [ ] YAML frontmatter parseable, including cross_repo / rollout / activation sections if applicable
- [ ] All file paths resolve across all affected repos
- [ ] Cross-repo dependencies acyclic
- [ ] Activation criteria all quantitative (not "system should be OK")
- [ ] Rollout plan reversible (each stage has a rollback)
- [ ] Gates include `integration-pass` and `activation-criteria-met`
- [ ] Governor review pending (Tier L manifests MUST be reviewed before block start)

## Governor review

Tier L manifests are gated by Governor review:
1. Implementer (or whoever wrote the manifest) saves it with `status: pending`.
2. Governor reads, validates structure + cross-repo coherence + activation criteria realism.
3. Governor either approves (no edits) or returns with required changes.
4. Only after Governor approval does implementer start the block.

If no Governor agent active, treat user as Governor for approval step.

## Output

Save to `manifests/block-<NNN>-<slug>.md`. Notify Governor for review.

## Activation block pattern

For activation blocks specifically:
- Pre-block: code lands at lowest stage (e.g., Disabled)
- Bench stage: run benchmarks, gate by criteria
- Soak stage: long-running test, gate by criteria
- Default stage: flag flipped to default-on; block status → `done`

Each stage is its own audit event. Audit captures stage transition + criteria results.

End of manifest-large-generation protocol.
