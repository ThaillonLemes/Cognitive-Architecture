---
id: block-162
manifest: manifests/block-162-template-swap.md
status: done
gates_passed: 4/4
completed_at: 2026-06-01T00:00Z
agent: implementer
commit: ~
duration_actual_days: 1
actual_duration_hours: 1.5
duration_source: estimated
tok_estimated: ~2000
tok_src: estimated
wip_stage_reached: implementing
---

# Block 162 — Template Swap: v1 → v2

## 1. Summary

Templates v1 imutáveis (manifest-small.md, manifest-medium.md, manifest-large.md, block-retrospective.md)
removidos e substituídos pelos v2 aprovados em design/block-phase-redesign.md. audit.py atualizado para
aceitar ambos os formatos (v1 com `tier`, v2 com `size+importance`).

## 2. Gates

- [x] files-updated: STATE.md, NEXT.md, BLOCK_LOG.md atualizados
- [x] scope-clean: apenas arquivos declarados foram tocados
- [x] tests-pass: 5/5 pytest sdk/tests/test_template_swap.py
- [x] v1-removed: nenhum dos 4 templates v1 existe mais em templates/

## 3. What changed

| Arquivo | Ação |
|---------|------|
| templates/manifest-small.md | Removido (imutável, swap para v2) |
| templates/manifest-medium.md | Removido (imutável, swap para v2) |
| templates/manifest-large.md | Removido (imutável, swap para v2) |
| templates/block-retrospective.md | Removido (imutável, swap para v2) |
| sdk/audit.py | check5 atualizado: detecta v1 vs v2; usa keys corretos por versão |
| sdk/tests/test_template_swap.py | Novo: 5 testes |

## 4. Decisions

- `audit.py` detecta v2 pela presença de `size:` no frontmatter — sem flag de versão explícita
- v1 manifests continuam funcionando (retrocompatível por detecção automática)

## 5. Analytics

```yaml
analytics:
  complexity_felt: 1
  estimation_accuracy: on-track
  blockers: []
  rework_in_block: false
  pattern_learned: []
```
