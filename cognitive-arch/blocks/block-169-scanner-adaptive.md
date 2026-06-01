---
id: block-169
manifest: manifests/block-169-scanner-adaptive.md
status: done
gates_passed: 3/3
completed_at: 2026-06-01T00:35Z
agent: implementer
commit: ~
duration_actual_days: 1
actual_duration_hours: 2.0
duration_source: estimated
tok_estimated: ~3000
tok_src: estimated
wip_stage_reached: implementing
---

# Block 169 — Adaptive Mode + Ticket Inference + Profile Management

## 1. Summary

Modo adaptativo: repos grandes (>200 arquivos) recebem pré-scan com estimativa de custo em 3 opções
antes de qualquer leitura massiva. Inferência de área por ticket: mapa de keywords (auth, payment,
user, api...) → busca diretório correspondente → confirma com Piloto. ProfileManager: detecção de
staleness, list_stale, refresh_level. scanner_ticket.py: entry point dedicado para fluxo de ticket.

## 2. Gates

- [x] files-updated: STATE.md, NEXT.md, BLOCK_LOG.md atualizados
- [x] scope-clean: apenas arquivos declarados foram tocados
- [x] tests-pass: 8/8 pytest sdk/tests/test_scanner_adaptive.py

## 3. What changed

| Arquivo | Mudança |
|---------|---------|
| sdk/scanner_adaptive.py | Novo: adaptive_preflight(), infer_area_from_ticket(), ProfileManager |
| sdk/scanner_ticket.py | Novo: scan_for_ticket(), CLI entry point |
| sdk/tests/test_scanner_adaptive.py | 8 testes novos |

## 4. Decisions

- Keyword map para inferência de área (9 categorias) — extensível sem mudança de interface
- `interactive=False` em testes + CI; modo interativo usa `input()` apenas em produção
- ProfileManager staleness padrão: 30 dias — configurável por chamador

## 5. Analytics

```yaml
analytics:
  complexity_felt: 2
  estimation_accuracy: on-track
  blockers: []
  rework_in_block: false
  pattern_learned: []
```
