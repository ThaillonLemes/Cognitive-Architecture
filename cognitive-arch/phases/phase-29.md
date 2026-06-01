---
id: phase-29
status: planned
prev_phase: phase-28
exit_criteria_count: 5
blocks_count: 4
estimated_duration_minutes: 300
created_at: 2026-05-30
last_updated: 2026-05-31
owner: implementer
design_source: design/block-phase-redesign.md
brainstorm_source: design/block-phase-redesign.md
supersedes: phases/phase-29.md draft 2026-05-30 (5 blocos com scanner — reescopado)
---

# Phase 29 — Corporate Mode: Fundação

BRIEF: Implementa a fundação do modo corporativo — swap formal dos templates v1 → v2,
infraestrutura SDK dual-mode (bloco + fase) e ticket intake. Pré-requisito de todas
as fases corporativas seguintes (30, 31, 32).

## 1. Purpose

A virada de norte de 2026-05-30 redefiniu o objetivo da arquitetura. A arquitetura agora
serve a dois modos — **MMORPG (projeto pessoal)** e **Corporativo (Visagio/tickets)** —
e o bloco, a fase e o STATE precisam ser atualizados para servir a ambos sem bifurcar o sistema.

O design está aprovado em `design/block-phase-redesign.md` (2026-06-01). Esta fase implementa:

1. **Template swap** — substituição formal dos templates imutáveis v1 pelos v2 aprovados
2. **Phase infrastructure** — `mode`, `type`, `client_id` nas fases; STATE centrado no Piloto
3. **Block infrastructure** — `size + importance`, `wip_stage`, `paused`, corporate gates no SDK
4. **Ticket intake** — converter texto de ticket em manifest de bloco corporativo

## 2. Goals

- Templates v1 (`manifest-small/medium/large.md`, `block-retrospective.md`) removidos; v2 são os canônicos
- `sdk/phase_manager.py` suporta `mode: corporate | mmorpg | shared`, `type: feature | workday`, `client_id`
- `STATE.md` com estrutura dual: estado do projeto (MMORPG) + estado cognitivo do Piloto (corporativo)
- `sdk/block_start.py` e `sdk/block_close.py` suportam `size + importance`, `wip_stage`, `paused`
- Corporate gates implementados: `functionality-check`, `consistency-check`, `teach-ready`
- `sdk/ticket_intake.py` — texto de ticket → manifest de bloco com campos corporativos

## 3. Invariants

- Templates v1 são SUBSTITUÍDOS, não coexistem com v2 após este bloco
- `mode` NUNCA aparece no manifest do bloco — herdado da fase
- Bloco corporativo só vai para `done` quando `wip_stage` alcançou `teaching`
- Todos os módulos têm `--arch-root` e `--help` sem crash em cp1252
- Suite verde após cada bloco (`pytest sdk/tests/ -q` → 0 failed)

## 4. Dependencies

- Phase 28 completa (audit 92/100, 1067 testes, 0 errors) — ✓ confirmado
- `design/block-phase-redesign.md` aprovado (2026-06-01)
- `templates/manifest-*-v2.md` existentes como rascunho (criados na design session)
- `templates/block-retrospective-v2.md` existente como rascunho

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Template swap quebra parsers do `audit.py` | High | `audit.py` validado contra templates v2 antes do swap; smoke test pós-swap |
| `wip_stage` não é respeitado pelo `block_close.py` | Med | Gate explícito: block_close verifica `wip_stage == teaching` antes de marcar `done` |
| STATE dual-mode quebra `session_start.py` | Med | `session_start.py` testado em ambos os modos após mudança |
| Campos corporativos opcionais viram obrigatórios inadvertidamente | Low | Campos marcados com comentário `# [corporate]`; validação gate só em mode=corporate |

## 6. Validation

- `pytest sdk/tests/ -q` → 0 failed após cada bloco
- `python sdk/audit.py --arch-root .` → Score ≥ 90 após fase completa
- `ls templates/manifest-*.md` → NÃO lista small/medium/large sem sufixo `-v2`
- Smoke test ticket intake: `python sdk/ticket_intake.py --ticket "implementar JWT refresh" --arch-root .` → manifest com campos `ticket_id`, `acceptance_criteria`, `reviewer`, `client_id`

## 7. Exit Criteria

1. Templates v1 removidos; todos os manifests e retros existentes continuam válidos com os v2
2. `phases/` suporta campos `mode: corporate`, `type: feature`, `client_id` via `phase_manager.py`
3. `block_start.py` lida corretamente com `size + importance` e inicializa `wip_stage: implementing`
4. `block_close.py` valida progressão `implementing → quality → teaching → done` quando mode=corporate
5. `python sdk/ticket_intake.py` gera manifest de bloco com campos `ticket_id`, `acceptance_criteria`, `reviewer`, `client_id` preenchidos

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|---------|
| block-162 | Template Swap — v1 → v2 | M · critical | planned | `manifests/block-162-template-swap.md` |
| block-163 | Phase Infrastructure — dual-mode | M · critical | planned | `manifests/block-163-phase-infrastructure.md` |
| block-164 | Block Infrastructure — dual-mode SDK | M · critical | planned | `manifests/block-164-block-infrastructure.md` |
| block-165 | Ticket Intake | S · normal | planned | `manifests/block-165-ticket-intake.md` |

## 9. Dependency Graph

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 1
  groups:
    - id: 29A
      blocks: [block-162]
      type: sequential
      depends_on: []
      note: "Template swap primeiro — todos os outros blocos usam os templates v2"
    - id: 29B
      blocks: [block-163, block-164]
      type: parallel
      depends_on: [29A]
      note: "Phase infrastructure e block infrastructure são independentes entre si"
    - id: 29C
      blocks: [block-165]
      type: sequential
      depends_on: [29B]
      note: "Ticket intake usa os novos campos de bloco e fase implementados no 29B"
```

## 10. Out of Scope

- Scanner de codebase (phase-30, blocks 166–169)
- Consistency checker (phase-31)
- Pipeline de revisão + qualidade (phase-31)
- Teach mode (phase-31)
- Forecast e velocity de tickets (phase-32)
- Integração com Jira/Linear API
