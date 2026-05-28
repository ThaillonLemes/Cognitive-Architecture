---
id: block-107
tier: M
kind: implementation
phase: phase-16
scope: phase-bound
status: pending
security: false
dependencies: [block-098]
files:
  read:
    - blocks/BLOCK_LOG.md
    - board.md
    - STATE.md
    - agents/agent-master.md
    - design/arch-v3.md
  modify:
    - board.md
  create:
    - sdk/dependency_resolver.py
    - sdk/tests/test_dependency_resolver.py
    - protocols/dependency-resolution.md
gates:
  - name: resolver-module
    type: file-changed
    paths: [sdk/dependency_resolver.py, protocols/dependency-resolution.md]
  - name: tests-pass
    cmd: cd sdk && python -m pytest tests/test_dependency_resolver.py
    expect: "passed"
  - name: dependencies-met
    type: deps-complete
    deps: [block-098]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-107-dependency-resolution.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 107 — Dependency resolution automation

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

When a block closes (BLOCK_LOG append), scan pending manifests for any whose `dependencies:` are now fully satisfied. Move their state from `wait` to `pending` and notify the user via Master (per D7). Eliminates the manual check after every close.

## 2. Dependencies

- block-098 (Master Agent role exists; resolver is one of its tools)

## 3. Files

- **Read:** BLOCK_LOG, board.md, STATE.md, Master role, arch-v3
- **Modify:** board.md (resolver updates state of unblocked items)
- **Create:** `sdk/dependency_resolver.py`, test file, `protocols/dependency-resolution.md`

## 4. Validation

- On block close, resolver:
  1. Reads all `manifests/*.md` for pending/wait blocks
  2. Checks `dependencies:` field of each
  3. Verifies all listed deps appear `done` in BLOCK_LOG
  4. Updates board.md row from `wait` → `pending` for satisfied blocks
  5. Outputs notification list to Master Agent
- Test suite covers: no unblocks, single unblock, multiple unblocks, partial dep satisfied (no unblock)
- Notification list format matches AgentMessage schema from block-102 (kind: notification)

## 5. Gates

Per frontmatter.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Resolver updates board.md while user holds lock | Med | Check lock state before write; defer if held |
| Wrong unblock (transitive dep missed) | Low | Tests cover transitive cases; conservative approach |
| Notification fatigue | Low | One notification per close, batched |

## 7. Out of Scope

- Cross-repo dependency resolution (MMORPG-specific concern; not cognitive-arch)
- Auto-start of unblocked blocks (always user-initiated)
- Dependency visualization (Phase 16 dashboard shows it)

## 8. New Abstraction

`DependencyResolver` module. Justification: consumed by Master Agent, by audit checks (future), potentially by dashboard. Rule of Three met.
