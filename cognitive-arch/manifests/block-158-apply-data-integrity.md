---
id: block-158
phase: phase-28
title: Corrupção de dados no apply & gate de verificação
tier: M
kind: fix
status: done
created_at: 2026-05-30
source: bug-hunt-2026-05-30
bugs_fixed: [C1-utf8-lossy-corrupt, LOW-re-sub-status-unanchored, LOW-run-verification-error-marker, LOW-test-hot-boot-red]
files:
  modify:
    - sdk/proposal_apply.py
    - sdk/tests/test_apply_e2e.py
    - INDEX.md
---

# block-158 — Corrupção de dados no apply & gate de verificação

BRIEF: O apply bem-sucedido corrompe silenciosamente arquivos cp1252 (bytes 0xE9 viram U+FFFD) porque lê com `errors='replace'` e regrava como UTF-8 — o apply *limpo* é exatamente o caso onde a corrupção é mantida permanentemente. Este bloco é o bug crítico C1.

## Bugs corrigidos

### C1 (CRITICAL) — UTF-8 lossy re-encode corrompendo arquivos
- **Arquivo:** `sdk/proposal_apply.py` linhas 602–604, 677, 289–299
- **Defeito:** `read_text(encoding='utf-8', errors='replace')` substitui bytes cp1252 válidos por U+FFFD; `_atomic_write` regrava como UTF-8; rollback só dispara em falha → apply limpo mantém corrupção.
- **Fix:** Não round-tripar o corpo via decode lossy. Estratégia: (a) ler como bytes (`read_bytes()`), detectar encoding (UTF-8 vs não-UTF-8), e para não-UTF-8 recusar o apply com mensagem clara OU (b) ler com `errors='surrogateescape'` e reescrever com o mesmo codec. Fix mínimo seguro: `original_bytes = target_path.read_bytes()` antes de qualquer decode; se `original_bytes != original_text.encode('utf-8')` então `abort("target is not valid UTF-8 — apply would corrupt it")`. Assim o apply é recusado em vez de silenciosamente corromper.
- **Teste:** `test_apply_e2e.py` — arquivo alvo com bytes `b'caf\xe9'` (válido cp1252, inválido UTF-8); apply deve ser recusado (não corromper e não aplicar).

### LOW — `_mark_proposal_applied` re.sub sem âncora corrompe Status em exemplos
- **Arquivo:** `sdk/proposal_apply.py` linha 799
- **Defeito:** `re.sub(r'\*\*Status:\*\*[^\n]*', '**Status:** applied', text)` sem count/âncora; reescreve TODA ocorrência de `**Status:**` no doc, incluindo linhas citadas em exemplos.
- **Fix:** Adicionar `count=1` e âncora de início de linha: `re.sub(r'(?m)^\*\*Status:\*\*[^\n]*', '**Status:** applied', text, count=1)`.
- **Teste:** Proposta com duas linhas `**Status:**` (uma em seção de resolução, outra em exemplo citado) → só a primeira é reescrita.

### LOW — `_run_verification` marker `"error"` causa rollback espúrio
- **Arquivo:** `sdk/proposal_apply.py` linhas 721–727, 772–778
- **Defeito:** `fail_markers=("failed", "error")` casa substring em nomes de teste e em `AssertionError` do pytest; apply válido rola back por causa de teste vermelho pré-existente ou nome de test function contendo "error".
- **Fix:** Usar word-boundary / regex ancorado na linha de summary do pytest: `re.search(r'\b\d+\s+(failed|error[s]?)\b', output, re.IGNORECASE)` em vez de substring simples. Alternativamente, confiar no exit code do pytest (0 = all green) e dropar o marker `"error"`.
- **Teste:** Mock pytest output com `"1 error in collection"` e `"0 failed"` → deve NÃO disparar rollback quando exit code é 0.

### LOW — `test_hot_boot_keeps_headroom` RED bloqueia todos os applies
- **Arquivos:** HOT files (CLAUDE.md, PROTOCOLS.md, STATE.md, NEXT.md, INDEX.md, board.md)
- **Defeito:** HOT boot = 3811 tok > 3800 (BUDGET - HEADROOM); teste vermelho bloqueia qualquer `proposal_apply confirm=True` na árvore atual.
- **Fix:** Trimar um ou mais HOT files para restaurar slack ≥ 200 tok (manter semântica, comprimir conteúdo redundante). Candidato prioritário: `INDEX.md` (verboso) ou `CLAUDE.md`.
- **Teste:** `test_boot_budget.py::test_hot_boot_keeps_headroom` → verde após trim.

## Arquivos a modificar

```yaml
files.modify:
  - sdk/proposal_apply.py              # _apply_proposal (UTF-8 guard), _mark_proposal_applied (re.sub), _run_verification (markers)
  - sdk/tests/test_apply_e2e.py        # teste cp1252 bytes → recused
  - cognitive-arch/INDEX.md            # ou CLAUDE.md — trim para < 3800 tok total HOT
  - sdk/tests/test_apply_guards.py     # teste re.sub Status
```

## Gates de saída

- `python -m pytest sdk/tests/test_boot_budget.py -q` → 4/4 passed (incluindo `test_hot_boot_keeps_headroom`)
- Repro C1: arquivo `b'caf\xe9'` → apply recusado (não corrompe)
- Repro re.sub: proposta com 2 `**Status:**` → só 1 linha alterada
- `python -m pytest sdk/tests/ -q` → 0 failed
