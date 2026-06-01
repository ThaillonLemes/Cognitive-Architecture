---
id: phase-31
status: planned
prev_phase: phase-30
exit_criteria_count: 6
blocks_count: 3
estimated_duration_minutes: 300
created_at: 2026-05-31
last_updated: 2026-05-31
owner: implementer
design_source: design/pipeline.md
brainstorm_source: _brainstorm/pipeline-v2-redesign.md
---

# Phase 31 — Pipeline de Trabalho Corporativo

BRIEF: Implementa o pipeline completo de entrega corporativa — consistency checker com
threshold dinâmico, ciclo review implementar↔qualidade com decisão manual do Piloto,
e teach mode obrigatório em todo ticket com export multi-audiência.

## 1. Purpose

O Scanner (Phase 30) dá o conhecimento do projeto. Esta fase entrega a máquina de entrega:
o mecanismo que garante que todo ticket é implementado no padrão do time, revisado com rigor,
e só entregue quando o Piloto entende completamente o que fez.

## 2. Goals

- `sdk/consistency_checker.py`: verifica naming, imports, organização (nível B, padrão) + estilo interno (nível C, toggleável); threshold dinâmico baseado em histórico; export textual para copy-paste
- `sdk/review_pipeline.py`: orquestra o ciclo implementar↔qualidade; gera HTML de qualidade (consistency + testes + Big-O + sugestões opcionais); prompt manual para go/no-go do Piloto
- `sdk/teach_mode.py`: teach sempre obrigatório por ticket; dial de abstração global; 3 HTMLs por audiência (técnico/equipe/aprendizado); export textual; loopback flag para implementar
- `governance/ux-config.yaml` atualizado com todos os toggles de HTML e checker

## 3. Invariants

- Teach mode é SEMPRE executado antes de fechar qualquer bloco de ticket (`wip_stage: teaching`)
- Nenhuma transição automática no ciclo — Piloto decide em cada iteração
- Threshold de consistência NUNCA baixa automaticamente — requer aprovação explícita do Piloto
- Checker valida contra o project-profile existente — NÃO roda sem L3/L4 no perfil
- Export textual disponível em todas as etapas com HTML
- Todos os HTMLs default ON; Piloto desliga o que não usa

## 4. Dependencies

- Phase 29 completa (block infrastructure: `wip_stage: teaching` antes de `done`)
- Phase 30 completa (scanner: `project-profile-<cliente>.md` com L3/L4 para o checker)
- `governance/ux-config.yaml` com estrutura de toggles definida

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Checker sem L3/L4 no profile gera falsos positivos | High | Checker verifica presença de L3/L4 antes de rodar; erro claro se ausente |
| Nível C do checker gera muitos falsos positivos | Med | C é default OFF; Piloto ativa conscientemente |
| Threshold dinâmico cai rápido num período de tickets difíceis | Med | Auto-lower bloqueado; Piloto aprova qualquer redução |
| Teach mode obrigatório vira fricção percebida | Low | É requisito do `wip_stage: teaching`; sem teach, bloco não fecha — design intencional |
| 3 HTMLs de teach são muito similares | Low | Cada HTML tem foco claro; Piloto desliga os que não usa via ux-config |

## 6. Validation

- `pytest sdk/tests/ -q` → 0 failed após cada bloco
- Smoke test checker: `python sdk/consistency_checker.py --diff <arquivo> --profile governance/project-profile-fixture.md` → score + lista de divergências sem crash
- Smoke test review: `python sdk/review_pipeline.py --block-id block-XXX` → HTML gerado com todas as seções; prompt go/no-go exibido
- Smoke test teach: `python sdk/teach_mode.py --block-id block-XXX` → 3 HTMLs gerados; texto puro disponível; loopback prompt exibido

## 7. Exit Criteria

1. `consistency_checker.py` retorna score + divergências para um diff sintético com divergências conhecidas de naming e imports (nível B).
2. Nível C toggleável: ligado → detecta estilo interno; desligado → ignora.
3. `review_pipeline.py` gera HTML com consistency + cobertura de testes + Big-O; prompt go/no-go permite ao Piloto iterar ou encerrar.
4. Threshold dinâmico: após 5 blocos com score alto, threshold sobe; nunca cai sem aprovação.
5. `teach_mode.py` gera 3 HTMLs + export textual; loopback flag retorna bloco para `wip_stage: implementing`.
6. `block_close.py` rejeita `done` se `wip_stage != teaching` em blocos de ticket (`kind: ticket`).

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|---------|
| block-170 | Consistency Checker | L · critical | planned | `manifests/block-170-consistency-checker.md` |
| block-171 | Review Pipeline + Quality Reporter | M · critical | planned | `manifests/block-171-review-pipeline.md` |
| block-172 | Teach Mode | M · critical | planned | `manifests/block-172-teach-mode.md` |

## 9. Dependency Graph

```yaml
parallel_execution_plan:
  total_blocks: 3
  recommended_agents: 1
  groups:
    - id: 31A
      blocks: [block-170]
      type: sequential
      depends_on: []
      note: "Checker primeiro — review pipeline e teach mode consomem seu output"
    - id: 31B
      blocks: [block-171, block-172]
      type: parallel
      depends_on: [31A]
      note: "Review pipeline e teach mode são independentes entre si"
```

## 10. Out of Scope

- Integração com Jira/Linear API
- Paralelismo de tickets (phase-32)
- Auto-geração de PRs
- Análise semântica de lógica de negócio no checker
- Velocity e forecast de qualidade (phase-32)
