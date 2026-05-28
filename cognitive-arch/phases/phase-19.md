---
id: phase-19
status: planned
prev_phase: phase-18
exit_criteria_count: 4
blocks_count: 4
estimated_duration_days: 4
created_at: 2026-05-28
last_updated: 2026-05-28
owner: implementer
---

# Phase 19 — Auto-ADR

BRIEF: When brainstorm_synthesis.py produces a decision flagged as significant, automatically draft an ADR scaffold and save it to design/adrs/. Human fills in rationale; AI supplies context, options considered, and synthesis source. Saves ~800 tokens per ADR.

## 1. Purpose

ADRs (Architecture Decision Records) exist since Phase 12 but are created manually. The workflow is: brainstorm → synthesis → human writes ADR. Phase 19 automates the scaffold step: when brainstorm_synthesis.py detects a decision marked `significance: high` or `significance: medium`, it calls `sdk/adr_drafter.py` which generates a pre-filled ADR draft citing the synthesis source, the options considered, the AI's recommended option, and the confidence band. Human reviews, edits rationale, and saves. The manual ADR template (templates/ADR.md) remains unchanged — auto-generated ADRs use a separate template (templates/ADR-auto.md) and are stored in design/adrs/.

## 2. Goals

- sdk/adr_drafter.py generates valid ADR scaffold from brainstorm synthesis JSON output
- brainstorm_synthesis.py automatically triggers adr_drafter for significant decisions
- templates/ADR-auto.md: format for auto-generated ADRs (includes synthesis source, confidence band, options considered)
- governance/adrs/index.md maintained automatically; dashboard shows ADR count and last ADR date

## 3. Invariants

- Auto-generated ADRs always have status: draft — human must change to accepted/rejected
- The manual ADR.md template is never modified by automation
- adr_drafter.py never overwrites an existing ADR file; it creates with unique timestamp slug
- ADR index is append-only; adr_drafter.py never deletes index entries

## 4. Dependencies

- Phase 17 complete (brainstorm_synthesis.py exists and produces synthesis JSON)
- Phase 12 complete (templates/ADR.md exists; design/adrs/ directory convention established)
- sdk/brainstorm_synthesis.py accepts plugin hooks (or adr_drafter is called as post-step)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| adr_drafter generates low-quality drafts, human ignores them | Med | Draft quality gate: requires at minimum title, decision, options, synthesis_source populated |
| Brainstorm synthesis marks everything as significant | Low | Significance threshold configurable in brainstorm-pattern-v2.md; default medium+ |
| ADR index becomes stale if files are manually renamed | Low | Index rebuild command: `python sdk/adr_drafter.py --rebuild-index` |
| Auto ADR format diverges from manual ADR format over time | Low | Both templates share core fields; auto-specific fields are additive |

## 6. Validation

- Run a test brainstorm synthesis with significance:high decision — check design/adrs/ for new draft
- Run `python -m pytest sdk/tests/ -q` — 0 failures
- Verify governance/adrs/index.md has new entry
- Verify dashboard shows ADR count incremented

## 7. Exit Criteria

1. `sdk/adr_drafter.py` generates a valid ADR scaffold from brainstorm synthesis JSON; draft saved to `design/adrs/YYYY-MM-DD-<slug>.md`; file includes: title, status:draft, synthesis_source, options_considered, recommended_option, confidence_band, rationale placeholder.
2. `sdk/brainstorm_synthesis.py` automatically calls `adr_drafter.generate()` for decisions with `significance: high` or `significance: medium`; can be disabled via `--no-adr` flag.
3. `templates/ADR-auto.md` documents the auto-generated ADR format; distinct from `templates/ADR.md`; includes synthesis_source and confidence_band fields not present in manual ADR.
4. `governance/adrs/index.md` updated automatically on each draft creation; dashboard shows ADR count + date of last ADR.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-117 | adr_drafter.py core | M | planned | `manifests/block-117-adr-drafter.md` |
| block-118 | synthesis → adr trigger | S | planned | `manifests/block-118-synthesis-adr-trigger.md` |
| block-119 | ADR-auto.md template | S | planned | `manifests/block-119-adr-auto-template.md` |
| block-120 | ADR index + dashboard widget | M | planned | `manifests/block-120-adr-index-dashboard.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 1
  groups:
    - id: 19A
      blocks: [block-117, block-119]
      type: parallel
      depends_on: []
    - id: 19B
      blocks: [block-118]
      type: sequential
      depends_on: [19A]
    - id: 19C
      blocks: [block-120]
      type: sequential
      depends_on: [19B]
```

Drafter core and template can be built in parallel; trigger integration requires both; index/dashboard requires trigger working.

## 10. Out of Scope

- Auto-generating ADRs from sources other than brainstorm synthesis (retros, manual triggers — future phase)
- ADR versioning / superseding automation
- Publishing ADRs to external wiki or documentation site
- ML-based significance classification (heuristic threshold sufficient)

---

End of phase-19.
