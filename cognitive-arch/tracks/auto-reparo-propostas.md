---
id: track/auto-reparo-propostas
system: Auto-reparo de Propostas
description: Aplicação segura e reversível de mudanças propostas — proposal_apply, proposal_resolver, protocol_updater
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 95% das propostas são aplicadas sem necessidade de rollback"
benchmark_unit: "%"
priority_score: 22
stagnation_count: 0
---

# Track: Auto-reparo de Propostas

## System Overview

O sistema de propostas permite que a IA gere mudanças estruturadas no sistema (novos protocolos, updates de estado, correções de arquivos) e as aplique de forma segura. `proposal_apply.py` aplica; `proposal_resolver.py` resolve conflitos; `protocol_updater.py` atualiza protocolos. Guards garantem que mudanças perigosas não passem sem revisão. Rollback disponível se algo der errado. No modo corporativo, esse sistema vai ser usado para aplicar mudanças no repo do cliente — tornando o requisito de confiabilidade ainda mais crítico.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| clean_apply_rate | ≥ 95% | não medido (sem instrumentação de taxa) | 2026-05-31 |
| rollback_required_rate | ≤ 5% | não medido | 2026-05-31 |

**Definição:** `clean_apply_rate` = % de proposals aplicados que não requerem rollback. `rollback_required_rate` = % que precisam de rollback.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Instrumentação de apply/rollback**: Adicionar log em `governance/proposal-log.md` — cada apply registra sucesso/rollback/motivo. Pré-requisito para medir a taxa.
2. **Guards para operação à distância (repo do cliente)**: Quando `proposal_apply` aponta para um repo externo (`--target-repo <path>`), guards extras: confirm do Piloto obrigatório, nunca em batch sem revisão, log imutável.
3. **Dry-run obrigatório antes de apply em repo externo**: `proposal_apply --dry-run` deve ser o passo 1 de qualquer apply fora do repo cognitivo. Reduz rollback por consequência inesperada.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 4 | Guards implementados (fase 27); funciona mas falta instrumentação |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 5 | Vai escalar em criticidade quando for usado no repo do cliente |
| **total_priority** | **22** | (4×3)+(0×1)+(5×2) |

## Technical Context

- `sdk/proposal_apply.py`: aplica propostas estruturadas
- `sdk/proposal_resolver.py`: resolve conflitos entre propostas
- `sdk/protocol_updater.py`: atualiza protocolos
- Guards implementados em Fase 27 (block-level guards + rollback)
- 0 proposals pending (session_start 2026-05-31)
- Operação à distância: `--target-repo <path>` — ver §3.5 corporate-mode.md
- Compliance crítico: nunca persistir código do cliente no repo cognitivo

## Benchmark Tooling

```bash
# Ver proposals pendentes:
python sdk/proposal_apply.py --list --arch-root .

# Dry run de uma proposta:
# python sdk/proposal_apply.py --dry-run --proposal governance/proposals/proposal-NNN.md --arch-root .

# Após implementação de log:
# cat governance/proposal-log.md | grep -E "apply|rollback" | wc -l
```

End of track auto-reparo-propostas.
