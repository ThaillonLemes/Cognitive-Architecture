---
id: track/ux-dial-abstracao
system: UX & Dial de Abstração
description: Camada de apresentação adaptativa — ux_validator, ux-config.yaml, ux-voice.md; dial leigo/iniciante/técnico
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 90% das respostas de explain/teach produzidas no nível correto sem ajuste do usuário"
benchmark_unit: "%"
priority_score: 27
stagnation_count: 0
---

# Track: UX & Dial de Abstração

## System Overview

O sistema UX controla como a IA apresenta informação — o nível de detalhe técnico, o tom, e o formato. `ux-config.yaml` define o perfil ativo; `ux_validator.py` verifica conformidade; `ux-voice.md` define os tons disponíveis. No modo corporativo, o "dial de abstração" (leigo / iniciante / técnico) atravessa todo o sistema: scan, qualidade, teach. Quando funciona bem: o Piloto e terceiros recebem explicações no nível certo na primeira tentativa. Quando falha: explicações muito técnicas para gestores, ou muito rasas para devs — retrabalho e re-explicações.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| dial_first_try_accuracy | ≥ 90% | não medido (dial não implementado) | 2026-05-31 |

**Definição:** `dial_first_try_accuracy` = % de sessões em que o nível de explicação foi aproveitado sem pedido de "explica de novo mais simples/técnico". Medição via feedback explícito do Piloto + observação de re-requests.

**Estado atual:** O teach mode tem 3 níveis fixos (técnico/equipe/aprendizado). O "dial" generalizado (leigo/iniciante/técnico atravessando scan/qualidade/teach) não existe ainda — está nos plans da Fase 29+.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Implementar dial global de abstração**: Substituir os 3 níveis fixos do teach por um dial configurável que afeta scan, qualidade, e teach. Expectativa: reduz re-requests de ajuste de nível.
2. **Detectar nível automaticamente**: Se o usuário usa termos técnicos, escolher nível técnico automaticamente. Se usa linguagem casual, nível leigo. Expectativa: 80%+ de acerto sem configuração explícita.
3. **HTMLs com nível de abstração configurável**: Os artefatos HTML (scan, qualidade, teach) adaptam sua profundidade conforme o dial. Leigo vê resumo; técnico vê detalhes.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 5 | Teach mode funciona; dial global é melhoria importante mas não bloqueia o trabalho |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 6 | Crítico para tornar o sistema vendável/ensinável a terceiros |
| **total_priority** | **27** | (5×3)+(0×1)+(6×2) |

## Technical Context

- `ux-config.yaml`: configuração de UX ativa
- `ux-voice.md`: definições de tons
- `sdk/ux_validator.py`: validação de conformidade UX
- Teach mode atual: 3 níveis (técnico/equipe/aprendizado) — em `protocols/teach-mode.md`
- Dial pretendido: leigo / iniciante / técnico — atravessa todos os outputs do sistema
- Vendabilidade: o dial é o que torna a arquitetura usável por terceiros (ver §3.6 corporate-mode.md)

## Benchmark Tooling

```bash
# Verificar config UX atual:
# cat cognitive-arch/ux-config.yaml

# Validar outputs UX (quando disponível):
# python sdk/ux_validator.py --arch-root . --check-last-session

# Proxy atual: observar quantas vezes por sessão o Piloto pede "simplifica" ou "mais técnico"
# Meta: esse número deve cair com o dial funcionando
```

End of track ux-dial-abstracao.
