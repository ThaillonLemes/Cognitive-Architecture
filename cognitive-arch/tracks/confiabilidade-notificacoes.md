---
id: track/confiabilidade-notificacoes
system: Confiabilidade & Notificações
description: Entrega garantida de notificações e integridade do sistema — notification_manager, audit, integrity_check, invariant_check
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "100% das notificações criadas atingem status:seen — zero falhas silenciosas"
benchmark_unit: "%"
priority_score: 37
stagnation_count: 0
---

# Track: Confiabilidade & Notificações

## System Overview

O sistema de notificações (`notification_manager.py`) alerta o Piloto sobre eventos críticos — padrões detectados, prazo de invariantes, health degradado. `audit.py` verifica consistência estrutural. `integrity_check.py` detecta corrupção de dados. `invariant_check.py` verifica invariantes do sistema. Quando funciona bem: alertas críticos chegam sempre, sem falha silenciosa. Quando falha: o Piloto não sabe que algo está errado — o pior modo de falha possível. A diretriz do design/corporate-mode.md é explícita: **notificações de track devem ser absolutas — zero tolerância a erro**.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| notification_delivery_rate | 100% | não medido | 2026-05-31 |
| silent_failure_rate | 0% | não medido | 2026-05-31 |
| audit_clean_run_rate | ≥ 95% | Score 80/100 (DEGRADED) | 2026-05-31 |

**Definição:** `notification_delivery_rate` = notificações com `status:seen` / notificações criadas × 100. `silent_failure_rate` = notificações que falham sem log de erro / total × 100.

**Estado atual (session_start 2026-05-31):** Health: 80/100 [DEGRADED]. 29 invariant warnings ativos. Isso indica que o sistema de confiabilidade está ativo mas não está zero-erro.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| _(sem histórico — track recém-criada)_ | — | — | — | — | — |

## Open Hypotheses

1. **Instrumentação de delivery_rate**: Adicionar contador de criação vs. seen em `governance/notifications.md`. Hoje não existe medição de quantas notificações ficam perpetuamente `pending`. Pré-requisito para qualquer outra melhoria.
2. **Modo fail-loud em `notification_manager.py`**: Se `_acquire_lock()` tiver timeout, hoje pode falhar silenciosamente. Adicionar log obrigatório em `governance/governor-log.md` para toda falha de lock.
3. **Reduzir 29 invariant warnings**: `sdk/invariant_check.py` mostra 29 warns. Cada warn não tratado é ruído que oculta warnings reais. Triagem e resolução dos warns ativos.
4. **Health score 100 como meta**: Session start mostra 80/100 [DEGRADED]. Identificar e corrigir os 20 pontos de degradação.

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 7 | Sistema degradado (80/100); notificações sem medição de reliability |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 8 | "Notificações de track devem ser absolutas" — design/corporate-mode.md §6B |
| **total_priority** | **37** | (7×3)+(0×1)+(8×2) |

## Technical Context

- `sdk/notification_manager.py`: CRUD para `governance/notifications.md`. Lock file cross-platform. Prioridades: critical/high/medium/low. Status: pending/seen/dismissed.
- `sdk/audit.py`: verificação estrutural completa. Usado em CI e em `session_start.py`.
- `sdk/integrity_check.py`: detecta corrupção de dados em STATE.md e outros arquivos de estado.
- `sdk/invariant_check.py`: verifica invariantes — atualmente 0 critical, 29 warn.
- `governance/notifications.md`: arquivo de estado das notificações ativas.
- `governance/notifications-archive.md`: histórico.
- `governance/governor-log.md`: log de operações do governor.

## Benchmark Tooling

Como medir `notification_delivery_rate` e `silent_failure_rate`:

```bash
# Estado atual das notificações:
python sdk/notification_manager.py --list --arch-root .
# Conta pending vs. seen vs. dismissed

# Rodar audit completo:
python sdk/audit.py --arch-root .
# Score atual: 80/100

# Verificar invariants:
python sdk/invariant_check.py --arch-root .
# Saída: N critical, M warn

# Medir delivery_rate manualmente:
# 1. Criar uma notificação de teste via notification_manager
# 2. Confirmar que aparece no list
# 3. Marcar como seen
# 4. Verificar que não ficou stuck em pending
```

End of track confiabilidade-notificacoes.
