---
id: block-130
tier: S
kind: doc-only
phase: phase-22
status: planned
security: false
files:
  read:
    - PROTOCOLS.md
    - CLAUDE.md
    - sdk/session_start.py
  modify: []
  create:
    - governance/ux-voice.md
    - governance/ux-config.yaml
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: 2026-05-28
---

# Block 130 — governance/ux-voice.md

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Create governance/ux-voice.md: the AI communication tone guide. Defines: (1) tone rules — direct, specific, no filler words; (2) response format standards — when to use headers vs prose vs tables vs code blocks; (3) prohibited patterns — list of patterns like "I'll now...", "Certainly!", "As an AI...", "I hope this helps"; (4) ≥5 positive/negative examples side by side; (5) session_start.py specific rules (what must always appear, what must never appear). Create governance/ux-config.yaml for configuration (dashboard link protocol, etc.).

## 2. Dependencies

None (first block of phase-22; foundation for block-134).

## 3. Files

- **Read:** PROTOCOLS.md (tone axioms if any), CLAUDE.md (existing AI entry instructions), sdk/session_start.py (output format reference)
- **Modify:** None
- **Create:** governance/ux-voice.md, governance/ux-config.yaml

## 4. Validation

- governance/ux-voice.md exists with all 4 sections documented
- ≥5 positive/negative example pairs present
- governance/ux-config.yaml has: dashboard_link_protocol (file|vscode), default: file
- Content is specific and actionable — not vague guidelines

## 5. Gates

- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md changed

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Voice guide is too restrictive, stifles useful output | Low | Rules are guidelines; ux_validator produces WARNs not errors; user can update ux-voice.md freely |

## 7. Out of Scope

- Enforcing ux-voice.md on all AI output (ux_validator.py in block-134 handles that)
- Voice rules for non-English output

## 8. New Abstraction

None. Governance documentation file only.
