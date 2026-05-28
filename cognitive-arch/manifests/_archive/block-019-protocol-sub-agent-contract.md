---
id: block-019
tier: S
kind: doc-only
phase: phase-4
status: planned
dependencies: [block-017]
files:
  read:
    - design/governor-v2.md
    - _syntax.md
    - protocols/block-close-checklist.md
  modify: []
  create:
    - protocols/sub-agent-contract.md
gates:
  - name: protocol-exists
    type: file-exists
    paths: [protocols/sub-agent-contract.md]
  - name: return-package-spec
    type: manual
    description: protocol defines the exact return package format (key:value) including all required and optional fields
  - name: lifecycle-defined
    type: manual
    description: protocol describes the full sub-agent lifecycle (receive packet → read files → execute block → write retro → emit return)
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 019 — Protocol: sub-agent-contract

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Dependencies:** block-017

## 1. Purpose

Create `protocols/sub-agent-contract.md` — the specification that defines what a sub-agent is obligated to do when it receives a task packet. Covers the full sub-agent lifecycle and the return package format the Governor expects back.

## 2. Files

- **Read:** design/governor-v2.md (Sections 4, 6), _syntax.md, protocols/block-close-checklist.md
- **Modify:** none
- **Create:** protocols/sub-agent-contract.md

## 3. Spec

`protocols/sub-agent-contract.md` must cover:

### Sub-agent obligations
1. Read and parse the task packet (first message)
2. Read all files listed in `fread:` — no more, no less (scope discipline)
3. Execute the block as specified in the manifest
4. Follow `protocols/block-close-checklist.md` for close steps
5. Write retrospective if `retro_req:yes`
6. Emit a return package as the final message

### Return package format
```
b:NNN sid:s-HASH status:STATUS ts:ISO8601
gates:GATE-NAME:PASS|FAIL,...
fmod:FILE:NLINES,...
fread:FILE,...
scope_exp:yes|no|brief-description
issues:none|DESCRIPTION
retro:yes|no retro_path:PATH
tok_in:NNN tok_out:NNN tok_src:estimated|actual
```

### Status values
- `done` — block completed, all gates pass
- `blocked` — cannot proceed; issue in `issues:` field
- `scope-exceeded` — discovered work beyond manifest scope; `scope_exp:` field describes it
- `partial` — some gates pass, some fail; details in `gates:` field

### What the sub-agent must NOT do
- Read files not in `fread:` (unless strictly required by block and documented in `notes:`)
- Modify files not in `fmod:` (scope discipline)
- Commit to git (Governor owns commit unless explicitly delegated)
- Send multiple messages — the return package is ONE final message

### Failure escalation
If sub-agent cannot complete: emit return with `status:blocked issues:DESCRIPTION`
Governor decides: retry, skip, or halt phase.

## 4. Out of scope

- Governor-side logic (→ block-021 governor-dispatch)
- Convention snippet generation (→ block-020)
- Template for return packages (→ block-025)
