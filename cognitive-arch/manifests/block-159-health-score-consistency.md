---
id: block-159
phase: phase-28
title: Consistência health/score entre ferramentas
tier: M
status: planned
created_at: 2026-05-30
source: bug-hunt-2026-05-30
bugs_fixed: [MEDIUM-warning-vs-degraded-label, MEDIUM-audit-silent-legacy-fallback, MEDIUM-stagnation-count-crash, LOW-health-unknown-scrape-fail, DISPUTED-measured-estimated-label]
---

# block-159 — Consistência health/score entre ferramentas

BRIEF: O mesmo score (80/100) aparece como "WARNING" no session_start e "DEGRADED" no health_report. O fallback legado de audit.score() diverge 50 pontos silenciosamente. `stagnation_count` não-numérico derruba o relatório inteiro. Este bloco unifica rótulos e score em uma única fonte.

## Bugs corrigidos

### MEDIUM — "WARNING" vs "DEGRADED" para o mesmo score
- **Arquivo:** `sdk/session_start.py` linha 427 vs `sdk/health_report.py` linhas 65–70
- **Defeito:** Mesmo threshold (≥70) mas palavras diferentes: `"WARNING"` vs `"DEGRADED"`. Score 82 lido como duas severidades distintas dependendo da ferramenta.
- **Fix:** Centralizar em `health_model.py` uma função `label_for(score: int) -> str` com vocabulário único (`HEALTHY/DEGRADED/CRITICAL`) e um `HealthLabel` enum opcional. Ambas as ferramentas chamam `health_model.label_for(score)`.
- **Teste:** `test_health_model.py` — `label_for(82) == label_for(82)` vindo de ambas as ferramentas; `label_for(89) == "DEGRADED"`, `label_for(90) == "HEALTHY"`, `label_for(69) == "CRITICAL"`.

### MEDIUM — fallback legado silencioso em `audit.score()` (gap de 50 pts)
- **Arquivo:** `sdk/audit.py` linhas 80–86
- **Defeito:** `except Exception: pass` engole qualquer falha de `health_model.compute()` e cai em `max(0, 100 - errors*15 - warnings*2)` — gap de 50 pontos (80 vs 30), sem nenhum sinal no output.
- **Fix:** Capturar exceção estreita (não bare `Exception`); na falha, emitir `WARN:` visível em output/log (como já faz `health_report._section_audit`). Se fallback for mantido, garantir que o número produzido é consistente com o de health_report (ambos numéricos ou ambos UNKNOWN).
- **Teste:** Monkeypatch `health_model.compute` para lançar `RuntimeError`; `audit.run_audit()` deve emitir warning visível e NÃO produzir score numérico silencioso divergente.

### MEDIUM — `stagnation_count` não-numérico derruba relatório inteiro
- **Arquivo:** `sdk/health_report.py` linha 365
- **Defeito:** `int(row.get("stagnation_count","0") or "0")` lança `ValueError` para valores como `"n/a"`, `"1.5"`, `"-"` — sem try/except, a exceção propaga e derruba `_section_track_health` inteira, e via cadeia chega ao session_start.
- **Fix:** Parse defensivo: `try: stagnation = int(raw) except (ValueError, TypeError): stagnation = 0`. Alternativamente, envolver `_section_track_health` em try/except como `_section_audit` já faz.
- **Teste:** `test_health_report_velocity.py` ou novo `test_health_consistency.py` — row com `stagnation_count: "n/a"` → relatório gera sem exception, seção de track mostra 0.

### LOW — health_report emite "Score: UNKNOWN" mas session_start regex não casa
- **Arquivo:** `sdk/audit.py:80-86` + `sdk/session_start.py` linha 424
- **Defeito:** No fallback de `health_model.compute()`, `health_report._section_audit` retorna string `"Score: UNKNOWN — health_model.compute failed"` mas `audit.score()` retorna um número legado; `session_start` faz `re.search(r'Score: (\d+)/100', text)` → None → linha Health some silenciosamente.
- **Fix:** Tornar os dois fallbacks consistentes: se audit emite número, health_report também deve (ou vice-versa). Regex de session_start deve casar o formato que qualquer um dos dois produzir. Resolvido naturalmente pelo fix do MEDIUM acima (emitir warning e manter scrape compatível).

### DISPUTED — label MEASURED/ESTIMATED desacoplado do valor usado
- **Arquivo:** `sdk/phase_forecast.py` linhas 204–213
- **Decisão do Piloto:** se aprovado, fazer `forecast()` derivar o label da `velocity_means` fornecida (não de re-medição local separada) quando caller passa `velocity_means`. Fix: aceitar `velocity_confidence` como argumento adicional ou re-medir localmente e usar os valores medidos também para `means`.

## Arquivos a modificar

```yaml
files.modify:
  - sdk/health_model.py              # adicionar label_for(score)
  - sdk/session_start.py             # usar health_model.label_for()
  - sdk/health_report.py             # usar health_model.label_for(); fix stagnation_count
  - sdk/audit.py                     # fallback estreito com warning visível
  - sdk/phase_forecast.py            # (se Piloto aprovar disputado)
  - sdk/tests/test_health_model.py
  - sdk/tests/test_health_consistency.py
```

## Gates de saída

- `health_model.label_for(80)` retorna mesmo string em session_start e health_report
- Monkeypatch compute() → audit emite warning visível (não score divergente silencioso)
- Row com `stagnation_count: "n/a"` → report sem exception
- `python -m pytest sdk/tests/ -q` → 0 failed
