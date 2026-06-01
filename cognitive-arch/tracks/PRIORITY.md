# tracks/PRIORITY.md — Track Priority Table

This file is the Governor's runtime priority source. Updated after every Track Block (close or reopen) and whenever the human changes user_priority.

**Priority formula:** `total_priority = (bottleneck_score × 3) + (stagnation_score × 1) + (user_priority × 2)`

**Highest total_priority = current_focus.**

Protocol: `protocols/track-priority.md`

---

## Active Tracks

| track_id | bottleneck_score | stagnation_count | user_priority | total_priority | current_best | last_improved_at | stagnation_alert | notes |
|----------|-----------------|-----------------|--------------|----------------|-------------|-----------------|-----------------|-------|
| track/bloco-fase | 8 | 0 | 10 | 44 | ~80% completude (estimado) | ~ | — | **SESSÃO PRINCIPAL — não trabalhar autonomamente** |
| track/fundacao-corporativa | 8 | 0 | 7 | 38 | 0% (não implementado) | ~ | — | Fase 29 — em design |
| track/orquestracao-paralelismo | 7 | 0 | 8 | 37 | 100% mock / SDK: desconhecido | ~ | — | **CURRENT FOCUS do agente paralelo** |
| track/confiabilidade-notificacoes | 7 | 0 | 8 | 37 | Health: 80/100 DEGRADED | ~ | — | 29 invariant warnings ativos |
| track/forecast-pilotagem | 5 | 0 | 6 | 27 | ~72% accuracy (estimado) | ~ | — | Reorientar para tickets corporativos |
| track/ux-dial-abstracao | 5 | 0 | 6 | 27 | não medido (dial não existe) | ~ | — | Dial global planejado para Fase 29+ |
| track/motor-brainstorm | 4 | 0 | 5 | 22 | ~70% aceitação (estimado) | ~ | — | Já em uso ativo |
| track/auto-reparo-propostas | 4 | 0 | 5 | 22 | não medido | ~ | — | Guards implementados (fase 27) |
| track/mineracao-padroes | 4 | 0 | 5 | 22 | 3 padrões ativos sem resolução | ~ | — | Ver governance/patterns.md |
| track/master-agent | 3 | 0 | 4 | 17 | não medido | ~ | — | Proatividade útil, não crítica |
| track/adr-drafter | 3 | 0 | 4 | 17 | não medido | ~ | — | — |
| track/briefing-pos-pausa | 2 | 0 | 3 | 12 | gap 14.7h coberto | ~ | — | Funciona; threshold 24h |
| track/dashboard-relatorios | 2 | 0 | 3 | 12 | skipped em 2026-05-31 | ~ | — | Investigar por que foi skipped |
| track/token-tracker | 1 | 0 | 3 | 9 | tok_src:estimated maioria | ~ | — | Token não é gargalo no corporativo |
| track/scanner-dossie | 1 | 0 | 2 | 7 | N/A — não construído | ~ | — | **Fase 30 — eventualmente** |
| track/pipeline-qualidade | 1 | 0 | 2 | 7 | N/A — não construído | ~ | — | **Fase 31 — eventualmente** |

---

## current_focus

```
current_focus: track/orquestracao-paralelismo
reason: highest actionable total_priority (37) — track/bloco-fase (44) reservado para sessão principal com Piloto
agent: tracker (agente paralelo, wip desde 2026-05-31)
```

---

## Stagnation Alerts

Tracks onde `stagnation_count ≥ 3` aparecem aqui. The Governor includes these in the next health report.

| track_id | stagnation_count | alert |
|----------|-----------------|-------|
| _(none)_ | — | — |

---

## Update Log

| date | event | track_id | field_changed | old_value | new_value |
|------|-------|----------|--------------|-----------|-----------|
| 2026-05-31 | track_created | ALL (16 tracks) | — | none | 16 tracks created by agent:tracker |
| 2026-05-31 | current_focus_set | track/orquestracao-paralelismo | current_focus | none | track/orquestracao-paralelismo |

---

## Score Reference

| Factor | Weight | 0 | 3–4 | 5–6 | 7–8 | 9–10 |
|--------|--------|---|-----|-----|-----|------|
| bottleneck_score | ×3 | Unknown | Minor | Moderate | Major | Primary bottleneck |
| stagnation_count | ×1 | Improving | Stuck | Very stuck | Rethink needed | Escalate |
| user_priority | ×2 | Paused | Low | Normal | High | Top priority |

---

## Benchmark adaptation note (2026-05-31)

Os benchmarks desta arquitetura NÃO são de latência/ms (contexto MMORPG original). São de **qualidade / robustez / consistência**:

- `%` completude de campos, taxa de aceitação, taxa de retrabalho, accuracy de forecast
- `count` de falhas silenciosas, padrões ativos sem resolução, warnings não tratados
- Métricas contínuas medidas via scripts SDK ou observação de sessão

**Por que isso importa:** no modo corporativo, "performance" é qualidade de entrega e confiabilidade do processo — não velocidade de operações. Otimizar latência de um dispatch Python local seria ruído.

End of PRIORITY.md.
