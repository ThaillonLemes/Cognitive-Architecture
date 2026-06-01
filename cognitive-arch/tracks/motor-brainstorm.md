---
id: track/motor-brainstorm
system: Motor de Brainstorm
description: Geração e síntese de ideias estruturadas — brainstorm_context, brainstorm_predictor, brainstorm_synthesis
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 80% das sínteses de brainstorm são aceitas pelo Piloto sem revisão estrutural"
benchmark_unit: "%"
priority_score: 22
stagnation_count: 0
---

# Track: Motor de Brainstorm

## System Overview

O motor de brainstorm recebe input do Piloto, gera contexto estruturado, prevê abordagens, e sintetiza uma proposta. É a ferramenta de tomada de decisão — cada decisão de design importante passa por aqui. Já em uso ativo. Quando funciona bem: a síntese entregue já captura a decisão certa e o Piloto só confirma. Quando falha: a síntese precisa de revisão estrutural — o Piloto está reescrevendo em vez de aprovando.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| synthesis_acceptance_rate | ≥ 80% | ~70% (estimado — sem instrumentação formal) | 2026-05-31 |

**Definição:** `synthesis_acceptance_rate` = % de brainstorms onde a síntese foi aceita verbatim ou com ajustes mínimos (sem revisão estrutural). Taxa de acerto reportada: 5/10 aceitos verbatim no corporate-mode.md session = 50%, mas os outros foram expandidos (não rejeitados) — logo o real é ≥50% mas <80%.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Calibrar confiança pré-síntese**: Quando a IA tem baixa confiança (🔴), sinalizar antes de gerar a síntese e perguntar ao Piloto por mais contexto. Expectativa: reduz revisões estruturais nos pontos 🔴.
2. **Separar estrutura de conteúdo**: A estrutura da síntese (campos, formato) deve ser fixa e previsível. O conteúdo varia. Reduzir variação estrutural entre brainstorms aumenta a taxa de aprovação.
3. **Brainstorm de intake de ticket**: Adaptar o motor para o formato de intake corporativo (ticket_id, acceptance_criteria, tier). O brainstorm de decisão de abordagem é diferente do brainstorm de design — templates distintos.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 4 | Já em uso; funciona mas poderia ser mais preciso |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 5 | Importante mas não urgente — a arquitetura de brainstorm já está rodando |
| **total_priority** | **22** | (4×3)+(0×1)+(5×2) |

## Technical Context

- `sdk/brainstorm_context.py`: gera contexto estruturado para o brainstorm
- `sdk/brainstorm_predictor.py`: prevê abordagens e riscos
- `sdk/brainstorm_synthesis.py`: sintetiza o output final
- Protocolo: `protocols/brainstorm-pattern-v2.md`
- Taxa de acerto por confiança: 🟢 alta confiança → aceito verbatim; 🔴 baixa → revisado
- Corporate-mode.md foi gerado por brainstorm v2 — caso de uso de referência

## Benchmark Tooling

```bash
# Ver histórico de brainstorms (quando disponível):
# ls cognitive-arch/_brainstorm/

# Medir synthesis_acceptance_rate:
# 1. Após cada brainstorm, registrar: aceito_verbatim | revisado_estrutural | revisado_conteudo
# 2. Calcular %_aceito_verbatim + %_revisado_conteudo / total (ambos = síntese ok)
# 3. %_revisado_estrutural é o que queremos minimizar
```

End of track motor-brainstorm.
