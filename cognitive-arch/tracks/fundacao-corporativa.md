---
id: track/fundacao-corporativa
system: Fundação Corporativa
description: Infraestrutura da Fase 29 — estrutura de bloco/fase corporativa, hierarquia agente=cliente, modos compartilhados
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "100% dos blocos criados após lançamento do modo corporativo possuem todos os campos corporativos obrigatórios"
benchmark_unit: "%"
priority_score: 38
stagnation_count: 0
---

# Track: Fundação Corporativa

## System Overview

A Fundação Corporativa é a ramificação compartilhada (modes: corporativo + pessoal) que serve a todos os outros sistemas no modo de trabalho real. Inclui: hierarquia agente=cliente/fase=workday/bloco=ticket, tiers por tamanho×importância (XS/S/M/L/XL), campos de ticket (ticket_id, acceptance_criteria, reviewer, scope), e estado centrado no Piloto. Está em `status: em design` (Fase 29). Quando completa: o Piloto entra com um ticket qualquer e a arquitetura processa do intake até a entrega com qualidade corporativa.

**Status:** 🔧 em design — Fase 29 ainda não iniciada. Esta track é um marcador de progresso.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| corporate_field_coverage | 100% | 0% (não implementado) | 2026-05-31 |

**Definição:** `corporate_field_coverage` = % de blocos criados após o lançamento corporativo que possuem todos os campos obrigatórios: `ticket_id`, `acceptance_criteria`, `tier_size`, `tier_importance`, `reviewer`, `client_id`.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — fundação não construída)_ | — | — | — | — | — |

## Open Hypotheses

1. **Brainstorm de bloco + redesign de template** (pré-requisito Fase 29): Definir todos os campos corporativos, tiers, e template atualizado. Expectativa: corporate_field_coverage sobe de 0% para 100% em novos blocos.
2. **Brainstorm de fase + redesign de template**: Adaptar fase para hierarquia agente=cliente. Expectativa: fases geradas já carregam client_id e mode de expansão.
3. **Sistema de marca de expansão (corporativo/pessoal/compartilhado)**: Tagger que marca cada artefato com sua origem. Permite separação limpa dos dois modos.
4. **Seleção de modo no boot**: Primeira ação ao abrir = escolher modo. Desliga arquivos do modo não-ativo para reduzir contexto.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 8 | Sem a fundação, modo corporativo não existe; bloqueia todo trabalho na Visagio |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 7 | Fase 29 é a próxima grande prioridade após o sistema de tracks |
| **total_priority** | **38** | (8×3)+(0×1)+(7×2) |

## Technical Context

- Documento de design: `design/corporate-mode.md` (fonte da verdade)
- Fase 29 rascunho: `phases/phase-29.md` (draft — reescopado pelo corporate-mode.md)
- Template de bloco atual: `templates/block.md` (precisa de redesign)
- Template de fase atual: `templates/phase.md` (precisa de redesign)
- Brainstorm de bloco e fase: planejados como sessões separadas (§7B do corporate-mode.md)
- Modos: corporativo (exclusivo) / pessoal (exclusivo) / compartilhado (serve aos dois)
- Scanner é compartilhado — track #15

## Benchmark Tooling

```bash
# Medir corporate_field_coverage após implementação:
# Para cada bloco em blocks/ criado após 2026-06-XX (data de lançamento):
#   Verificar presença de: ticket_id, acceptance_criteria, tier_size, tier_importance, reviewer, client_id
#   Score = campos_presentes / 6 × 100

# Proxy atual (antes do lançamento):
python sdk/audit.py --arch-root .
# O audit atual verifica campos do template ATUAL.
# Após redesign: audit.py precisa ser atualizado para verificar os novos campos.
```

End of track fundacao-corporativa.
