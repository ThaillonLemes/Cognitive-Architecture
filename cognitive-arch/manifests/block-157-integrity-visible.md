---
id: block-157
phase: phase-28
title: Integridade visível por padrão em toda a cadeia
tier: M
status: planned
created_at: 2026-05-30
source: bug-hunt-2026-05-30
bugs_fixed: [HIGH-mismatch-invisible, HIGH-session-start-no-strict, MEDIUM-audit-strict-warnings, HIGH-security-revalidation-unrunnable, MEDIUM-last-run-unconditional]
---

# block-157 — Integridade visível por padrão em toda a cadeia

BRIEF: PROTOCOLS.md tem SHA256 MISMATCH agora e o audit default passa (PASS, exit 0). Toda a cadeia (integrity_check, audit, session_start, INV1) é cega a isso. Este bloco torna qualquer MISMATCH em arquivo imutável visível e bloqueante sem precisar de `--strict`.

## Bugs corrigidos

### HIGH — MISMATCH em arquivo imutável invisível por padrão
- **Arquivo:** `sdk/integrity_check.py` linhas 164, 167–171
- **Defeito:** MISMATCH/MISSING → `WARN:` e exit 0 sem `--strict`; audit default classifica via `r.warn()`, não `r.err()`.
- **Fix:** Mapear não-OK **sempre** para `ERROR:` independente de `--strict`; mover `sys.exit(1)` para fora do guard de strict (MISMATCH sempre exit 1). Manter `--strict` só para escalar WARNs de outros checks.
- **Também:** Reforçar `INV1` em `sdk/invariant_check.py` para comparar hash (não só presença): `if lock.get(rel) != sha256(file): → CRITICAL`.
- **Teste:** `test_integrity_check.py` — MISMATCH sem `--strict` → exit 1 e `ERROR:` no output.

### HIGH — session_start chama integrity_check sem `--strict`
- **Arquivo:** `sdk/session_start.py` linha 166–167
- **Defeito:** `run_integrity_check` invoca `integrity_check.py --verify` sem `--strict` → sempre exit 0 → `ok=True`. Session_start reporta OK com arquivo adulterado.
- **Fix:** Passar `--strict` na chamada (após o fix acima, MISMATCH → exit 1 sem strict; ou parsear output por `MISMATCH`/`MISSING` e retornar `ok=False`). Imprimir contagem de arquivos com falha, não só primeira linha.
- **Teste:** Simular MISMATCH → session_start reporta integrity-check como FAILED (não Ran).

### MEDIUM — `audit --strict` não falha em warnings (bug de contrato)
- **Arquivo:** `sdk/audit.py` linhas 64–66, 440, 445
- **Defeito:** `AuditResult.passed = len(errors) == 0` ignora warnings e `strict`. Help diz "Fail on warnings too" mas não implementa. Só falha por acidente via integrity.
- **Fix:** `failed = (not result.passed) or (args.strict and len(result.warnings) > 0)`; alinhar `Result: PASS/FAIL` e exit code com essa condição.
- **Teste:** `test_cli_smoke.py` — `audit --strict` com warnings > 0 e errors == 0 → exit 1.

### HIGH — security-revalidation e conflicts-check nunca executam
- **Arquivo:** `sdk/session_start.py` linhas 257–266, 340–342
- **Defeito:** Ambos no registry (trigger_type: time, last_run: never) mas ausentes de `TOOL_RUNNERS`; sempre em "Skipped" indistinguível de "fresh".
- **Fix:** Adicionar runners mínimos para ambos (ou bucket "UNRUNNABLE/No runner" distinto), e mover check de staleness para antes do check de existência de runner no relatório.
- **Teste:** Verificar que tools com last_run "never" e sem runner aparecem em bucket separado no output de session_start.

### MEDIUM — health-report e dashboard-refresh têm last_run carimbado sem rodar
- **Arquivo:** `sdk/session_start.py` linhas 375–377
- **Defeito:** `_update_last_run` chamado incondicionalmente pós-loop mesmo quando "Ran: none"; corrompe `last_run` e `_detect_session_gap`.
- **Fix:** Remover carimbos incondicionais; só carimbar dentro do loop em execução bem-sucedida. Se devem sempre rodar, invocá-los de fato.
- **Teste:** Rodar session_start com todos os tools frescos → health-report.last_run NÃO muda.

## Arquivos a modificar

```yaml
files.modify:
  - sdk/integrity_check.py          # MISMATCH → ERROR, exit sem --strict
  - sdk/invariant_check.py          # INV1: comparar hash, não só presença
  - sdk/session_start.py            # --strict no integrity call, last_run fix, UNRUNNABLE bucket
  - sdk/audit.py                    # --strict gates warnings
  - sdk/tests/test_integrity_check.py
  - sdk/tests/test_invariant_check.py
  - sdk/tests/test_cli_smoke.py
```

## Gates de saída

- `python sdk/integrity_check.py --verify --arch-root .` com PROTOCOLS.md adulterado → exit 1, `ERROR:` no output
- `python sdk/audit.py --arch-root .` → agora deve reportar `Errors: 1` (PROTOCOLS.md MISMATCH é ERROR)
- `python sdk/audit.py --arch-root . --strict` com warnings → exit 1
- INV1 com hash errado → CRITICAL (não OK)
- `python -m pytest sdk/tests/ -q` → 0 failed
- Nota: após este bloco, `audit` vai reportar erro até que PROTOCOLS.md seja re-lockado (fix imediato pós-bloco: `python sdk/integrity_check.py --update --arch-root .` ou re-gerar o lock)
