---
id: track/master-agent
system: Master Agent
description: Sugestão proativa de próximas ações e scheduling — master_scheduler, master_suggest
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 70% das sugestões proativas do master_suggest são adotadas pelo Piloto"
benchmark_unit: "%"
priority_score: 17
stagnation_count: 0
---

# Track: Master Agent

## System Overview

O Master Agent opera em background para sugerir proativamente o que trabalhar a seguir e quando — baseado em STATE.md, NEXT.md, e padrões de trabalho detectados. `master_scheduler.py` agenda tarefas recorrentes; `master_suggest.py` gera sugestões baseadas no contexto atual. Quando funciona bem: o Piloto chega e já tem uma sugestão precisa de onde continuar. Quando falha: sugestões irrelevantes que o Piloto ignora — ruído que cria desconfiança no sistema.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| suggestion_acceptance_rate | ≥ 70% | não medido | 2026-05-31 |

**Definição:** `suggestion_acceptance_rate` = % de sugestões do master_suggest adotadas sem modificação significativa pelo Piloto.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Instrumentação de acceptance**: Rastrear para cada sugestão: adotada / modificada / ignorada. Sem isso, taxa de sucesso é desconhecida.
2. **Contextualização corporativa**: Sugestões devem levar em conta o calendário do Piloto, prazos de tickets, e reuniões próximas (quando integrado). "Você tem reunião amanhã — trabalhe no ticket mais próximo de ser fechável hoje."
3. **Limiar de confiança antes de sugerir**: Só sugerir quando confidence ≥ 80%. Sugestões de baixa confiança fazem mais mal que bem.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 3 | Sistema funciona; não é gargalo crítico |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 4 | Proatividade é útil mas o Piloto pilota — não é pré-requisito |
| **total_priority** | **17** | (3×3)+(0×1)+(4×2) |

## Technical Context

- `sdk/master_scheduler.py`: agenda tarefas recorrentes
- `sdk/master_suggest.py`: gera sugestões proativas
- Estado: `agents/board.md` (master agent registrado como idle)
- Integração futura: calendário e prazos de tickets do corporativo

## Benchmark Tooling

```bash
# Ver sugestões atuais:
python sdk/master_suggest.py --arch-root .

# Verificar agenda:
python sdk/master_scheduler.py --list --arch-root .
```

End of track master-agent.
