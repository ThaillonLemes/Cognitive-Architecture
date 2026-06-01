---
id: block-171
manifest: manifests/block-171-review-pipeline.md
status: done
gates_passed: 3/3
completed_at: 2026-06-01T00:45Z
agent: implementer
commit: ~
duration_actual_days: 1
actual_duration_hours: 2.0
duration_source: estimated
tok_estimated: ~3500
tok_src: estimated
wip_stage_reached: implementing
---

# Block 171 — Review Pipeline + Quality Reporter

## 1. Summary

`sdk/review_pipeline.py` implementado: orquestra ciclo implementar↔qualidade. Chama consistency_checker,
analisa cobertura de testes (heurística por manifest), calcula Big-O heurístico (nested loops → O(n²),
.sort() → O(n log n)), gera HTML de qualidade, e apresenta prompt A/B/C ao Piloto. Override (B) registra
`gate_override_reason` no manifest. block_close.py atualizado para mostrar review HTML se presente.

## 2. Gates

- [x] files-updated: STATE.md, NEXT.md, BLOCK_LOG.md atualizados
- [x] scope-clean: apenas arquivos declarados foram tocados
- [x] tests-pass: 5/5 pytest sdk/tests/test_review_pipeline.py

## 3. What changed

| Arquivo | Mudança |
|---------|---------|
| sdk/review_pipeline.py | Novo: run_quality_review(), QualityReport, HTML generator, override recording |
| sdk/block_close.py | Superficia quality HTML path se presente após review_pipeline |
| sdk/tests/test_review_pipeline.py | 5 testes novos |

## 4. Decisions

- Sem profile = gate passa com WARN (corporativo precisa de scan antes do primeiro ticket)
- Big-O heurístico: análise simples de padrões no diff — não é análise estática real
- override_reason gravado no manifest permanece visível para audit e velocity

## 5. Analytics

```yaml
analytics:
  complexity_felt: 2
  estimation_accuracy: on-track
  blockers: []
  rework_in_block: false
  pattern_learned: []
```
