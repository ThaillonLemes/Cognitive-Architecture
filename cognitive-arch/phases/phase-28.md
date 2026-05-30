---
id: phase-28
status: planned
prev_phase: phase-27
exit_criteria_count: 6
blocks_count: 6
estimated_duration_minutes: 480
created_at: 2026-05-30
last_updated: 2026-05-30
owner: implementer
---

# Phase 28 — Bug Hunt: Hardening & Consistency

BRIEF: Resultado de um bug hunt multi-agente adversarial completo (77 agentes, 32 candidatos → 26 confirmados, 2 disputados). Esta fase corrige todos os defeitos encontrados, organizados em 6 blocos por família de risco. Nenhum bloco introduz funcionalidade nova — cada um fecha bugs reais reproduzidos no código atual.

## 1. Purpose

Após as fases 24–27 construírem o motor completo (invariant engine, health model, proposal apply/rollback, forecasts), o bug hunt de abertura da fase 28 revelou que várias camadas têm furos silenciosos: o guard de imutabilidade é bypassável por colisão de basename, integridade SHA256 falha invisível ao audit default, applies corrompem arquivos cp1252, ferramentas divergem no mesmo score, CLIs crasham sob Windows cp1252, e previsões de fase usam regex não-ancorado que over-conta blocos. Esta fase sela esses defeitos e deixa o motor confiável o suficiente para o Piloto decidir o próximo norte.

## 2. Goals

- Fechar os 2 gaps de segurança críticos no apply (corrupção UTF-8 + bypass de imutabilidade por basename).
- Tornar qualquer MISMATCH SHA256 em arquivo imutável visível e bloqueante em toda a cadeia (integrity_check, audit, session_start, INV1).
- Unificar número e rótulo de health em uma única fonte (health_model.label_for()), eliminando divergências entre ferramentas.
- Fazer todos os CLIs sobreviverem a cp1252 e ao flag-as-path `--arch-root`.
- Corrigir regex de contagem de blocos em phase_forecast e tendência de velocidade.
- Cobrir com testes os caminhos de erro descobertos pelo hunt.

## 3. Invariants

- Cada bloco termina com `python -m pytest sdk/tests/ -q` verde (0 failed).
- `python sdk/audit.py --arch-root .` sem erros após cada bloco.
- Nenhum arquivo de protocolo imutável é modificado sem integrity-bump explícito.
- Nenhum bug novo introduzido nos caminhos existentes (regressão detectada por suite).

## 4. Dependencies

- Phase 27 (proposal_apply, guard gates, invariant engine) — base direta para blocks 156–158.
- Phase 26 (health_model) — base para block 159.
- Phase 25 (integrity_check, invariant_check) — base para blocks 156–157.
- Bug hunt report (2026-05-30) — fonte primária de todos os findings.

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Fix de basename-guard quebra caso legítimo de bump por nome curto | High | Rastrear governor-log real; suite de testes cobre cenários legítimos |
| Mudança de integrity_check --strict altera comportamento de CI | Med | Flag --strict só escalona exit code; output WARN→ERROR é additive |
| Refactor de label_for() em health_model rompe scrapes em session_start | Med | Regex de scrape atualizado no mesmo bloco; teste de integração cobre |
| HOT files trim (block-158) pode excluir conteúdo necessário | Low | Medir tokens antes/depois; manter semântica, só comprimir |

## 6. Validation

- Suite completa verde após cada bloco (gate obrigatório).
- Para cada bug corrigido: um novo teste ou asserção existente modificada demonstra o fix.
- `audit --strict` deve agora falhar com MISMATCH em PROTOCOLS.md (confirmado no bug hunt) — bloco 157 o conserta e bloco 157 verifica que PASS só volta após fix do lock.
- `audit --strict` deve falhar quando warnings > 0 após bloco 157.
- `proposal_apply` com arquivo cp1252 deve preservar bytes intactos após bloco 158.
- Todos os CLIs com `--arch-root` devem rodar sem traceback sob cp1252 após bloco 160.

## 7. Exit Criteria

1. Os 26 bugs confirmados pelo hunt têm fix no código e teste cobrindo o caminho corrigido.
2. Os 2 disputados foram decididos (pelo Piloto) e tratados ou aceitos documentadamente.
3. `python sdk/audit.py --arch-root .` → `Result: PASS`, `Errors: 0`, Score ≥ 90.
4. `python sdk/audit.py --arch-root . --strict` → falha se e somente se houver MISMATCH ou warning real (não falso positivo).
5. `python -m pytest sdk/tests/ -q` → 0 failed (inclui `test_hot_boot_keeps_headroom`).
6. `session_start.py` session_gap e health line funcionam corretamente; label uniforme WARNING→DEGRADED resolvido.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-156 | Guards de imutabilidade & autorização de bump | L | planned | `manifests/block-156-immutability-guards.md` |
| block-157 | Integridade visível por padrão em toda a cadeia | M | planned | `manifests/block-157-integrity-visible.md` |
| block-158 | Corrupção de dados no apply & gate de verificação | M | planned | `manifests/block-158-apply-data-integrity.md` |
| block-159 | Consistência health/score entre ferramentas | M | planned | `manifests/block-159-health-score-consistency.md` |
| block-160 | Robustez CLI: encoding cp1252 & flag-as-path | M | planned | `manifests/block-160-cli-robustness.md` |
| block-161 | Forecasts, relatórios & ruído de audit | M | planned | `manifests/block-161-forecasts-reports.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 6
  recommended_agents: 1
  groups:
    - id: 28A
      blocks: [block-156]
      type: sequential
      depends_on: []
      note: "Guards de imutabilidade — deve rodar primeiro; bloco 158 depende dos guards corretos"
    - id: 28B
      blocks: [block-157]
      type: sequential
      depends_on: [28A]
      note: "Integridade visível — usa _is_immutable corrigido do 156"
    - id: 28C
      blocks: [block-158]
      type: sequential
      depends_on: [28B]
      note: "Apply data integrity — depende de guards (156) e integrity check (157)"
    - id: 28D
      blocks: [block-159, block-160, block-161]
      type: parallel
      depends_on: [28C]
      note: "Independentes entre si; podem rodar em qualquer ordem após 28C"
```

## 10. Out of Scope

- Novos features (nenhum bloco adiciona capacidade nova).
- Correção de gaps históricos aceitos em known-drift.md (INV2 blocos 061-085, INV3 blocos 108-111).
- Áreas identificadas pelo crítico de completude como fora do hunt (dispatch.py, governor.py, notification_manager locks, block_close gate wiring) — ficam para fase 29.
- Decisão do Norte (rumo estratégico da arquitetura) — permanece com o Piloto.
