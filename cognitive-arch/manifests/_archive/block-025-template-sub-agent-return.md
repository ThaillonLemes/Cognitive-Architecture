---
id: block-025
tier: S
kind: doc-only
phase: phase-4
status: planned
dependencies: [block-017]
files:
  read:
    - design/governor-v2.md
    - protocols/sub-agent-contract.md
    - _syntax.md
  modify: []
  create:
    - templates/sub-agent-return.md
gates:
  - name: template-exists
    type: file-exists
    paths: [templates/sub-agent-return.md]
  - name: all-status-variants
    type: manual
    description: template shows examples for all 4 status values (done, blocked, scope-exceeded, partial)
  - name: required-fields
    type: manual
    description: template has all required return-package fields as placeholders
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 025 — Template: sub-agent-return

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Dependencies:** block-017

## 1. Purpose

Create `templates/sub-agent-return.md` — the fill-in-the-blank template for sub-agents to emit their return package at the end of block execution. Ensures consistent return package format so the Governor can reliably parse every return.

## 2. Files

- **Read:** design/governor-v2.md (Section 4), protocols/sub-agent-contract.md, _syntax.md
- **Modify:** none
- **Create:** templates/sub-agent-return.md

## 3. Spec

`templates/sub-agent-return.md` content:

```markdown
# Return package — Block NNN

<!-- Emit this as the FINAL message of your sub-agent session -->
<!-- One return package only — do not send intermediate updates -->
<!-- Remove comments before sending -->

b:NNN sid:s-SESSIONHASH status:STATUS ts:TIMESTAMP
gates:GATE-NAME:PASS|FAIL,GATE-NAME:PASS|FAIL
fmod:FILE:LINES_CHANGED,FILE:LINES_CHANGED
fread:FILE,FILE,...
scope_exp:no              <!-- no | yes | brief description of what was discovered -->
issues:none               <!-- none | brief description of any problems encountered -->
retro:yes retro_path:blocks/block-NNN-SLUG.md
tok_in:~NNN tok_out:~NNN tok_src:estimated

---
## Examples

### Successful block:
b:018 sid:s-abc123 status:done ts:2026-05-21T11:30Z
gates:protocol-exists:PASS,format-spec-complete:PASS,references-syntax:PASS,files-updated:PASS
fmod:protocols/task-packet.md:87 fread:design/governor-v2.md,_syntax.md
scope_exp:no issues:none
retro:yes retro_path:blocks/block-018-protocol-task-packet.md
tok_in:~1200 tok_out:~450 tok_src:estimated

### Blocked block:
b:020 sid:s-def456 status:blocked ts:2026-05-21T11:45Z
gates:protocol-exists:FAIL
fmod: fread:design/governor-v2.md,PROTOCOLS.md,_syntax.md
scope_exp:no issues:PROTOCOLS.md axiom table format differs from brainstorm — need clarification on P5/P6 scope
retro:no
tok_in:~800 tok_out:~120 tok_src:estimated

### Scope exceeded:
b:019 sid:s-ghi789 status:done ts:2026-05-21T12:00Z
gates:protocol-exists:PASS,return-package-spec:PASS,lifecycle-defined:PASS,files-updated:PASS
fmod:protocols/sub-agent-contract.md:112 fread:design/governor-v2.md,_syntax.md,protocols/block-close-checklist.md
scope_exp:yes discovered need for explicit timeout handling section — added minimal note; full spec deferred
issues:none
retro:yes retro_path:blocks/block-019-sub-agent-contract.md
tok_in:~1400 tok_out:~550 tok_src:estimated
```

### Usage instructions (in the template file):
1. Emit this as your LAST message — nothing after it
2. Fill in all fields
3. `sid:` = first 6 chars of session hash (any unique identifier if hash unavailable)
4. `fmod:` = comma-separated FILE:LINES pairs for every file you changed
5. `tok_in:` / `tok_out:` = use ~NNN format; chars/4 estimate acceptable

## 4. Out of scope

- Task packet template (→ block-024)
- Return package parsing logic (Governor responsibility)
