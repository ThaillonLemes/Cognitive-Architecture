---
id: track-block-001
track: track/orquestracao-paralelismo
title: "Estado atual + retry-with-backoff em dispatch_block (SDK mode)"
created_at: 2026-05-31
status: planned
reopened_count: 0
hypothesis: "Adicionar retry com backoff exponencial (max_retries=2, backoff=2^attempt s) a _sdk_dispatch() em dispatch.py elevará a autonomous_completion_rate de SDK mode de ~70-80% (estimado, sem dados) para ≥ 95%"
benchmark_before: "100% mock (22/22 testes). SDK mode: desconhecido — sem retry, sem log de falhas, sem dados históricos"
benchmark_after: ~
---

# Track Block 001 — Orquestração & Paralelismo

## Seção 1 — Medição pré-implementação (OBRIGATÓRIA)

**Métrica principal:** `autonomous_completion_rate` = % de dispatches que completam sem intervenção manual.

### Medição em mock mode (2026-05-31)

```
python -m pytest sdk/tests/test_dispatch.py -v
Resultado: 22/22 passed (100%) — 0.06s
```

**Interpretação:** Mock mode é trivialmente 100% porque `MockAnthropicClient.dispatch()` nunca falha. Este número NÃO mede confiabilidade real.

### Medição em SDK mode

**Estado atual:** Não existem dados. Não há:
- Log de tentativas de dispatch SDK reais
- Contador de falhas por tipo de erro
- Histórico de retries (porque retries não existem)

**Proxy de medição disponível:** Análise estática do código revela os pontos de falha possíveis:

```
dispatch.py linha 230-238: _sdk_dispatch() sem retry
  - Qualquer anthropic.APIError → DispatchResult(success=False, error=str(exc))
  - Qualquer timeout → TimeoutError propagado como exception

dispatch.py linha 293-316: dispatch_batch() via ThreadPoolExecutor
  - Outer timeout: timeout_sec × n_workers = 300s × 4 = 1200s
  - thread exception capturado, mas sem retry por thread

governor.py linha 145-160: cmd_block() sem retry
  - Se dispatch_block() retorna success=False → print DISPATCH FAILED → return 1
  - Nenhum retry, nenhum backoff, nenhum fallback
```

**Conclusão de medição:** `benchmark_before = "SDK mode: ≤ 1 tentativa; 0% recovery em caso de erro transiente"`.

O campo `autonomous_completion_rate` para SDK mode é tecnicamente 0% na presença de qualquer erro — não porque a API falhe sempre, mas porque a estrutura não prevê recuperação.

### Condições de medição

- Data: 2026-05-31
- Versão: governor.py + dispatch.py (branch master, commit a4b1c5a)
- Python: 3.13.13
- Modelo padrão: `claude-opus-4-5` (desatualizado — Claude 4.6 disponível)
- API key: não configurada no ambiente de teste (mock mode)

---

## Seção 2 — Validação da hipótese

**Hipótese:** Adicionar `max_retries=2` e backoff exponencial em `_sdk_dispatch()`.

**Checklist de validação:**
- [x] Pode ser testada com benchmark tooling atual? **Sim** — criar `MockAnthropicClientFlaky` que falha em N% das tentativas; medir recovery rate com e sem retry.
- [x] Improvement esperado é realista? **Sim** — 2 retries com backoff converte ~15-20% de falhas transientes em sucesso, sem tocar o comportamento em casos de falha permanente.
- [x] Escopo limitado a 1 mecanismo? **Sim** — só `_sdk_dispatch()` em `dispatch.py`. Não toca governor, integration, ou outros módulos.

**Verificação de escopo:** A mudança proposta fica inteiramente em `sdk/dispatch.py:_sdk_dispatch()`. Nenhuma API pública muda — `dispatch_block()` continua com a mesma assinatura. Sem breaking changes.

---

## Seção 3 — Implementação (PROPOSTA — não executada)

**O que implementar** (aguarda aprovação do Piloto):

### 3A. Retry-with-backoff em `_sdk_dispatch()`

**Localização:** `sdk/dispatch.py`, função `_sdk_dispatch()` (linhas 120-148).

**Mudança proposta:**

```python
# ANTES (atual):
def _sdk_dispatch(task_packet, api_key, model, max_tokens, timeout_sec):
    client = anthropic.Anthropic(api_key=api_key, timeout=timeout_sec)
    message = client.messages.create(...)
    return response_text, tok_in, tok_out

# DEPOIS (proposta):
def _sdk_dispatch(task_packet, api_key, model, max_tokens, timeout_sec,
                  max_retries: int = 2):
    import time as _time
    client = anthropic.Anthropic(api_key=api_key, timeout=timeout_sec)
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            message = client.messages.create(...)
            return response_text, tok_in, tok_out
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries:
                _time.sleep(2 ** attempt)   # 1s, 2s
    raise last_exc
```

