---
id: track/bloco-fase
system: Bloco & Fase
description: Estrutura de execução do trabalho — a unidade atômica (bloco) e seu agrupamento (fase/workday/feature)
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 95% dos blocos gerados têm todos os campos obrigatórios preenchidos no primeiro rascunho"
benchmark_unit: "%"
priority_score: 44
stagnation_count: 0
---

# Track: Bloco & Fase

## System Overview

Bloco é a unidade atômica de progresso (um ticket, uma tarefa). Fase é o agrupamento — um workday, uma feature, ou um conjunto de tickets de um cliente. Toda entrega acontece dentro dessa estrutura. Quando funciona bem: blocos são gerados completos, consistentes com o template, e fechados sem retrabalho. Quando funciona mal: campos faltam, retrospectivas são superficiais, e a qualidade dos gates cai.

No modo corporativo, o bloco precisa de campos extras (ticket_id, acceptance_criteria, tier por tamanho×importância). O redesign do bloco e da fase é pré-requisito de toda a Fase 29.

**⚠️ REGRA: O redesign de Bloco & Fase acontece na sessão principal com o Piloto. Este Track REGISTRA e monitora — não executa o redesign autonomamente.**

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| completude_de_campos | ≥ 95% | ~80% (estimado — template desatualizado) | 2026-05-31 |

**Nota de medição:** `completude_de_campos` = (campos preenchidos / total de campos obrigatórios do template) × 100, média sobre os últimos 5 blocos gerados. Ferramenta: `python sdk/audit.py --arch-root .` verifica campos; inspeção manual do template.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Redesign do template de bloco com campos corporativos**: Adicionar `ticket_id`, `acceptance_criteria`, `tier` (tamanho×importância), `reviewer`, `scope_corp`. Expectativa: completude sobe de ~80% para ≥95% em novos blocos.
2. **Redesign do template de fase com hierarquia agente=cliente**: Adicionar `client_id`, `mode` (corporativo/pessoal/compartilhado), `workday_or_feature`. Expectativa: alinhar a fase ao modelo corporativo.
3. **Gate de completude obrigatório no block_close**: Verificar campos antes de fechar. Expectativa: zero blocos fechados com campos faltantes.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 8 | Sem o redesign do bloco, o modo corporativo não tem base |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 10 | Piloto explicitamente: "bloco é a estrutura mais importante" |
| **total_priority** | **44** | (8×3)+(0×1)+(10×2) |

## Technical Context

- Template atual: `templates/block.md` (desatualizado — não tem campos corporativos)
- Template de fase: `templates/phase.md`
- Geração de blocos: `protocols/block-generation.md`, `sdk/block_start.py`
- Fechamento: `sdk/block_close.py`, `protocols/block-close-checklist.md`
- Estado: `STATE.md`, `NEXT.md`, `blocks/BLOCK_LOG.md`
- Tiers existentes: S/M/L — precisam de XS (micro) e XL (feature robusta)
- Corporate context: `design/corporate-mode.md` §3.3 (pipeline) e §6B (bloco como coração)

## Benchmark Tooling

Como medir `completude_de_campos`:

```bash
# 1. Listar os últimos 5 blocos fechados
# grep -r "status: done" blocks/ | tail -5

# 2. Para cada bloco, contar campos obrigatórios presentes vs. ausentes
# python sdk/audit.py --arch-root . --check-template

# 3. Inspecionar manualmente: abrir blocks/block-NNN-*.md e comparar com templates/block.md
# Campos obrigatórios atuais: id, title, phase, kind, tier, status, gates, fread, fmod,
#   tok_in, tok_out, tok_src, retro
# Campos corporativos futuros: ticket_id, acceptance_criteria, reviewer, scope_corp
```

End of track bloco-fase.
