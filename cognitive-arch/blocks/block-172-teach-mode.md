---
id: block-172
manifest: manifests/block-172-teach-mode.md
status: done
gates_passed: 3/3
completed_at: 2026-06-01T00:50Z
agent: implementer
commit: ~
duration_actual_days: 1
actual_duration_hours: 2.0
duration_source: estimated
tok_estimated: ~3500
tok_src: estimated
wip_stage_reached: implementing
---

# Block 172 — Teach Mode

## 1. Summary

`sdk/teach_mode.py` implementado: sempre obrigatório para blocos corporativos antes de `done`. Gera
3 HTMLs por audiência (technical para PR/senior, team para standup, learning para revisão do Piloto)
+ exports de texto para copy-paste. Dial de abstração (leigo/iniciante/técnico) lido do ux-config.yaml.
Loopback: Piloto pode escolher B = retornar para `wip_stage: implementing` com nota do que corrigir.

## 2. Gates

- [x] files-updated: STATE.md, NEXT.md, BLOCK_LOG.md atualizados
- [x] scope-clean: apenas arquivos declarados foram tocados
- [x] tests-pass: 7/7 pytest sdk/tests/test_teach_mode.py

## 3. What changed

| Arquivo | Mudança |
|---------|---------|
| sdk/teach_mode.py | Novo: run_teach(), 3 HTML builders, text export, loopback |
| sdk/block_close.py | Surficia teach HTMLs se presentes; já enforça wip_stage_reached: teaching (block-164) |
| sdk/tests/test_teach_mode.py | 7 testes novos |

## 4. Decisions

- HTML builders são funções puras (sem efeitos externos) para facilidade de teste
- Loopback atualiza `wip_stage: implementing` no manifest — não usa state_manager (é campo local do bloco)
- block_close wip_stage check (block-164) já enforça teaching before done — teach_mode é o que gera o HTML

## 5. Analytics

```yaml
analytics:
  complexity_felt: 2
  estimation_accuracy: on-track
  blockers: []
  rework_in_block: false
  pattern_learned: [three-audience-html-pattern]
```
