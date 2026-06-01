---
id: track/token-tracker
system: Token Tracker
description: Rastreamento de consumo de tokens por sessão e por bloco — token_tracker
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 95% das sessões têm contagem de tokens dentro de 10% do real"
benchmark_unit: "%"
priority_score: 9
stagnation_count: 0
---

# Track: Token Tracker

## System Overview

O token tracker coleta e consolida o consumo de tokens por bloco e por sessão. No modo corporativo, token cost não é gargalo (o Piloto usa a IA livremente e o custo vale o resultado). Portanto, a track tem prioridade baixa — mas permanece ativa porque: (a) dados históricos de tokens informam planejamento de capacidade, e (b) a integridade do rastreamento é útil para identificar blocos excessivamente pesados. Quando funciona bem: relatórios mostram consumo real por bloco. Quando falha: os dados são estimados, não medidos.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| token_accuracy | ≥ 95% | desconhecido — maioria usa tok_src:estimated | 2026-05-31 |

**Definição:** `token_accuracy` = % de blocos onde tok_src:actual (não :estimated).

**Nota corporativa:** Token não é gargalo no corporativo (conforme §7C corporate-mode.md). Esta track é mantida para integridade de dados, não para otimização de custo.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Instrumentação de tok_src:actual por padrão no SDK mode**: Quando dispatch usa SDK mode, tok_in e tok_out vêm da API — tok_src deve ser :actual. Hoje o mock usa :estimated. Corrigir para que SDK mode sempre gere :actual.
2. **Alertas de blocos "pesados" (> X tokens)**: Blocos com muitos tokens geralmente indicam complexidade excessiva ou falta de escopo claro — útil como sinal de qualidade.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 1 | Token não é gargalo no corporativo |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 3 | Útil para dados históricos; baixa prioridade |
| **total_priority** | **9** | (1×3)+(0×1)+(3×2) |

## Technical Context

- `sdk/token_tracker.py`: rastreia tokens por bloco e sessão
- `return_validator.py`: valida tok_in, tok_out, tok_src nos return packages
- tok_src válidos: `actual` (API mediu) | `estimated` (placeholder)
- Integração: tok_in/tok_out são campos obrigatórios no return package

## Benchmark Tooling

```bash
# Ver token usage por bloco no log:
# grep "tok_in\|tok_out\|tok_src" cognitive-arch/blocks/BLOCK_LOG.md

# Taxa atual de actual vs. estimated:
# python sdk/token_tracker.py --arch-root . --summary
```

End of track token-tracker.
