---
id: block-161
phase: phase-28
title: Forecasts, relatórios & ruído de audit
tier: M
kind: fix
status: done
created_at: 2026-05-30
source: bug-hunt-2026-05-30
bugs_fixed: [HIGH-phase-block-counts-overcount, LOW-velocity-trend-tier-grouped, LOW-locate-manifest-multi-match, LOW-h4-600-byte-cap, MEDIUM-pointer-false-positives-doc, MEDIUM-pointer-root-relative-base]
files:
  modify:
    - sdk/phase_forecast.py
    - sdk/health_report.py
    - sdk/velocity_inference.py
    - sdk/risk_forecast.py
    - sdk/audit.py
    - sdk/tests/test_phase_forecast.py
    - sdk/tests/test_velocity_inference.py
---

# block-161 — Forecasts, relatórios & ruído de audit

BRIEF: `phase_block_counts()` usa regex sem âncora que over-conta blocos mencionados em prose (phase-26 lê 5/4, phase-24 lê 6/4 → gera data futura falsa para fases concluídas). `check3_pointer_integrity` gera falsos positivos em links ilustrativos e root-relative. Tendência de velocity é tier-grouped, não cronológica.

## Bugs corrigidos

### HIGH — `phase_block_counts()` over-conta por regex não-ancorado
- **Arquivo:** `sdk/phase_forecast.py` linhas 87–93
- **Defeito:** `re.findall(r'\|\s*block-\d+', content)` e `re.findall(r'\|\s*done\s*\|', content)` varrem o arquivo inteiro sem âncora; casam células de prosa (tabela de Riscos). Phase-26: 5/4, phase-24: 6/4 → `remaining = 1` → data futura falsa para fase concluída.
- **Fix:** Ancorar a início de linha: `re.findall(r'(?m)^\s*\|\s*block-\d+\s*\|', content)` para total; derivar done contando linhas do mesmo padrão que contêm `\|\s*done\s*\|`. Ou iterar linha-a-linha o subset da tabela de blocos.
- **Teste:** `test_phase_forecast.py` — phase com `block-NNN` em célula de Riscos → `total_count == n_real_block_rows` (não n+1).

### LOW — tendência de velocity usa lista tier-grouped, não cronológica
- **Arquivo:** `sdk/health_report.py` linhas 206–216
- **Defeito:** `all_durations = [d for tier in by_tier.values() for d in tier]` → S→M→L fixo; `[-5:]` é cauda da lista L, não os 5 blocos mais recentes. IMPROVING/DECLINING sem relação com tempo real.
- **Fix:** Coletar `(block_id, duration)` em ordem de BLOCK_LOG (que já é cronológica) em uma única lista plana, então fatiar `[-5:]` vs `[-10:-5]` disso.
- **Teste:** `test_health_report_velocity.py` — 10 blocos com S rápidos recentes e L lentos antigos → trend = IMPROVING (não DECLINING como hoje).

### LOW — `_locate_manifest` retorna primeiro de múltiplos matches (não-determinístico)
- **Arquivo:** `sdk/velocity_inference.py` linhas 90–96
- **Defeito:** Docstring: "exactly one else None"; impl: `candidates[0]` em ordem de `glob()` não-garantida. Com 2+ arquivos para o mesmo block_id, retorna manifest errado não-deterministicamente.
- **Fix:** Honrar docstring: `return candidates[0] if len(candidates) == 1 else None`. Se first-match intencional: `sorted(candidates)[0]` + corrigir docstring.
- **Teste:** Criar 2 arquivos `block-086-a.md` e `block-086-b.md` → `_locate_manifest('block-086', root)` retorna `None`.

### LOW — H4 `risk_forecast` lê só 600 bytes, diverge de `integrity_check.is_immutable_text`
- **Arquivo:** `sdk/risk_forecast.py` linhas 209–239
- **Defeito:** `head = p.read_text(...)[:600]`; arquivo com `protection: immutable` após byte 600 → H4 não dispara, mas `integrity_check.is_immutable_text` (ilimitado) sim. Subaviso silencioso.
- **Fix:** Substituir `[:600]` pela chamada canônica: `from integrity_check import is_immutable_text; if is_immutable_text(p.read_text(...)): ...`. Unificar também o `[:500]` em `proposal_resolver._is_immutable` para a mesma helper.
- **Teste:** Arquivo com `protection: immutable` após byte 600 → H4 dispara.

### MEDIUM — `check3_pointer_integrity` gera falsos positivos em links ilustrativos
- **Arquivo:** `sdk/audit.py` linhas 149–169
- **Defeito:** `_MD_LINK_RE` sobre texto cru de todo `.md` sem excluir code-fences/inline-code; `protocols/pointer-integrity.md` produz 4–5 WARNs de links ilustrativos (`path/to/file.md`, `design/combat.md`) que são placeholders intencionais.
- **Fix:** Remover blocos fenced (````...````) e inline code (`` `...` ``) do texto antes de escanear. Adicionar suporte a marcador `<!-- audit:ignore-links -->` por arquivo.
- **Teste:** `test_cli_smoke.py` ou `test_audit.py` — `audit --arch-root .` não reporta WARNs para `protocols/pointer-integrity.md`.

### MEDIUM — `check3` resolve links só via `md_file.parent`, falha em root-relative
- **Arquivo:** `sdk/audit.py` linha 164
- **Defeito:** `resolved = (md_file.parent / target).resolve()` sem fallback para arch_root; `governance/proposals/index.md` com links root-relative gera segmento duplicado (`governance/proposals/governance/proposals/...`) → 3 falsos WARNs.
- **Fix:** Tentar múltiplas bases: `resolved = (md_file.parent / target)` E `(arch_root / target)` → válido se qualquer uma existir.
- **Teste:** Link root-relative em arquivo dentro de subdiretório → não gera WARN.

## Arquivos a modificar

```yaml
files.modify:
  - sdk/phase_forecast.py            # regex ancorado para block rows
  - sdk/health_report.py             # tendência cronológica
  - sdk/velocity_inference.py        # _locate_manifest: len==1 guard
  - sdk/risk_forecast.py             # H4: is_immutable_text canônico
  - sdk/proposal_resolver.py         # _is_immutable: usar helper canônico (mesmo que risk_forecast)
  - sdk/audit.py                     # check3: excluir fenced/inline; multi-base resolve
  - sdk/tests/test_phase_forecast.py
  - sdk/tests/test_velocity_inference.py
  - sdk/tests/test_risk_forecast.py
```

## Gates de saída

- Phase-26 e phase-24: `phase_block_counts()` retorna `(done=4, total=4)` (não 5 ou 6)
- `_locate_manifest` com 2 arquivos → `None`
- H4 com `protection: immutable` após byte 600 → dispara warning
- `audit --arch-root .` não reporta WARNs para `protocols/pointer-integrity.md`
- `audit --arch-root .` não reporta WARNs para links root-relative válidos em `governance/proposals/index.md`
- `python -m pytest sdk/tests/ -q` → 0 failed
- Score do audit sobe de 80 para ≥ 90 (após remover todos os falsos positivos e fixes dos outros blocos)
