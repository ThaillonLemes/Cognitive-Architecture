---
id: block-101
tier: M
kind: implementation
phase: phase-15
scope: phase-bound
status: pending
security: false
dependencies: [block-100, block-102]
files:
  read:
    - sdk/master_scheduler.py
    - agents/agent-master.md
    - governance/tools-registry.yaml
    - design/arch-v3.md
  modify:
    - agents/agent-master.md
  create:
    - protocols/master-active-suggestion.md
    - sdk/master_suggest.py
    - sdk/tests/test_master_suggest.py
gates:
  - name: protocol-and-module
    type: file-changed
    paths: [protocols/master-active-suggestion.md, sdk/master_suggest.py]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_master_suggest.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-100, block-102]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-101-active-suggestion.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 101 — Active suggestion protocol

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Define WHEN and HOW the Master surfaces stale tools or recommendations to the user. Three triggers: session-start briefing (always if stale items exist), inline with block-start (only if tool is relevant to that block), on explicit status request. Implements the hybrid proactive+reactive posture per Q5.

## 2. Dependencies

- block-100 (need scheduler output to know what's stale)
- block-102 (need inter-agent message format to communicate suggestions)

## 3. Files

- **Read:** master_scheduler, Master role, tools-registry, arch-v3
- **Modify:** `agents/agent-master.md` (add active-suggestion section)
- **Create:** `protocols/master-active-suggestion.md` (behavior doc), `sdk/master_suggest.py` (logic), test file

## 4. Validation

- Protocol doc covers 3 trigger types with explicit examples
- Module exposes: `suggest_at_session_start() -> list[Suggestion]`, `suggest_inline(block_id) -> list[Suggestion]`, `suggest_on_demand() -> list[Suggestion]`
- Each Suggestion has: tool, urgency, message (template-rendered), action_button_label
- Test suite covers all 3 triggers with mock registry states

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Suggestions too noisy at session-start | High | Only show urgency >= overdue; user can mute per-tool via registry flag |
| Inline suggestions disrupt block flow | Med | Limited to direct relevance to active block; max 2 inline suggestions per block-start |
| Confusing what "relevant" means | Med | Heuristic documented: tools mentioned in active block's manifest files.read |

## 7. Out of Scope

- Push notifications (this is text-in-conversation only)
- Auto-execution of stale tools (always user-initiated)
- Cross-project suggestions

## 8. New Abstraction

`Suggestion` dataclass. Justification: used in 3 contexts (session-start, inline, on-demand); also consumed by Phase 16 dashboard. Past Rule of Three.
