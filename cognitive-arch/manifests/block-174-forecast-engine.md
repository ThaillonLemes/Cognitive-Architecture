---
id: block-174
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
  - block-175
files:
  read:
    - design/forecast-calendar.md
    - sdk/velocity_tracker.py
    - sdk/phase_forecast.py
    - governance/ux-config.yaml
  modify:
    - sdk/phase_forecast.py
    - governance/tools-registry.yaml
  create:
    - sdk/forecast_engine.py
    - sdk/tests/test_forecast_engine.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-174-forecast-engine.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_forecast_engine.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 2
finished_at: 2026-06-01T08:56Z
actual_duration_hours: 0.0
---

# Block 174 — Forecast Engine: HTML + Confidence + Paralelismo

- **Size:** M | **Importance:** normal
- **Kind:** implementation
- **Status:** pending
- **Mode:** shared (MMORPG + corporativo)

## 1. Purpose

Gera o HTML de forecast: velocity atual (tickets/dia + horas/ticket), estimativa de entrega
ajustada por reuniões do calendário, confidence band baseado em quantidade de histórico,
e sugestão de paralelismo quando métricas indicam capacidade. Reorienta `phase_forecast.py`
existente para usar dados reais de velocity.

## 2. Dependencies

- block-173 (`VelocityRecord` com dados reais de duração)

## 3. Files

- **Read:** `design/forecast-calendar.md`, `sdk/velocity_tracker.py`, `sdk/phase_forecast.py`
- **Modify:**
  - `sdk/phase_forecast.py` — reorientar para usar `actual_duration_hours` dos manifests; não reescrever
  - `governance/tools-registry.yaml` — registrar `forecast_engine`
- **Create:**
  - `sdk/forecast_engine.py` — HTML generator: velocity + estimativa + confidence + paralelismo
  - `sdk/tests/test_forecast_engine.py`

## 4. Validation

- `pytest sdk/tests/test_forecast_engine.py -v` → 0 failed
- Com 5 blocos de histórico → HTML gerado com confidence MÉDIO, velocity em tickets/dia E horas
- Com reunião no calendário do dia → estimativa ajustada (horas de reunião descontadas)
- Com < 3 blocos → HTML mostra "histórico insuficiente" em vez de forecast enganoso
- Sugestão de paralelismo aparece quando: 5+ blocos sem loopback + pipeline > 20min por etapa
- `phase_forecast.py` existente ainda funciona (não regride)

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Confidence BAIXO com poucos dados gera desconfiança | Low | Exibir "histórico insuficiente" explicitamente — melhor que esconder o forecast |
| Sugestão de paralelismo pode ser prematura | Low | É uma sugestão — Piloto confirma. Sem ação automática. |

## 7. Out of Scope

- Calendar manager (block-175 — forecast lê o YAML mas não o gerencia)
- Notificações push de forecast

## 8. New Abstraction

**`ForecastReport`**: dataclass com `velocity_tickets_per_day`, `velocity_hours_per_ticket`,
`estimated_days`, `adjusted_days` (com meetings), `confidence`, `parallelism_suggestion`.
Entrada para o HTML renderer do forecast.
