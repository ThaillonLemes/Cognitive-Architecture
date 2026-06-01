---
id: track/forecast-pilotagem
system: Forecast & Pilotagem
description: Predição de entrega e visibilidade do ritmo do Piloto — velocity_inference, phase_forecast, risk_forecast
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 80% de accuracy nas forecasts de entrega (|real - forecast| / forecast ≤ 20%)"
benchmark_unit: "%"
priority_score: 27
stagnation_count: 0
---

# Track: Forecast & Pilotagem

## System Overview

O sistema de forecast prediz quando fases e blocos vão ser concluídos, baseado em velocity medida (horas reais por bloco). No modo corporativo, o foco muda: em vez de "quando o MMORPG fica pronto", a pergunta é "quantos tickets o Piloto entrega esta semana / até sexta". `velocity_inference` mede o ritmo; `phase_forecast` projeta; `risk_forecast` identifica riscos de não-entrega. Quando funciona bem: o Piloto sempre sabe se vai entregar a tempo — ou tem alert precoce de atraso.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| forecast_accuracy | ≥ 80% | ~72% (baseado em phases 25-28) | 2026-05-31 |

**Definição:** `forecast_accuracy` = média de (1 - |dias_reais - dias_previstos| / dias_previstos) × 100, sobre as últimas 5 fases concluídas. Medido via `sdk/phase_forecast.py --verify-past`.

**Contexto atual:** Forecast de 2026-06-01 (MEASURED) — session_start reportou. Sistema funcionando mas orientado ao MMORPG. Needs reorientação para tickets do Piloto no corporativo.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Reorientação para tickets do Piloto**: Trocar a unidade de medição de "dias por bloco de MMORPG" para "horas por ticket corporativo". Expectativa: forecast_accuracy para tickets atinge ≥80% após 3 semanas de dados.
2. **Escalada de paralelismo medida**: Começar com 1 ticket/vez, subir para 2 depois de 5 tickets concluídos, depois 3 — até achar o gargalo humano. Instrumentar o ponto de inflexão.
3. **Alerta de entrega por prazo**: "No ritmo atual, você entrega N tickets até sexta." Disparar alerta se N < tickets_prometidos.
4. **Calibração via tick real de velocidade**: Coletar tempo real por bloco corporativo (não estimado) → derivar ritmo correto. Primeiras 2-3 semanas de dados reais superam qualquer estimativa.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 5 | Sistema funciona, mas orientado ao MMORPG; reorientação necessária para corporativo |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 6 | Importante para gestão de expectativas no trabalho |
| **total_priority** | **27** | (5×3)+(0×1)+(6×2) |

## Technical Context

- `sdk/velocity_inference.py`: calcula velocidade real de blocos (tempo por bloco)
- `sdk/phase_forecast.py`: projeta data de conclusão baseado em velocity
- `sdk/risk_forecast.py`: identifica riscos de atraso
- Dados históricos: `blocks/BLOCK_LOG.md` (datas reais), `STATE.md` (fase atual)
- Forecast atual: `governance/phase-forecast-*.md`
- Reorientação necessária: velocity de tickets ≠ velocity de blocos de feature

## Benchmark Tooling

```bash
# Forecast atual:
python sdk/phase_forecast.py --arch-root .

# Verificar accuracy histórica (quando disponível):
# python sdk/phase_forecast.py --arch-root . --verify-past --phases 5

# Velocity atual:
python sdk/velocity_inference.py --arch-root .
```

End of track forecast-pilotagem.
