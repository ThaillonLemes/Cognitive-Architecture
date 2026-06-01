---
id: phase-32
status: planned
prev_phase: phase-31
exit_criteria_count: 6
blocks_count: 3
estimated_duration_minutes: 270
created_at: 2026-05-31
last_updated: 2026-05-31
owner: implementer
design_source: design/forecast-calendar.md
brainstorm_source: _brainstorm/forecast-tracks-v2-redesign.md
note: Tracks excluídas — gerenciadas por agente separado (agent:tracks)
phase_finished_at: 2026-06-01T08:58Z
phase_duration_hours: 0.0
---

# Phase 32 — Forecast, Velocidade & Calendário

BRIEF: Fecha o loop do modo corporativo com dados reais. Timestamps automáticos em blocos e
fases (ambos os modos), velocity calculada de verdade, forecast de entrega com impacto de
reuniões, sugestão de paralelismo baseada em métricas, e alertas de reunião persistentes
no dia da reunião. Tracks ficam com o agente de tracks.

## 1. Purpose

Com as Phases 29–31 o Piloto entrega tickets com qualidade. Com a Phase 32 ele sabe:
- Quanto tempo cada bloco/fase realmente levou
- Quando vai terminar o lote de tickets abertos
- Quando tem reunião e quanto isso impacta o dia
- Se está pronto para abrir um segundo ticket em paralelo

Tudo isso com dados reais capturados automaticamente — não estimativas manuais.

## 2. Goals

- `sdk/velocity_tracker.py`: registra `started_at`, `paused_at`, `resumed_at`, `finished_at` nos manifests; calcula `actual_duration_hours` descontando pausas; adiciona timestamps de fase em `phase_manager.py`
- `sdk/forecast_engine.py`: lê velocity history + calendar; gera HTML de forecast com velocity em tickets/dia + horas, estimativa ajustada por reuniões, confidence band, sugestão de paralelismo
- `sdk/calendar_manager.py`: gerencia `governance/pilot-calendar.yaml` via linguagem natural; suporta reuniões recorrentes; injeta alertas de reunião do dia em TODAS as sessões + no session_start para reuniões futuras
- `block_start.py`, `block_close.py`, `phase_manager.py` atualizados com campos de timestamp
- `velocity_inference.py` e `phase_forecast.py` existentes reorientados para usar dados reais

## 3. Invariants

- Timestamps automáticos nos dois modos (MMORPG + corporativo) — zero input manual para o dado básico
- Mesmo dia de reunião: alerta aparece em TODA sessão e no início de TODA resposta com countdown
- Forecast NUNCA recomenda paralelismo automaticamente — sempre uma sugestão que o Piloto confirma
- pilot-calendar.yaml é local (`governance/`) — nunca commitar no repo do cliente (já separado por design)
- Suite verde após cada bloco

## 4. Dependencies

- Phase 29 completa (`block_start.py`, `block_close.py`, `phase_manager.py` com suporte a novos campos)
- Phase 31 completa (consistency_score por bloco disponível para o forecast de paralelismo)
- `velocity_inference.py` e `phase_forecast.py` existentes (reorientados, não reescritos)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `started_at`/`finished_at` ausentes em blocos antigos | Med | Velocity calculada só de blocos com timestamps; blocos antigos ignorados |
| Pausa não registrada distorce velocity | Low | Campo `paused_duration_hours` opcional; sem pausa = assume tempo contínuo (aceitável na v1) |
| Forecast confidence BAIXO com poucos dados distrai mais que ajuda | Low | Confidence band exibida explicitamente; abaixo de 3 blocos exibe "histórico insuficiente" |
| Alerta de reunião em toda resposta vira ruído | Low | Só ativo no mesmo dia; formatado como linha única; Piloto desliga via ux-config se quiser |

## 6. Validation

- `pytest sdk/tests/ -q` → 0 failed após cada bloco
- Smoke test velocity: fechar um bloco com `started_at` + `finished_at` → `actual_duration_hours` calculado corretamente
- Smoke test pausa: `--pause` + `--resume` → duração da pausa descontada do total
- Smoke test forecast: `python sdk/forecast_engine.py --arch-root .` → HTML gerado com velocity, estimativa, confidence
- Smoke test calendar: ditar reunião → `pilot-calendar.yaml` atualizado; alerta aparece no mesmo dia
- Phase timestamps: fechar fase com MMORPG → `phase_finished_at` + `phase_duration_hours` no arquivo de fase

## 7. Exit Criteria

1. `block_start.py` registra `started_at` automaticamente ao iniciar qualquer bloco (ambos os modos).
2. `block_close.py` registra `finished_at` e calcula `actual_duration_hours` (descontando pausas se houver).
3. `forecast_engine.py` gera HTML com velocity (tickets/dia + horas), estimativa ajustada por reuniões do `pilot-calendar.yaml`, confidence band, e sugestão de paralelismo.
4. `calendar_manager.py` atualiza `pilot-calendar.yaml` via input natural; alerta de reunião do dia aparece em toda sessão com countdown.
5. `phase_manager.py` registra `phase_started_at` e `phase_finished_at` ao iniciar e fechar fases.
6. `velocity_inference.py` existente usa `actual_duration_hours` reais dos manifests (não retorna "INSUFFICIENT DATA" com dados disponíveis).

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|---------|
| block-173 | Velocity Tracker — timestamps + pausa/retomada | M · critical | planned | `manifests/block-173-velocity-tracker.md` |
| block-174 | Forecast Engine — HTML + confidence + paralelismo | M · normal | planned | `manifests/block-174-forecast-engine.md` |
| block-175 | Calendar Manager — YAML + alertas | M · normal | planned | `manifests/block-175-calendar-manager.md` |

## 9. Dependency Graph

```yaml
parallel_execution_plan:
  total_blocks: 3
  recommended_agents: 1
  groups:
    - id: 32A
      blocks: [block-173]
      type: sequential
      depends_on: []
      note: "Velocity tracker primeiro — forecast e calendar dependem de dados de tempo"
    - id: 32B
      blocks: [block-174, block-175]
      type: parallel
      depends_on: [32A]
      note: "Forecast e calendar são independentes entre si"
```

## 10. Out of Scope

- Tracks (agente separado — agent:tracks)
- Integração com Google Calendar / Outlook
- Notificação push fora da sessão (email, Slack, mobile)
- Paralelismo automático de agentes
- Relatório semanal automático (ferramenta já existe no SDK)
