# Template: Phase doc — Dual-Mode (v2)
# Atualizado em: 2026-06-01 (design/block-phase-redesign.md)
# Modos: mmorpg | corporate | shared

BRIEF: Skeleton para doc de fase. Fases ficam em `phases/phase-N.md`. Usar `protocols/phase-generation.md`.
Seções marcadas [mmorpg] são opcionais no modo corporativo. Seções marcadas [corporate] são opcionais no mmorpg.
Seções sem marcação são obrigatórias em ambos os modos.

**Nota de modo:**
- **corporate/feature** → usar as 5 seções obrigatórias abaixo. Opcionais apenas se claramente úteis.
- **corporate/workday** → workday NÃO tem documento. É representado por `current_workday` no STATE.md.
- **mmorpg** → usar todas as seções aplicáveis; OPTIONAL segue a instrução original.

Copiar para `phases/phase-<N>.md`.

---

```yaml
---
id: phase-<N>
mode: mmorpg | corporate | shared    # herdado pelo governor e pelos blocos
type: feature | mmorpg               # feature = fase corporativa; mmorpg = fase de produto
status: planned                      # planned | active | complete
prev_phase: phase-<N-1>              # ou "none" se for a primeira
blocks_count: <number>
created_at: YYYY-MM-DD
last_updated: YYYY-MM-DD
owner: <agent or human>
# [corporate]:
# client_id: ~                       # nome do cliente ou projeto
# [mmorpg]:
# estimated_duration_minutes: <number>   # S≈15min, M≈40min, L≈120min
---
```

---

# Phase <N> — <Title>

BRIEF: 2 linhas max — o que esta fase entrega.

---

## 1. Objective [REQUIRED]

**[corporate]:** Um parágrafo. O que esta feature entrega ao cliente? Qual o resultado observável?

**[mmorpg]:** Um parágrafo. O que esta fase entrega ao projeto? Qual o outcome?

---

## 2. Tickets / Block Index [REQUIRED]

**[corporate]:** Lista de ticket_ids incluídos nesta feature.

| ticket_id | Título | Status | Block |
|-----------|--------|--------|-------|
| <ID> | <título> | planned | `manifests/block-<NNN>-<slug>.md` |

**[mmorpg]:** Tabela de blocos.

| Block | Título | Status | Manifest |
|-------|--------|--------|----------|
| <ID> | <título> | planned | `manifests/block-<ID>-<slug>.md` |

---

## 3. Exit Criteria [REQUIRED]

Lista numerada. Cada item AUDITÁVEL — não "parece bom", mas "X está medido e passou".

1. <critério 1>
2. <critério 2>
3. ...

**[corporate]:** Incluir: "Todos os acceptance_criteria dos tickets foram atendidos e teach-ready passou."

---

## 4. Out of Scope [REQUIRED]

O que esta fase explicitamente NÃO faz:
- <deferral 1>
- <deferral 2>

---

## 5. Phase Retrospective Summary [REQUIRED — preencher ao fechar]

*Gerado ao fechar a fase. Fornece dados para velocity e forecast.*

```yaml
phase_retro:
  completed_at: YYYY-MM-DDTHH:MMZ
  total_blocks: <N>
  blocks_done: <N>
  total_hours: <N>                    # soma de actual_duration_hours dos blocos
  tickets_delivered: <N>              # [corporate]
  velocity_tickets_per_day: <N>       # [corporate]
  highlights: []                      # o que foi melhor que o esperado
  lowlights: []                       # o que foi pior que o esperado
  decisions: []                       # decisões arquiteturais ou de processo tomadas na fase
```

---

## 6. Dependencies [mmorpg — REQUIRED; corporate — OPTIONAL]

O que deve ser verdade antes desta fase começar:
- Phase <N-1> exit criteria todos atendidos
- [Outras dependências]

---

## 7. Goals [mmorpg — REQUIRED se ≥3 blocos; corporate — omitir — use tickets em §2]

3–7 bullets. Cada um concreto e testável.
- Goal 1
- Goal 2

---

## 8. Invariants [OPTIONAL — include if cross-cutting properties must be preserved]

Propriedades que devem ser verdadeiras durante toda a fase:
- API X permanece backward-compatible
- Budget de performance Y não é excedido

---

## 9. Risks [OPTIONAL — include if ≥3 blocks OR cross-system]

| Risk | Impact | Mitigation |
|------|--------|------------|
| <risco> | high/med/low | <plano> |

---

## 10. Dependency Graph & Parallel Execution Plan [mmorpg — OPTIONAL; corporate — raramente necessário]

```yaml
parallel_execution_plan:
  total_blocks: <count>
  recommended_agents: <count>
  groups:
    - id: <Na>
      blocks: [<id1>, <id2>]
      type: parallel | sequential
      depends_on: []
```

---

End of phase template (v2 — dual-mode).
