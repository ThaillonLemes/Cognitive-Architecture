---
id: block-174
manifest: manifests/block-174-forecast-engine.md
status: done
gates_passed: 3/3
completed_at: 2026-06-01T01:00Z
agent: implementer
commit: ~
duration_actual_days: 1
actual_duration_hours: 2.0
duration_source: estimated
tok_estimated: ~3000
tok_src: estimated
wip_stage_reached: implementing
---

# Block 174 — Forecast Engine: HTML + Confidence + Paralelismo

## 1. Summary

`sdk/forecast_engine.py` implementado: lê histórico de `actual_duration_hours` dos manifests,
calcula velocity (tickets/dia + horas/ticket), gera HTML de forecast com confidence band
(BAIXO/MÉDIO/ALTO baseado em N histórico), estimativa de entrega ajustada por reuniões do calendário,
e sugestão de paralelismo. phase_forecast.py reorientado por comentário + velocity_inference.py
já beneficia automaticamente dos dados reais.

## 2. Gates

- [x] files-updated: STATE.md, NEXT.md, BLOCK_LOG.md atualizados
- [x] scope-clean: apenas arquivos declarados foram tocados
- [x] tests-pass: 9/9 pytest sdk/tests/test_forecast_engine.py

## 3. What changed

| Arquivo | Mudança |
|---------|---------|
| sdk/forecast_engine.py | Novo: generate_forecast_html(), _load_velocity_history(), _compute_velocity(), _parallelism_recommendation() |
| sdk/phase_forecast.py | Adicionado comentário de integração com velocity_tracker |
| sdk/tests/test_forecast_engine.py | 9 testes novos |

## 4. Decisions

- 6h/dia útil produtiva como baseline (configurável manualmente por contexto)
- Paralelismo recomendado apenas quando: 5+ blocos sem loopback E tempo médio > 30min
- Histórico insuficiente (<3) exibe "BAIXO" explicitamente — sem forecast enganoso

## 5. Analytics

```yaml
analytics:
  complexity_felt: 2
  estimation_accuracy: on-track
  blockers: []
  rework_in_block: false
  pattern_learned: []
```
