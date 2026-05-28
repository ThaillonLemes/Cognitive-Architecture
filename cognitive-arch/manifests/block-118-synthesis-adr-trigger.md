---
id: block-118
tier: S
kind: small-fix
phase: phase-19
status: planned
security: false
files:
  read:
    - sdk/brainstorm_synthesis.py
    - sdk/adr_drafter.py
  modify:
    - sdk/brainstorm_synthesis.py
  create: []
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
---

# Block 118 — synthesis → ADR Trigger

- **Tier:** S
- **Kind:** small-fix
- **Status:** planned

## 1. Purpose

Wire adr_drafter.py into brainstorm_synthesis.py as a post-synthesis step. After synthesis.py writes the design/<topic>.md file, it calls adr_drafter.generate() if any decisions have significance:high or significance:medium. Add --no-adr flag to synthesis.py to disable. Print count of ADR drafts created to stdout.

## 2. Dependencies

- block-117: adr_drafter.py must exist before wiring
- block-119: ADR-auto.md template must exist (adr_drafter.py needs it)

## 3. Files

- **Read:** sdk/brainstorm_synthesis.py, sdk/adr_drafter.py
- **Modify:** sdk/brainstorm_synthesis.py — add post-synthesis adr_drafter call + --no-adr flag
- **Create:** None

## 4. Validation

- Run brainstorm_synthesis.py on a synthesis with significant decisions — confirm ADR drafts created
- Run with --no-adr — confirm no ADR files created
- Run with no significant decisions — confirm no ADR files created, no error
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, files-updated

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| adr_drafter import failure breaks synthesis | Low | Import wrapped in try/except; synthesis never blocked by ADR failure |

## 7. Out of Scope

- Triggering ADR from sources other than synthesis

## 8. New Abstraction

None. Small wiring change to existing synthesis.py.
