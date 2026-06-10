---
id: block-177
size: S
importance: normal
kind: implementation
phase: phase-33
scope: phase-bound
status: pending
wip_stage: ~
paused_reason: ~
security: false
dependencies:
  - block-176
files:
  read:
    - sdk/session_start.py
    - sdk/notification_manager.py
    - sdk/invariant_check.py
    - sdk/audit.py
    - sdk/health_report.py
  modify:
    - sdk/session_start.py
    - sdk/tests/test_session_start.py
  create: []
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-177-session-start-cria-notificacoes.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: python -m pytest sdk/tests/test_session_start.py -v
    expect: "0 failed"
  - name: fila-nao-vazia
    type: manual
    checklist:
      - "Após rodar session_start, python sdk/notification_manager.py list mostra pelo menos 1 notificação quando há warnings/degradação"
created_at: 2026-06-01
---

# Block 177 — session_start cria notificações a partir das ferramentas

- **Size:** S | **Importance:** normal | **Kind:** implementation
- **Status:** pending

## 1. Purpose

Fazer `session_start.py` criar entradas em `notification_manager` quando detecta problemas — audit degradado, invariant warnings, health score baixo — para que a fila nunca fique vazia quando há algo relevante.

## 2. Dependencies

`block-176` (INV3 fix — sem ele, invariant_check gera falsos positivos que poluiriam as notificações)

## 3. Files

- **Read:** `sdk/session_start.py`, `sdk/notification_manager.py`, `sdk/invariant_check.py`, `sdk/audit.py`, `sdk/health_report.py`
- **Modify:** `sdk/session_start.py` — após cada ferramenta, criar notificação se threshold atingido; `sdk/tests/test_session_start.py` — testar criação de notificações

## 4. Regras de criação (Q2 do brainstorm)

| Evento | Threshold | Prioridade | Tipo |
|--------|-----------|-----------|------|
| audit_score | < 80 | high | health |
| audit_score | < 60 | critical | health |
| invariant critical | ≥ 1 | critical | health |
| invariant warn | ≥ 1 | high (consolidado — 1 notif por tipo, não por bloco) | health |
| health_score | < 75 | high | health |
| health_score | < 60 | critical | health |
| pattern ativo > 7 dias | ≥ 1 | medium | pattern |

## 5. Validation

- `python -m pytest sdk/tests/test_session_start.py -v` → 0 failed
- Fila não fica vazia quando há degradação detectada pelas ferramentas

## 6. Out of Scope

- Integração com calendar/reuniões → block-178
- Surfacing por trigger (phase close, block close) → block-179
