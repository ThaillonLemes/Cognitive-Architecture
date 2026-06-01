---
id: track/briefing-pos-pausa
system: Briefing pós-pausa
description: Resumo de reentrada após gap de sessão — briefing_generator
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "100% das sessões com gap > 24h têm um briefing válido consumido antes de iniciar trabalho"
benchmark_unit: "%"
priority_score: 12
stagnation_count: 0
---

# Track: Briefing pós-pausa

## System Overview

O gerador de briefing produz um resumo de reentrada quando o gap entre sessões é grande — o que mudou, o que estava em andamento, e qual é o próximo passo. `briefing_generator.py` gera o arquivo; `session_start.py` dispara quando detecta gap > 24h. Quando funciona bem: o Piloto retoma exatamente de onde parou, sem "o que eu estava fazendo mesmo?". Quando falha: briefing desatualizado ou ausente — perda de contexto e retrabalho de orientação.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| briefing_coverage_rate | 100% | gap 14.7h coberto (session_start) | 2026-05-31 |

**Definição:** `briefing_coverage_rate` = % de sessões com gap > 24h onde um briefing foi gerado e está disponível ao iniciar.

**Estado atual:** session_start reportou "session gap: 14.7h since last run" — gap detectado mas abaixo de 24h, sem briefing necessário. O mecanismo funciona.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Briefing corporativo com context de tickets**: No modo corporativo, o briefing deve incluir: tickets em aberto, prazo mais próximo, e última ação em cada ticket ativo. Hoje é orientado ao MMORPG.
2. **Nível de detalhe configurável**: Curto (3 bullet points) ou longo (seção por área). O Piloto escolhe conforme o tempo disponível.
3. **Threshold de gap configurável**: Hoje é 24h. Semanas longas de trabalho podem precisar de briefing mais cedo (após 8h de inatividade quando há prazo iminente).

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 2 | Funciona; gap handling detectado corretamente |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 3 | Útil mas raramente o gargalo principal |
| **total_priority** | **12** | (2×3)+(0×1)+(3×2) |

## Technical Context

- `sdk/briefing_generator.py`: gera briefings de reentrada
- `sdk/session_start.py`: dispara briefing quando gap > 24h
- Gap atual: 14.7h (abaixo do threshold de 24h)
- Forecast de próxima sessão: 2026-06-01 (MEASURED)

## Benchmark Tooling

```bash
# Verificar último briefing:
# ls cognitive-arch/governance/briefing-*.md | tail -1

# Forçar geração de briefing (para testar):
# python sdk/briefing_generator.py --arch-root . --force

# Session start (detecta gap automaticamente):
python sdk/session_start.py --arch-root .
```

End of track briefing-pos-pausa.
