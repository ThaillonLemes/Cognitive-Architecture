---
id: block-156
phase: phase-28
title: Guards de imutabilidade & autorização de bump
tier: L
status: planned
created_at: 2026-05-30
source: bug-hunt-2026-05-30
bugs_fixed: [C2-basename-collision, LOW-end-marker-sticky, DISPUTED-integrity-ok-unlocked]
---

# block-156 — Guards de imutabilidade & autorização de bump

BRIEF: Fecha os furos de segurança no guard de imutabilidade do proposal_apply. O bug crítico é a colisão por basename em `_has_integrity_bump`: um bump aprovado para `GUIDE.md` desbloqueia qualquer `*/GUIDE.md` imutável. Reproduzido end-to-end (applied=True em arquivo errado). Este bloco é pré-requisito de 157 e 158.

## Bugs corrigidos

### C2 (CRITICAL) + HIGH — basename collision em `_has_integrity_bump`
- **Arquivo:** `sdk/proposal_apply.py` linhas 390 e 407–411
- **Defeito:** `if named == rel or Path(named).name == base:` — a cláusula de basename autoriza escrita em qualquer arquivo imutável que compartilhe o nome, independente de diretório.
- **Fix:** Remover `Path(named).name == base` e casar **só** pelo relpath POSIX normalizado: `if Path(named).as_posix() == rel: return True`.
- **Teste:** `test_apply_guards.py` — adicionar caso: bump para `templates/manifest-medium.md` NÃO autoriza `archive/manifest-medium.md`.

### LOW — END-marker sticky flag (`_has_integrity_bump`)
- **Arquivo:** `sdk/proposal_apply.py` linhas 382–383
- **Defeito:** `in_block` só fecha com `"END INTEGRITY BUMP"` no texto; marcador `--- END APPLY ---` da provenance NÃO fecha o bloco, vazando autorização para todo `file:` posterior no log.
- **Fix:** Também fechar `in_block` ao encontrar qualquer marcador `--- ... ---` que não contenha `INTEGRITY BUMP APPROVED`, ou ao abrir um novo bloco de qualquer tipo.
- **Teste:** `test_apply_guards.py` — cenário com log híbrido (bump + provenance block) confirma que file: dentro de APPLY APPLIED não conta como bump.

### DISPUTED — `_integrity_ok` retorna OK para imutável não-lockado
- **Arquivo:** `sdk/proposal_apply.py` linha 424
- **Decisão do Piloto:** implementar fail-safe (recusar e pedir integrity-bump) vs manter como está.
- **Se aprovado:** `if rel not in lock and _is_immutable(target_path): return False, "target is immutable but not in .integrity.lock — run integrity-bump first"`
- **Teste:** cenário com arquivo `protection: immutable` e `.integrity.lock` vazio retorna refused.

## Arquivos a modificar

```yaml
files.modify:
  - sdk/proposal_apply.py        # _has_integrity_bump, _integrity_ok
  - sdk/tests/test_apply_guards.py  # novos casos para todos os 3 bugs
```

## Gates de saída

- `python -m pytest sdk/tests/test_apply_guards.py -q` → 0 failed
- `python -m pytest sdk/tests/ -q` → 0 failed
- Repro original do bug C2 (`check_guards` com basename collision) → `allowed: False`
- Repro do sticky-flag → `_has_integrity_bump` retorna False para file: em bloco mal-terminado
