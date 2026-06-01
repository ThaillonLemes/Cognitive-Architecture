---
id: track/pipeline-qualidade
system: Pipeline de Qualidade
description: Ciclo implementar↔qualidade com motor de consistência, testes e revisão — intake, scan-dirigido, implementar, qualidade, teach
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≤ 10% dos blocos de implementação requerem reabrir após a etapa de qualidade"
benchmark_unit: "%"
priority_score: 7
stagnation_count: 0
---

# Track: Pipeline de Qualidade

## ⚠️ STATUS: NÃO CONSTRUÍDO — eventualmente

Este sistema ainda não existe. Está planejado para a Fase 31. Esta track é registrada agora para **não esquecer** — quando a Fase 31 iniciar, esta track já tem o contexto necessário.

## System Overview

O pipeline de qualidade é a espinha dorsal do trabalho corporativo: `TICKET → [Intake] → [Scan L2/L3] → [Implementar] → [Qualidade] → [Teach/Report] → ENTREGA`. Não é esteira reta — é ciclo: quando Qualidade detecta discrepância, reabre para Implementar. O motor de consistência valida estrutura do código contra o `project-profile` (não lógica de negócio — isso é do senior). Saída em HTML por etapa. Quando funciona bem: código entregue é consistente com o time, tem testes realísticos, e o Piloto consegue explicar tudo antes da reunião.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| rework_rate | ≤ 10% | N/A (não construído) | 2026-05-31 |

**Definição:** `rework_rate` = % de blocos de implementação que precisam ser reabertos após a etapa de qualidade (o ciclo implementar→qualidade→implementar conta como 1 retrabalho).

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — sistema não existe ainda)_ | — | — | — | — | — |

## Open Hypotheses

*(A ser definidas quando a Fase 31 iniciar)*

1. **Motor de consistência como primeira camada**: Validar nomenclatura, estrutura de arquivos, e imports contra project-profile ANTES da revisão humana. Fácil de automatizar, alto impacto.
2. **Ciclo implementar↔qualidade com HTML pequeno**: Cada iteração do ciclo gera um HTML enxuto (não um documento completo — só o delta da rodada).
3. **Liga/desliga HTML**: O Piloto pode desligar a geração de HTML e trabalhar só no chat. A função continua existindo.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 1 | Não existe — não pode ser bottleneck ainda |
| stagnation_score | 0 | N/A |
| user_priority | 2 | Baixa agora — construído na Fase 31 |
| **total_priority** | **7** | (1×3)+(0×1)+(2×2) |

## Technical Context

*(A ser definido na Fase 31)*

- Planejado: `sdk/intake.py`, `sdk/consistency_checker.py`, `sdk/teach_mode.py`
- Pipeline: intake → scan → implementar ↔ qualidade → teach
- Motor de consistência: valida estrutura APENAS — não lógica de negócio
- HTML por etapa: scan-html, qualidade-html, teach-html
- Referência de design: `design/corporate-mode.md` §3.2, §3.3, §6B

## Benchmark Tooling

```bash
# Não existe ainda.
# Quando implementado:
# python sdk/quality_check.py --block <NNN> --arch-root . --profile governance/project-profile-<cliente>.md
# Saída: consistency_score, divergencias[], rework_needed: true/false
```

End of track pipeline-qualidade.
