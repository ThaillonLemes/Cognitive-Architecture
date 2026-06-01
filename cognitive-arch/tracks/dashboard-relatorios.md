---
id: track/dashboard-relatorios
system: Dashboard & Relatórios
description: Geração automática de relatórios periódicos e dashboards de saúde — dashboard_generator, weekly_report
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 95% dos relatórios agendados são gerados sem correção manual"
benchmark_unit: "%"
priority_score: 12
stagnation_count: 0
---

# Track: Dashboard & Relatórios

## System Overview

O sistema de relatórios gera dashboards de saúde e weekly reports automaticamente — consolidando velocity, health score, padrões, e status de fases. `dashboard_generator.py` produz o dashboard visual; `weekly_report.py` gera o resumo semanal. No modo corporativo, esses relatórios viram instrumentos de visibilidade pessoal do Piloto — quantos tickets entregou, qual a qualidade, qual o ritmo. Quando funciona bem: o Piloto tem visibilidade do seu próprio trabalho sem esforço. Quando falha: relatórios com dados incorretos ou incompletos que precisam de correção manual.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| auto_generation_rate | ≥ 95% | desconhecido (skipped em session_start) | 2026-05-31 |

**Estado atual:** session_start reportou `Skipped: dashboard-refresh, weekly-report` — os relatórios foram pulados hoje. Precisam de instrumentação para medir taxa real.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Entender por que foram skipped**: session_start reportou dashboard e weekly_report como "skipped". Isso é por design (stale detection) ou bug? Verificar `governance/tools-registry.yaml`.
2. **Dashboard de velocity de tickets (corporativo)**: Adicionar view de tickets entregues/semana, ticket_quality, e forecast de capacidade semanal.
3. **Relatório de saída de sessão**: Ao final de cada sessão, gerar um mini-relatório: blocos fechados, tokens gastos, progresso. Visibilidade imediata sem esperar o weekly.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 2 | Sistema existe mas foi skipped — precisa diagnóstico |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 3 | Visibilidade importante mas não bloqueia entrega |
| **total_priority** | **12** | (2×3)+(0×1)+(3×2) |

## Technical Context

- `sdk/dashboard_generator.py`: gera dashboard visual
- `sdk/weekly_report.py`: gera relatório semanal
- Estado de execução: skipped em 2026-05-31 session_start
- Configuração: `governance/tools-registry.yaml` (define stale threshold e ordem de execução)
- Health report: gerado com sucesso (health 80/100 DEGRADED)

## Benchmark Tooling

```bash
# Verificar status dos relatórios:
cat cognitive-arch/governance/tools-registry.yaml

# Forçar geração do dashboard:
python sdk/dashboard_generator.py --arch-root .

# Forçar weekly report:
python sdk/weekly_report.py --arch-root .

# Ver último dashboard:
# ls cognitive-arch/governance/dashboard-*.md | tail -1
```

End of track dashboard-relatorios.
