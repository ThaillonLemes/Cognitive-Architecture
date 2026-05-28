---
id: block-108
tier: M
kind: implementation
phase: phase-17
scope: phase-bound
status: pending
security: false
dependencies: [block-095, block-097]
files:
  read:
    - protocols/brainstorm-pattern.md
    - sdk/pattern_analyzer.py
    - sdk/recommendation_engine.py
    - design/arch-v3.md
    - decisions/ADR-001-structure-option-a.md
  modify: []
  create:
    - sdk/brainstorm_context.py
    - sdk/tests/test_brainstorm_context.py
    - sdk/brainstorm_context_schema.py
gates:
  - name: context-module
    type: file-changed
    paths: [sdk/brainstorm_context.py, sdk/brainstorm_context_schema.py]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_brainstorm_context.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-095, block-097]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-108-brainstorm-context.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 108 — Brainstorm context loader

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Build the context bundler that, given a brainstorm topic, gathers the relevant retros, patterns, recommendations, ADRs, and state files. Topic-based relevance per Q14. Foundation for prediction engine (block-109).

## 2. Dependencies

- block-095 (patterns to consume)
- block-097 (recommendations to consume)

## 3. Files

- **Read:** brainstorm-pattern protocol, pattern_analyzer, recommendation_engine, arch-v3, example ADRs
- **Modify:** —
- **Create:** `sdk/brainstorm_context.py`, test file, `sdk/brainstorm_context_schema.py`

## 4. Validation

- Context loader exposes: `load_context(topic: str) -> ContextBundle`
- ContextBundle includes: relevant_retros[], applicable_patterns[], recommendations[], related_adrs[], state_snapshot
- Relevance heuristic: keyword match against retro slugs, pattern names, ADR titles; weighted by recency
- Test suite covers: known topic with rich context, novel topic with sparse context, multi-keyword topic

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Relevance heuristic picks wrong content | Med | User can override context selection (config option); test corpus validates against ground truth |
| Context bundle too large for LLM context window | Med | Hard cap on bundle size; truncate with priority by recency × relevance |

## 7. Out of Scope

- Semantic embedding (keyword + recency heuristic sufficient for v1)
- Cross-project context (single-project)
- ML training on prior brainstorms (deterministic heuristic)

## 8. New Abstraction

`ContextBundle` dataclass + loader. Justification: consumed by prediction engine (block-109), synthesis automation (block-111), potentially dashboard. Past Rule of Three.