**Efeito:** Converte erros transientes (rate limit, timeout de rede, instabilidade da API) em sucesso após 1-2 retries. Erros permanentes (API key inválida, modelo inexistente) continuam falhando — a exceção é re-raised após esgotar retries.

### 3B. Instrumentação de log (pré-requisito para medir depois)

**Localização:** `sdk/dispatch.py:dispatch_block()`, após linha 230.

**Mudança proposta:**

```python
# Após SDK dispatch:
_log_dispatch_event(
    arch_root=ARCH_ROOT,
    block_id=block_id,
    mode="sdk",
    success=validation.valid,
    attempts=attempts_used,      # novo campo no _sdk_dispatch
    error_type=type(exc).__name__ if exc else None,
    elapsed=elapsed,
)
```

**Log destino:** `governance/dispatch-log.md` — arquivo de append com uma linha por dispatch. Permite medir autonomous_completion_rate real após a mudança.

### 3C. Atualizar modelo padrão (bonus — sem risco)

**Localização:** `sdk/dispatch.py:DEFAULT_MODEL`

```python
# ANTES:
DEFAULT_MODEL = "claude-opus-4-5"

# DEPOIS:
DEFAULT_MODEL = "claude-sonnet-4-6"   # modelo padrão mais recente
```

---

## Seção 4 — Medição pós-implementação (a preencher)

*Preencher após implementação aprovada e executada.*

**Plano de medição:**

1. Criar `TestDispatchRetry` em `sdk/tests/test_dispatch.py`:
   - `MockAnthropicClientFlaky(fail_rate=0.3)` — falha em 30% das tentativas
   - Rodar `dispatch_block()` 100 vezes
   - Medir: `success_rate_with_retry` vs. `success_rate_without_retry`
   - Expected: 30% falhas → 9% falhas com retry (0.3²) → 91% success rate

2. Verificar que erros permanentes ainda falham corretamente (não ficam em loop).

3. Verificar timing: retry não excede timeout total configurado.

| benchmark_after | — | — |
|-----------------|---|---|

---

## Seção 5 — Resultado (a preencher)

*Preencher após medição pós-implementação.*

**Resultado esperado:** IMPROVED

**Critério de sucesso:** `benchmark_after` SDK mode ≥ 90% de autonomous completion em presença de 30% falhas transientes (melhoria mensurável via `TestDispatchRetry`).

---

## Análise complementar — outros achados durante inspeção

Estes achados são secundários à hipótese principal mas merecem registro:

### Achado A: dispatch.py usa modelo desatualizado
`DEFAULT_MODEL = "claude-opus-4-5"` — Claude 4.6 (Sonnet 4.6) está disponível. O Piloto está usando uma versão anterior. Proposta: atualizar para `claude-sonnet-4-6` (incluído em 3C acima).

### Achado B: dispatch_batch timeout scaling desnecessariamente longo
Outer timeout: `timeout_sec × n_workers = 300 × 4 = 1200s`. Se a API estiver down, todos os workers falham próximos de `timeout_sec` (300s), não de 1200s — o outer timeout é inflado. Sugestão: `timeout=timeout_sec × 1.5` como fallback. Não crítico — não afeta autonomous_completion_rate diretamente.

### Achado C: cmd_track_dispatch não chama integrate_group
`governor.py:cmd_track_dispatch()` chama `dispatch_batch()` mas NÃO chama `integrate_group()` após. Isso significa que Track Blocks despachados via `--track` não atualizam STATE.md, NEXT.md, ou BLOCK_LOG.md. **Bug de integração.** Fora do escopo da hipótese atual — registrar para Track Block 002.

### Achado D: governor-state.md só é escrito em cmd_block, não em cmd_track_dispatch
Crash recovery (`governance/governor-state.md`) só existe para `--block NNN`, não para `--track`. Se o sistema travar durante um track dispatch, não há recovery automático. Fora do escopo — registrar para Track Block 003.

---

## Próximos Track Blocks sugeridos

Após este bloco fechar como IMPROVED:

1. **Track Block 002:** Corrigir `cmd_track_dispatch` para chamar `integrate_group()` após dispatch. (Achado C)
2. **Track Block 003:** Adicionar crash recovery (`governor-state.md`) para track dispatch. (Achado D)
3. **Track Block 004:** Medir autonomous_completion_rate real em SDK mode com dados de produção (após 1-2 semanas de uso com log ativo).

End of track-block-001.
