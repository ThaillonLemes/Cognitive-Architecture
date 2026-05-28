---
id: block-125
tier: M
kind: implementation
phase: phase-20
scope: phase-bound
status: planned
security: false
dependencies:
  - block-123
  - block-124
files:
  read:
    - governance/proposals/
    - governance/proposals/index.md
    - PROTOCOLS.md
  modify:
    - governance/proposals/index.md
  create:
    - sdk/proposal_resolver.py
    - sdk/tests/test_proposal_resolver.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: lint-pass
    cmd: python -m flake8 sdk/proposal_resolver.py --max-line-length=120
    expect: "0 errors"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-125-proposal-resolver.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-123, block-124]
created_at: 2026-05-28
---

# Block 125 — proposal_resolver.py

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Build sdk/proposal_resolver.py: accept or reject proposals by ID. `--accept <id>` sets status:accepted in the proposal file and index. `--accept <id> --apply` additionally patches the target_file (creates .bak, checks if target is immutable before writing, aborts if immutable). `--reject <id> --note "..."` sets status:rejected with an optional note. All operations update governance/proposals/index.md.

## 2. Dependencies

- block-123 + block-124: session and dashboard integration means proposals are visible and users will act on them

## 3. Files

- **Read:** governance/proposals/ (individual proposal files), governance/proposals/index.md, PROTOCOLS.md (immutability check)
- **Modify:** governance/proposals/index.md (status updates)
- **Create:** sdk/proposal_resolver.py, sdk/tests/test_proposal_resolver.py

## 4. Validation

- `python sdk/proposal_resolver.py --accept <id>` — proposal status updated to accepted in file + index
- `python sdk/proposal_resolver.py --accept <id> --apply` — target_file patched; .bak created
- `python sdk/proposal_resolver.py --accept <id> --apply` on immutable target — abort with clear message
- `python sdk/proposal_resolver.py --reject <id> --note "..."` — proposal status rejected + note recorded
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, lint-pass, files-updated, dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| --apply corrupts target file | High | Always creates .bak first; dry-run default; write only with --apply |
| Proposal references non-existent target_file | Med | resolver checks file exists before patching; aborts with clear error |
| Concurrent resolver runs | Low | File-level lock on index.md during write |

## 7. Out of Scope

- Batch accept/reject
- Proposal merging (combining two proposals into one)
- Auto-apply without --apply flag (never)

## 8. New Abstraction

`ProposalResolver.accept(proposal_id, arch_root, apply=False)` and `ProposalResolver.reject(proposal_id, arch_root, note="")`. Both update the proposal file + index atomically.
