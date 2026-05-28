---
id: block-097
tier: M
kind: implementation
phase: phase-14
scope: phase-bound
status: pending
security: false
dependencies: [block-095]
files:
  read:
    - sdk/pattern_analyzer.py
    - sdk/pattern_schema.py
    - sdk/patterns_report.py
    - design/arch-v3.md
  modify:
    - sdk/patterns_report.py
  create:
    - sdk/recommendation_engine.py
    - sdk/recommendation_schema.py
    - sdk/tests/test_recommendation_engine.py
gates:
  - name: engine-module
    type: file-changed
    paths: [sdk/recommendation_engine.py, sdk/recommendation_schema.py]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_recommendation_engine.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-095]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-097-recommendation-engine.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 097 — Recommendation engine

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

For each detected Pattern, generate an actionable Recommendation. Recommendations are surfaced in patterns.md (modified to include a "Recommendations" section) and exported as input for Master Agent (Phase 15). Per D5, recommendations NEVER auto-create blocks — always human-decided.

## 2. Dependencies

- block-095 (Pattern records required as input)

## 3. Files

- **Read:** pattern_analyzer, pattern_schema, patterns_report (will be modified), arch-v3
- **Modify:** `sdk/patterns_report.py` (add Recommendations section to markdown output)
- **Create:** `sdk/recommendation_engine.py` (mapping rules pattern→recommendation), `sdk/recommendation_schema.py`, test file

## 4. Validation

- For each pattern type from block-095, at least one recommendation rule exists
- Recommendations include: title, rationale (citing evidence), priority (high/med/low), suggested next step (e.g., "create block-XXX to enforce X")
- Test suite covers all pattern→recommendation mappings
- patterns.md now has Recommendations section populated

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Recommendations too generic to act on | Med | Each rule requires specific actionable wording; review against test set |
| User feels nagged by recommendations | Med | Severity bands; only high-priority surfaced by Master proactively |

## 7. Out of Scope

- Auto-creation of blocks from recommendations (explicit human choice per D5)
- ML-generated recommendation text (deterministic mapping)
- Cross-project recommendations

## 8. New Abstraction

`Recommendation` dataclass. Justification: consumed by patterns_report, master_agent (Phase 15), potentially dashboard (Phase 16) — clear Rule of Three.
