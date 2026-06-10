---
id: block-176
size: XS
importance: normal
kind: intake
phase: phase-32
scope: phase-bound
status: pending
wip_stage: ~
paused_reason: ~
security: false
dependencies: []
# [corporate fields — required when kind is promoted to ticket]
ticket_id: to-define-176   # NEEDS_REVIEW — set actual ticket ID
acceptance_criteria:
  - "Acceptance Criteria:"
reviewer: ~   # NEEDS_REVIEW — set reviewer name
client_id: plane
files:
  read:
    - governance/project-profile-plane.md   # scan profile for context
  modify: []
  create: []   # intake never modifies client code
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-176-adicionar-filtro-de-issues-por-assignee.md]
  - name: scope-clean
    type: fmod-check
created_at: 2026-06-01
---

# Block 176 — Intake: Adicionar filtro de issues por assignee no board view do pro...

- **Size:** XS | **Importance:** normal
- **Kind:** intake (→ will become ticket block after Piloto review)
- **Client:** plane
- **Status:** pending

## 1. Purpose

Ticket intake para: "Adicionar filtro de issues por assignee no board view do projeto.
Atualmente o board Kanban mostra todas as issues indep"

## 2. Acceptance Criteria (NEEDS_REVIEW)

- Acceptance Criteria:

## 3. Next Step

Piloto revisa este manifest, preenche campos marcados com `# NEEDS_REVIEW`,
promove kind para `ticket`, e executa block-start.

## 4. Out of Scope

- Implementação de qualquer código de cliente neste bloco (intake = só leitura + geração de manifest)
