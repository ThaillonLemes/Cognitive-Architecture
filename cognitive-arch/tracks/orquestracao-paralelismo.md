---
id: track/orquestracao-paralelismo
system: Orquestração & Paralelismo
description: Motor de despacho de sub-agentes — governor, dispatch, task_packet, integration, return_validator
created_at: 2026-05-31
last_improved_at: ~
benchmark_target: "≥ 95% das tentativas de dispatch em SDK mode completam sem intervenção manual"
benchmark_unit: "%"
priority_score: 37
stagnation_count: 0
---

# Track: Orquestração & Paralelismo

## System Overview

O sistema de orquestração é o motor que transforma manifests em trabalho real de sub-agentes. `governor.py` lê `STATE.md`/`NEXT.md`, monta task packets via `task_packet.py`, despacha para Claude via `dispatch.py`, e integra os resultados de volta ao estado via `integration.py`. `return_validator.py` garante que os retornos são estruturalmente corretos. Quando funciona bem: blocos rodam autônomos, paralelos onde possível, sem intervenção manual. Quando funciona mal: transient API errors causam falhas silenciosas que exigem retry manual.

## Current Benchmark

| Metric | Target | Current best | Measured on |
|--------|--------|-------------|-------------|
| autonomous_completion_rate (mock) | 100% | 100% (22/22 testes) | 2026-05-31 |
| autonomous_completion_rate (SDK) | ≥ 95% | **desconhecido** — sem retry, sem instrumentação | 2026-05-31 |
| dispatch_batch_timeout_handling | ≥ 95% success sob timeout | não medido | 2026-05-31 |

**Definição:** `autonomous_completion_rate` = (dispatches que atingem `integrate_group` sem retry manual) / total de dispatches × 100.

**Nota crítica:** Em mock mode o benchmark é trivialmente 100% (MockAnthropicClient nunca falha). O valor relevante é o SDK mode — atualmente não existe dado porque nunca foi instrumentado.

## Benchmark History

| Block | Date | Hypothesis | benchmark_before | benchmark_after | Result |
|-------|------|-----------|-----------------|-----------------|--------|
| track-block-001-orquestracao | 2026-05-31 | Estado atual medido; retry-with-backoff proposto | SDK: desconhecido | — | PROPOSTA (não executado) |
| track-block-002-orquestracao | 2026-06-01 | Implementar hipóteses 1–4 | SDK: desconhecido | SDK: instrumentado (dispatch-log.md ativo) | IMPLEMENTADO — 1075/1075 testes |

## Open Hypotheses

~~1. **Retry-with-backoff em `_sdk_dispatch()`**~~ — FEITO: `max_retries=2`, backoff `2^attempt` s, retorna 4-tuple com `attempts_used`.
~~2. **Instrumentação de taxa de sucesso em SDK mode**~~ — FEITO: `_append_dispatch_log()` escreve `governance/dispatch-log.md` (thread-safe). Campos: `ts`, `block_id`, `mode`, `attempts`, `success`, `error_type`, `elapsed_sec`.
~~3. **Timeout mais conservador em `dispatch_batch()`**~~ — FEITO: outer timeout = `timeout_sec × 1.5` (era `× n_workers`).
~~4. **Retries independentes por worker**~~ — FEITO: cada thread chama `dispatch_block(max_retries=N)` → retry nativo por worker via `_sdk_dispatch`.

**Modelo atualizado:** `claude-opus-4-5` → `claude-sonnet-4-6`

## Próximas hipóteses

5. **Medir autonomous_completion_rate real em SDK mode**: Acumular 10+ execuções SDK em `dispatch-log.md` e calcular taxa de sucesso observada. Benchmark atual: instrumentado mas sem dados acumulados (zero execuções SDK registradas).

## Priority Score Breakdown

| Factor | Score (0–10) | Notes |
|--------|-------------|-------|
| bottleneck_score | 7 | Sem retry, qualquer erro API = bloqueio manual; afeta todo trabalho corporativo |
| stagnation_score | 0 | Track recém-criada |
| user_priority | 8 | Orquestração é a espinha do sistema — bugs aqui param tudo |
| **total_priority** | **37** | (7×3)+(0×1)+(8×2) |

## Technical Context

- `sdk/governor.py`: entrada CLI. Comanda: `--dry-run`, `--block NNN`, `--test-integration`, `--track`, `--list-tracks`. Lê STATE.md + NEXT.md. Monta governor-state.md antes de cada dispatch (crash recovery).
- `sdk/dispatch.py`: `dispatch_block()` — single dispatch; `dispatch_batch()` — paralelo via `ThreadPoolExecutor(max_workers=4)`. Modo: `sdk | mock | manual`. Sem retry no SDK mode.
- `sdk/task_packet.py`: monta packet a partir de manifest YAML frontmatter + convention snippet.
- `sdk/integration.py`: `integrate_group()` — verifica conflitos fmod, atualiza STATE.md, NEXT.md, BLOCK_LOG.md, board.md. Atomic writes via rename.
- `sdk/return_validator.py`: valida campos obrigatórios no return package do sub-agente.
- Timeout padrão: `DEFAULT_TIMEOUT_SEC = 300` por block. `dispatch_batch` outer: `timeout_sec × n_workers`.
- Modelo padrão: `claude-opus-4-5` (em `dispatch.py:DEFAULT_MODEL`) — desatualizado; Claude 4.6 disponível.

## Benchmark Tooling

Como medir `autonomous_completion_rate` em SDK mode:

```bash
# Pré-requisito: ANTHROPIC_API_KEY configurado no ambiente.

# 1. Instrumentação mínima (ainda não existe — proposta no Track Block):
#    Adicionar ao dispatch_block(): logging de attempt/success/error_type para
#    governance/dispatch-log.md

# 2. Medição por amostra:
#    python sdk/governor.py --block <NNN> --mode sdk
#    Observar se completa sem retry manual.
#    Repetir 10x em dias diferentes → taxa de sucesso observada.

# 3. Mock proxy (atual — só valida estrutura, não confiabilidade):
cd cognitive-arch
python -m pytest sdk/tests/test_dispatch.py -v
# Esperado: 22/22 passed (100% mock)

# 4. Teste de resiliência (a criar no Track Block):
#    Simular falha de API com mock que retorna erro em 30% das tentativas.
#    Verificar se retry recupera os casos.
```

End of track orquestracao-paralelismo.
