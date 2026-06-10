---
id: block-178
size: M
importance: normal
kind: implementation
phase: phase-33
scope: phase-bound
status: pending
wip_stage: ~
paused_reason: ~
security: false
dependencies:
  - block-177
files:
  read:
    - sdk/calendar_manager.py
    - sdk/notification_manager.py
    - sdk/session_start.py
  modify:
    - sdk/calendar_manager.py
    - sdk/session_start.py
    - sdk/tests/test_calendar_manager.py
  create:
    - sdk/tests/test_calendar_notifications.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-178-calendar-meeting-notifications.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: python -m pytest sdk/tests/test_calendar_manager.py sdk/tests/test_calendar_notifications.py -v
    expect: "0 failed"
  - name: meeting-notification-aparece
    type: manual
    checklist:
      - "Com uma reunião cadastrada para hoje, session_start mostra notificação com horas restantes"
      - "Com reunião em < 10min, session_start emite aviso soft-block: 'reunião em Xmin — continuar?'"
created_at: 2026-06-01
---

# Block 178 — Calendar → Notification: reuniões do dia sempre aparecem

- **Size:** M | **Importance:** normal | **Kind:** implementation
- **Status:** pending

## 1. Purpose

Integrar `calendar_manager.py` com o sistema de notificações para que reuniões do dia sempre apareçam no session_start com horas restantes, e reuniões em < 10min gerem soft-block antes de qualquer pedido.

## 2. Dependencies

`block-177` (session_start cria notificações — base necessária para esta integração)

## 3. Files

- **Read:** `sdk/calendar_manager.py`, `sdk/notification_manager.py`, `sdk/session_start.py`
- **Modify:** `sdk/calendar_manager.py` — adicionar `get_today_meetings(arch_root)` se não existir; `sdk/session_start.py` — chamar calendar check e criar notificações de reunião
- **Create:** `sdk/tests/test_calendar_notifications.py`

## 4. Regras de surfacing (Q3 do brainstorm)

| Situação | Comportamento |
|----------|--------------|
| Reunião cadastrada no dia | Sempre aparece no session_start com "reunião em Xh Ymin" |
| Reunião em ≤ 5h | Notificação `high` com contagem regressiva |
| Reunião em ≤ 10min | Soft-block: "⚠️ reunião em Xmin — você realmente quer iniciar isso?" |
| Reunião passou | Não notificar (passado) |

## 5. Validation

- Testes: `python -m pytest sdk/tests/test_calendar_manager.py sdk/tests/test_calendar_notifications.py -v` → 0 failed
- Com reunião hoje: session_start mostra notificação com horas restantes
- Com reunião em < 10min: soft-block aparece

## 6. Out of Scope

- Sincronização com Google Calendar / Outlook → futura fase
- Surfacing em triggers além de session_start → block-179
