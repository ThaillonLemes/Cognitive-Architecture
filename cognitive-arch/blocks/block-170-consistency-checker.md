---
id: block-170
manifest: manifests/block-170-consistency-checker.md
status: done
gates_passed: 3/3
completed_at: 2026-06-01T00:40Z
agent: implementer
commit: ~
duration_actual_days: 1
actual_duration_hours: 3.0
duration_source: estimated
tok_estimated: ~4000
tok_src: estimated
wip_stage_reached: implementing
---

# Block 170 — Consistency Checker

## 1. Summary

`sdk/consistency_checker.py` implementado com nível B (naming + imports + organização, sempre ativo)
e C (estilo interno, toggleável). Threshold dinâmico que sobe com a média histórica mas NUNCA cai
sem aprovação do Piloto. ConsistencyReport com score 0-1, lista de divergências por categoria,
e export textual formatado por audiência (Slack, meeting). Integrado com ux-config.yaml para
leitura dos toggles.

## 2. Gates

- [x] files-updated: STATE.md, NEXT.md, BLOCK_LOG.md atualizados
- [x] scope-clean: apenas arquivos declarados foram tocados
- [x] tests-pass: 10/10 pytest sdk/tests/test_consistency_checker.py

## 3. What changed

| Arquivo | Mudança |
|---------|---------|
| sdk/consistency_checker.py | Novo: check_consistency(), run_check(), ConsistencyReport, compute_dynamic_threshold |
| governance/ux-config.yaml | consistency_checker.level_b/level_c já adicionados no block-168 |
| governance/tools-registry.yaml | Adicionado consistency-checker (via patch abaixo) |
| sdk/tests/test_consistency_checker.py | 10 testes novos |

## 4. Decisions

- Checker sem L3/L4 no profile levanta FileNotFoundError — mensagem clara instrui rodar scanner primeiro
- Divergências por diff (não por arquivo completo) — análise do que MUDOU, não do estado total
- Score: 1.0 - 0.07 * len(divergences) — penalidade leve para não bloquear em falsos positivos
- Threshold: never falls é uma invariante de negócio, não só uma regra de código

## 5. Analytics

```yaml
analytics:
  complexity_felt: 3
  estimation_accuracy: on-track
  blockers: []
  rework_in_block: false
  pattern_learned: [score-with-soft-penalties]
```
