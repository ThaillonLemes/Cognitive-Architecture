---
id: block-165
size: S
importance: normal
kind: implementation
phase: phase-29
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies:
  - block-163
  - block-164
files:
  read:
    - design/block-phase-redesign.md
    - design/corporate-mode.md
    - templates/manifest-intake.md
  modify:
    - governance/tools-registry.yaml
  create:
    - sdk/ticket_intake.py
    - sdk/tests/test_ticket_intake.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-165-ticket-intake.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_ticket_intake.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 1.5
---

# Block 165 — Ticket Intake

- **Size:** S | **Importance:** normal
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Implementa `sdk/ticket_intake.py`: converte texto livre de ticket em manifest de bloco
corporativo (`kind: ticket`) com campos obrigatórios preenchidos. É o ponto de entrada
do fluxo corporativo — `TICKET → intake → manifest → revisão do Piloto → ticket block`.

## 2. Dependencies

- block-163 (phase infrastructure — `client_id` disponível na fase)
- block-164 (block infrastructure — novos campos de bloco no SDK)

## 3. Files

- **Read:** `design/block-phase-redesign.md §1.7`, `design/corporate-mode.md §3.3`, `templates/manifest-intake.md`
- **Modify:** `governance/tools-registry.yaml` (registrar novo tool)
- **Create:**
  - `sdk/ticket_intake.py` — CLI: `--ticket <text> --client <nome> --arch-root <path>`
  - `sdk/tests/test_ticket_intake.py`

## 4. Validation

- `pytest sdk/tests/test_ticket_intake.py -v` → 0 failed
- `python sdk/ticket_intake.py --ticket "implementar refresh de JWT" --client visagio --arch-root .`
  → gera manifest com `kind: ticket`, `ticket_id: to-define`, `acceptance_criteria` preenchido, `reviewer: to-define`, `client_id: visagio`
- Intake é sempre `size: XS` e nunca modifica código do cliente
- Manifest gerado em `manifests/block-<next-id>-<slug>.md`

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Geração de `acceptance_criteria` muito vaga para tickets mal escritos | Low | Intake marca campos incompletos com `# NEEDS_REVIEW`; Piloto preenche antes de aprovar |
| Numbering automático de bloco colide com blocos existentes | Med | Intake lê BLOCK_LOG.md para pegar o próximo número disponível |

## 7. Out of Scope

- Scanner L2/L3 da área do ticket (será chamado depois pelo Piloto manualmente ou pelo pipeline — phase-31)
- Integração com Jira/Linear API
- Auto-aprovação do manifest gerado (Piloto sempre revisa antes de executar)

## 8. New Abstraction

None. `ticket_intake.py` é um script CLI simples — lê texto, gera markdown.
Sem nova classe/trait que outros módulos precisem importar.
