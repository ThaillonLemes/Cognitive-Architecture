---
id: track/adr-drafter
system: ADR Drafter
description: Geração automática de Architecture Decision Records — adr_drafter
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 90% dos ADRs rascunhados não precisam de revisão estrutural"
benchmark_unit: "%"
priority_score: 17
stagnation_count: 0
---

# Track: ADR Drafter

## System Overview

O ADR Drafter gera Architecture Decision Records automaticamente quando uma decisão arquitetural é tomada — capturando o contexto, as opções consideradas, e a justificativa da escolha. No modo corporativo, ADRs são documentação que justifica decisões para revisores, superiores, e futuros membros do time. Quando funciona bem: o Piloto tem documentação clara de cada decisão sem esforço extra. Quando falha: ADRs gerados precisam de reescrita estrutural — o Piloto está escrevendo documentação em vez de receber documentação.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| no_rework_rate | ≥ 90% | não medido | 2026-05-31 |

**Definição:** `no_rework_rate` = % de ADRs que não precisam de revisão estrutural (campos faltando, raciocínio incompleto, ou seções trocadas) após a primeira geração.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Template de ADR corporativo**: Adicionar ao template campos relevantes para o contexto corporativo: `client_context`, `compliance_check`, `team_impact`. Expectativa: ADRs gerados já chegam adequados para apresentação interna.
2. **Trigger automático de ADR no brainstorm**: Quando brainstorm gera uma decisão com confidence ≥ alta, triggerar ADR automaticamente — o contexto ainda está fresco.
3. **Revisão de ADR por dial de abstração**: ADR para o Piloto (técnico) vs. ADR para gestores (leigo) — o mesmo conteúdo em dois formatos. Reutiliza o dial UX.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 3 | Funciona; não é gargalo |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 4 | Documentação importante mas não bloqueia entrega |
| **total_priority** | **17** | (3×3)+(0×1)+(4×2) |

## Technical Context

- `sdk/adr_drafter.py`: gera ADRs a partir de decisões detectadas
- Template: `templates/ADR.md`
- ADRs ficam em: `design/adr-*.md` ou equivalente
- Protocolo de geração: `protocols/adr-generation.md`

## Benchmark Tooling

```bash
# Gerar ADR para uma decisão:
# python sdk/adr_drafter.py --decision "..." --arch-root .

# Listar ADRs existentes:
# ls cognitive-arch/design/adr-*.md

# Medir no_rework_rate:
# Para cada ADR: status = aprovado_verbatim | revisado | descartado
# Rate = aprovado_verbatim / total × 100
```

End of track adr-drafter.
