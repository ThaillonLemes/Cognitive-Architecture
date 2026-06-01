---
id: block-165
manifest: manifests/block-165-ticket-intake.md
status: done
gates_passed: 3/3
completed_at: 2026-06-01T00:15Z
agent: implementer
commit: ~
duration_actual_days: 1
actual_duration_hours: 1.5
duration_source: estimated
tok_estimated: ~2500
tok_src: estimated
wip_stage_reached: implementing
---

# Block 165 — Ticket Intake

## 1. Summary

`sdk/ticket_intake.py` criado: lê texto livre de ticket, infere acceptance criteria, numera o próximo
bloco sem colisão lendo BLOCK_LOG.md + manifests/, gera manifest com `kind: intake` e campos corporativos
pré-preenchidos (com `NEEDS_REVIEW` nos campos que precisam de atenção do Piloto).

## 2. Gates

- [x] files-updated: STATE.md, NEXT.md, BLOCK_LOG.md atualizados
- [x] scope-clean: apenas arquivos declarados foram tocados
- [x] tests-pass: 6/6 pytest sdk/tests/test_ticket_intake.py

## 3. What changed

| Arquivo | Mudança |
|---------|---------|
| sdk/ticket_intake.py | Novo: CLI --ticket --client --arch-root; generate_manifest() |
| sdk/tests/test_ticket_intake.py | 6 testes novos |
| governance/tools-registry.yaml | Adicionado ticket-intake |

## 4. Decisions

- `kind: intake` (não `ticket`) no manifest gerado — Piloto promove para `ticket` após revisão
- Acceptance criteria extraídos heuristicamente; marcados NEEDS_REVIEW quando não encontrados
- Numeração usa max(BLOCK_LOG + manifests/) para evitar colisão em qualquer estado do repo

## 5. Analytics

```yaml
analytics:
  complexity_felt: 1
  estimation_accuracy: on-track
  blockers: []
  rework_in_block: false
  pattern_learned: []
```
