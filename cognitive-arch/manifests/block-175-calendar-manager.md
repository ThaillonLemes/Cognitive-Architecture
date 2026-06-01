---
id: block-175
size: M
importance: normal
kind: implementation
phase: phase-32
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies:
  - block-173
parallel_with:
  - block-174
files:
  read:
    - design/forecast-calendar.md
    - sdk/session_start.py
    - governance/ux-config.yaml
  modify:
    - sdk/session_start.py
    - governance/tools-registry.yaml
  create:
    - sdk/calendar_manager.py
    - governance/pilot-calendar.yaml
    - sdk/tests/test_calendar_manager.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-175-calendar-manager.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_calendar_manager.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 2
finished_at: 2026-06-01T08:58Z
actual_duration_hours: 0.0
---

# Block 175 — Calendar Manager: YAML + Alertas de Reunião

- **Size:** M | **Importance:** normal
- **Kind:** implementation
- **Status:** pending
- **Mode:** shared (MMORPG + corporativo)

## 1. Purpose

Gerencia `governance/pilot-calendar.yaml` e injeta alertas de reunião nas sessões.
Piloto dita reuniões em linguagem natural → AI atualiza o YAML. Reuniões recorrentes
suportadas. Mesmo dia: alerta em toda sessão com countdown. Dias futuros: só no session_start.

## 2. Dependencies

- block-173 (velocity_tracker implementado; session_start.py estrutura atualizada)

## 3. Files

- **Read:** `design/forecast-calendar.md`, `sdk/session_start.py`, `governance/ux-config.yaml`
- **Modify:**
  - `sdk/session_start.py` — integrar leitura do calendar; exibir alertas de reunião no briefing
  - `governance/tools-registry.yaml`
- **Create:**
  - `sdk/calendar_manager.py` — CLI `--add-meeting`/`--list`/`--remove`; suporte a recorrência; lógica de alerta
  - `governance/pilot-calendar.yaml` — arquivo inicial vazio (schema definido)
  - `sdk/tests/test_calendar_manager.py`

## 4. Validation

- `pytest sdk/tests/test_calendar_manager.py -v` → 0 failed
- `python sdk/calendar_manager.py --add-meeting "2026-06-02 14:00 2h sync semanal"` → entrada no YAML
- `recurring: weekly` → mesma reunião aparece nas semanas seguintes sem re-cadastro
- Mesmo dia de reunião às 14h → session_start às 9h exibe "⚠️ Reunião em 5h00 — sync semanal"
- Dia seguinte → session_start exibe "Amanhã: reunião às 14h"
- Forecast HTML (block-174) lê o YAML e ajusta estimativa de entrega

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Alerta em toda sessão no mesmo dia vira ruído | Low | Formatado como linha única no topo; Piloto desliga via `ux-config.yaml: meeting_alerts: false` |
| Reunião recorrente com datas erradas por DST/fuso | Low | Armazenar em UTC; exibir no horário local da máquina |

## 7. Out of Scope

- Integração com Google Calendar / Outlook
- Notificações push fora da sessão
- Gerenciamento de agenda além de reuniões (tarefas, deadlines pessoais)

## 8. New Abstraction

**`MeetingCalendar`** (em `calendar_manager.py`): lê `pilot-calendar.yaml`, expande recorrências
para as próximas N semanas, e retorna reuniões para uma data específica. Consumida pelo
`session_start.py` e pelo `forecast_engine.py` (block-174).
