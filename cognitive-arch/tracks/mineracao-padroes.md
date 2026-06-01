---
id: track/mineracao-padroes
system: Mineração de Padrões
description: Detectar padrões recorrentes no trabalho e gerar recomendações acionáveis — pattern_analyzer, recommendation_engine, retro_signals
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 60% dos padrões detectados resultam em uma recomendação concreta adotada"
benchmark_unit: "%"
priority_score: 22
stagnation_count: 0
---

# Track: Mineração de Padrões

## System Overview

O minerador de padrões analisa retrospectivas e logs de blocos para encontrar comportamentos recorrentes — scope expansion, blocos reabertas, erros repetidos. `pattern_analyzer.py` detecta; `recommendation_engine.py` gera sugestões; `retro_signals.py` extrai sinais das retrospectivas. No modo corporativo, padrões de retrabalho em tickets são dados de melhoria de processo valiosos. Quando funciona bem: o Piloto recebe insights acionáveis antes de repetir um erro. Quando falha: padrões são detectados mas ficam como "alertas sem consequência" — ruído.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| pattern_actionability_rate | ≥ 60% | não medido | 2026-05-31 |
| active_patterns_count | ≤ 2 ativos ao mesmo tempo | 3 ativos (session_start) | 2026-05-31 |

**Definição:** `pattern_actionability_rate` = % de padrões que resultam em pelo menos uma recomendação concreta adotada pelo Piloto. `active_patterns_count` = padrões em `governance/patterns.md` com status:active.

**Estado atual:** session_start reportou 3 active patterns detectados — estão em `governance/patterns.md`.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Resolver os 3 padrões ativos**: Triagem dos padrões em `governance/patterns.md` — para cada um, gerar uma ação concreta ou dismiss se irrelevante. Reduzir ruído de padrões "ativos eternamente".
2. **Threshold de acionamento por frequência**: Só promover um padrão para "active" se aparecer ≥ 3 vezes. Padrões de 1-2 ocorrências viram "observações" — não alertas.
3. **Integração com intake de ticket (corporativo)**: Quando um novo ticket chega, checar se há padrão de retrabalho associado ao tipo de ticket. Warning precoce: "esse tipo de ticket costuma ter scope expansion — garanta critérios claros".

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 4 | 3 padrões ativos sem resolução — ruído, mas não bloqueante |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 5 | Melhoria de processo — valioso mas não urgente |
| **total_priority** | **22** | (4×3)+(0×1)+(5×2) |

## Technical Context

- `sdk/pattern_analyzer.py`: detecta padrões
- `sdk/recommendation_engine.py`: gera recomendações
- `sdk/retro_signals.py`: extrai sinais de retrospectivas
- Estado: `governance/patterns.md` (3 ativos em 2026-05-31)
- Protocolo: session_start sempre lê patterns.md e reporta ativos
- Padrão mais recorrente: scope-expansion-recurring (detectado 4x segundo test_governor.py)

## Benchmark Tooling

```bash
# Ver padrões ativos:
cat cognitive-arch/governance/patterns.md

# Rodar análise de padrões:
python sdk/pattern_analyzer.py --arch-root .

# Gerar recomendações:
# python sdk/recommendation_engine.py --arch-root .

# Medir actionability_rate (quando instrumentado):
# Para cada padrão: status = adopted | dismissed | pending
# Rate = adopted / (adopted + dismissed + pending) × 100
```

End of track mineracao-padroes.
