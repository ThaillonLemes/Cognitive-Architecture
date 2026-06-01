---
id: track/scanner-dossie
system: Scanner & Dossiê
description: Scanner profundo de codebase com base de conhecimento persistente — L0/L1/L2/L3/L4, project-profile, dossiê HTML
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 90% dos campos L0-L4 de um project-profile são preenchidos corretamente no primeiro scan"
benchmark_unit: "%"
priority_score: 7
stagnation_count: 0
---

# Track: Scanner & Dossiê

## ⚠️ STATUS: NÃO CONSTRUÍDO — eventualmente

Este sistema ainda não existe. Está planejado para a Fase 30. Esta track é registrada agora para **não esquecer** — quando a Fase 30 iniciar, esta track já tem o contexto necessário.

## System Overview

O scanner analisa codebases externas em 5 níveis (L0-L4) e persiste o resultado como `project-profile-<cliente>.md` — a base de conhecimento que permite gerar código no estilo exato do time do cliente. L0 = arquitetura macro do sistema; L1 = estrutura e linguagens; L2 = padrões de arquitetura de software; L3 = estética e convenções de código; L4 = coexistência de padrões (legado vs. vigente). Saída: dossiê HTML visual + project-profile persistente.

**Por que importa:** é a fundação de tudo no modo corporativo. Código gerado sem scan tende a divergir do padrão do time — visível e problemático em review.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| scan_completeness_score | ≥ 90% | N/A (não construído) | 2026-05-31 |

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — sistema não existe ainda)_ | — | — | — | — | — |

## Open Hypotheses

*(A ser definidas quando a Fase 30 iniciar)*

1. **Scan macro profundo uma vez, salvo**: O L0-L1 é executado uma vez e persiste. Custo de token alto na primeira vez, mas só paga uma vez.
2. **Scan dirigido por ticket (L2/L3)**: Para cada ticket, scan apenas na área de toque — não re-scan completo. Eficiente.
3. **Dogfooding no MMORPG**: Testar o scanner no próprio projeto MMORPG antes de usar em cliente real.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 1 | Não existe — não pode ser bottleneck ainda |
| stagnation_score | 0 | N/A |
| user_priority | 2 | Baixa agora — construído na Fase 30 |
| **total_priority** | **7** | (1×3)+(0×1)+(2×2) |

## Technical Context

*(A ser definido na Fase 30)*

- Planejado: `sdk/scanner.py`, `sdk/profile_builder.py`
- Output: `governance/project-profile-<cliente>.md`
- HTML output: por cada nível de scan
- Compliance: project-profile guarda apenas METADADOS — nunca código-fonte do cliente
- Referência de design: `design/corporate-mode.md` §3.1

## Benchmark Tooling

```bash
# Não existe ainda.
# Quando implementado:
# python sdk/scanner.py --target-repo <path> --level L1 --arch-root .
# python sdk/scanner.py --target-repo <path> --level all --arch-root .
```

End of track scanner-dossie.
