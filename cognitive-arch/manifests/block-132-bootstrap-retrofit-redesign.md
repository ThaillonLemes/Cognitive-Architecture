---
id: block-132
tier: M
kind: refactor
phase: phase-22
scope: phase-bound
status: planned
security: false
dependencies:
  - block-130
files:
  read:
    - BOOTSTRAP.md
    - RETROFIT.md
    - CLAUDE.md
    - PROTOCOLS.md
    - sdk/session_start.py
    - sdk/block_start.py
    - sdk/block_close.py
    - sdk/phase_manager.py
  modify:
    - BOOTSTRAP.md
    - RETROFIT.md
  create:
    - BOOTSTRAP-v1.md
    - RETROFIT-v1.md
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-132-bootstrap-retrofit-redesign.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-130]
created_at: 2026-05-28
parallel_with: [block-131, block-133]
---

# Block 132 — BOOTSTRAP + RETROFIT Redesign

- **Tier:** M
- **Kind:** refactor
- **Status:** planned
- **Parallel-with:** block-131, block-133

## 1. Purpose

Redesign BOOTSTRAP.md and RETROFIT.md from scratch using 22 phases of accumulated learning. Archive originals as BOOTSTRAP-v1.md and RETROFIT-v1.md. Updated flows must: reference session_start.py as mandatory first step; replace all manual board/STATE/NEXT edits with SDK tool references (block_start.py, block_close.py, phase_manager.py, governor.py); remove obsolete manual steps; add governor/notifications awareness; update to governance/ux-voice.md tone.

## 2. Dependencies

- block-130: ux-voice.md must exist (redesign follows its tone rules)

## 3. Files

- **Read:** BOOTSTRAP.md, RETROFIT.md (originals to understand), CLAUDE.md, PROTOCOLS.md, sdk/session_start.py, sdk/block_start.py, sdk/block_close.py, sdk/phase_manager.py
- **Modify:** BOOTSTRAP.md (full rewrite), RETROFIT.md (full rewrite)
- **Create:** BOOTSTRAP-v1.md (archive of original), RETROFIT-v1.md (archive of original)

## 4. Validation

- Read through new BOOTSTRAP.md flow end-to-end — confirm no step references manual file editing that SDK tools now handle
- Read through new RETROFIT.md flow end-to-end — same check
- Both files reference session_start.py in first step
- Both files reference governor.py for notifications
- BOOTSTRAP-v1.md and RETROFIT-v1.md exist with original content preserved
- Confirm no working flow was removed (only manual-to-SDK substitutions)

## 5. Gates

- files-updated (no test gate — documentation refactor)
- dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Redesign removes a step that an edge case still needs | Med | Archive v1 files for 1 phase; migration note at top of new files pointing to v1 |
| BOOTSTRAP.md changes break CLAUDE.md routing | Low | CLAUDE.md references BOOTSTRAP.md by name only; internal structure change is safe |

## 7. Out of Scope

- Automated BOOTSTRAP flow execution (human-guided only)
- BOOTSTRAP for non-Python projects (generic template future phase)
- Video/interactive documentation

## 8. New Abstraction

None. Documentation refactor only.
