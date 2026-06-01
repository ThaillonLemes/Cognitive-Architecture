---
id: block-167
manifest: manifests/block-167-scanner-deep.md
status: done
gates_passed: 3/3
completed_at: 2026-06-01T00:25Z
agent: implementer
commit: ~
duration_actual_days: 1
actual_duration_hours: 3.0
duration_source: estimated
tok_estimated: ~4500
tok_src: estimated
wip_stage_reached: implementing
---

# Block 167 — Deep Scan: L2 + L3 + L4

## 1. Summary

Motor de detecção profunda implementado. L2: detecção de padrão arquitetural por sinais estruturais
(FSD, Clean, MVC, DDD, CQRS, etc.) com checklist de 9 padrões. L3: naming conventions, import style,
test organization, formatters. L4: classificação vigente/legado por frequência × recência de arquivos.
Cada inferência inclui prova de raciocínio para o HTML.

## 2. Gates

- [x] files-updated: STATE.md, NEXT.md, BLOCK_LOG.md atualizados
- [x] scope-clean: apenas arquivos declarados foram tocados
- [x] tests-pass: 7/7 pytest sdk/tests/test_scanner_deep.py

## 3. What changed

| Arquivo | Mudança |
|---------|---------|
| sdk/scanner_deep.py | Novo: scan_deep(), _detect_architecture(), _detect_naming_convention(), _detect_pattern_coexistence() |
| sdk/tests/test_scanner_deep.py | 7 testes novos |
| sdk/codebase_scanner.py | scan_deep importado e chamado para níveis L2/L3/L4 |

## 4. Decisions

- L4 usa timestamps de modificação de arquivo como proxy de recência (sem git blame — LGPD safe)
- Fallback gracioso quando checklist não identifica padrão: lê 5-10 arquivos-chave
- Perfil NUNCA armazena trechos de código (teste explícito valida)

## 5. Analytics

```yaml
analytics:
  complexity_felt: 3
  estimation_accuracy: on-track
  blockers: []
  rework_in_block: false
  pattern_learned: [structural-signal-detection]
```
