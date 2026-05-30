---
id: block-160
phase: phase-28
title: Robustez CLI — encoding cp1252 & flag-as-path
tier: M
kind: fix
status: done
created_at: 2026-05-30
source: bug-hunt-2026-05-30
bugs_fixed: [HIGH-master-suggest-cp1252-crash, MEDIUM-weekly-report-stdout-cp1252, HIGH-pattern-analyzer-flag-as-path, MEDIUM-window-zero-returns-full]
files:
  modify:
    - sdk/master_suggest.py
    - sdk/weekly_report.py
    - sdk/pattern_analyzer.py
    - sdk/patterns_report.py
    - sdk/tests/test_pattern_analyzer_window.py
    - sdk/tests/test_cli_smoke.py
---

# block-160 — Robustez CLI: encoding cp1252 & flag-as-path

BRIEF: Dois CLIs crasham com `UnicodeEncodeError` sob cp1252 (`master_suggest --session/--demand`, `weekly_report --stdout`). `pattern_analyzer` lê `--arch-root` como literal path posicional e reporta 0 padrões silenciosamente. `_window(signals, 0)` retorna histórico completo em vez de vazio.

## Bugs corrigidos

### HIGH — `master_suggest.py` crasha UnicodeEncodeError sob cp1252
- **Arquivo:** `sdk/master_suggest.py` linhas 204, 209
- **Defeito:** `--session` e `--demand` imprimem emoji 🟠/🔴 via `print()` sem guard UTF-8; exit 1, sem output.
- **Fix:** Adicionar no topo do módulo: `from safe_io import force_utf8` + `force_utf8()` (ou inline `_fix_utf8()` como em `session_start.py`).
- **Teste:** `test_cli_smoke.py` — adicionar `master_suggest --session` e `master_suggest --demand` à lista de runs testados; executar sob `PYTHONIOENCODING=cp1252` (via monkeypatch de `sys.stdout`).

### MEDIUM — `weekly_report.py --stdout` crasha UnicodeEncodeError sob cp1252
- **Arquivo:** `sdk/weekly_report.py` linha 303
- **Defeito:** `--stdout` faz `print(render_html(report))` com emoji 📊 sem guard; caminho default (grava arquivo com `encoding='utf-8'`) é seguro mas `--stdout` não é. Smoke test só roda sem `--stdout`.
- **Fix:** Adicionar `from safe_io import force_utf8` + `force_utf8()` no import.
- **Teste:** `test_cli_smoke.py` — adicionar `weekly_report --stdout` ao smoke test; executar sob cp1252.

### HIGH — `pattern_analyzer.py` lê `--arch-root` como path posicional (flag-as-path)
- **Arquivo:** `sdk/pattern_analyzer.py` linha 234
- **Defeito:** `arch_root = Path(sys.argv[1]) if len(sys.argv) > 1 else ...` — sem argparse; `--arch-root cognitive-arch/` usa `sys.argv[1] = '--arch-root'` como path, analisa diretório inexistente, reporta `Signals: 0 | Patterns detected: 0` (exit 0, silencioso). Irmão exato do bug do ff0d219.
- **Fix:** Substituir por `argparse` espelhando `patterns_report.build_parser()`: `parser.add_argument('--arch-root', default='.')`, usar `args.arch_root`. Validar `arch_root.is_dir()` com erro claro se não existir.
- **Teste:** `test_cli_smoke.py` / `test_pattern_analyzer.py` — `pattern_analyzer.py --arch-root cognitive-arch/` com root real → `Signals > 0`.

### MEDIUM — `_window(signals, 0)` retorna histórico completo (off-by-one)
- **Arquivo:** `sdk/pattern_analyzer.py` linhas 22–26
- **Defeito:** `signals[-0:] == signals[0:]` (Python: `-0 == 0`); `len(signals) > 0` é True → retorna lista completa. `--window 0` desliga silenciosamente a janela em vez de retornar vazio.
- **Fix:** Após `if size is None: return signals`, adicionar `if size <= 0: return []`. Validar `--window` em `patterns_report.build_parser()` para rejeitar valores negativos e avisar em 0.
- **Teste:** `test_pattern_analyzer_window.py` — `_window(list(range(50)), 0)` → `[]`; `_window(list(range(50)), 5)` → 5 elementos.

## Arquivos a modificar

```yaml
files.modify:
  - sdk/master_suggest.py            # force_utf8()
  - sdk/weekly_report.py             # force_utf8()
  - sdk/pattern_analyzer.py          # argparse + _window(size=0) fix
  - sdk/patterns_report.py           # validar --window
  - sdk/tests/test_cli_smoke.py      # --session, --demand, --stdout sob cp1252
  - sdk/tests/test_pattern_analyzer_window.py  # _window(.,0)
```

## Gates de saída

- `PYTHONIOENCODING=cp1252 python sdk/master_suggest.py --arch-root . --demand` → exit 0, sem UnicodeEncodeError
- `PYTHONIOENCODING=cp1252 python sdk/weekly_report.py --arch-root . --stdout` → exit 0
- `python sdk/pattern_analyzer.py --arch-root cognitive-arch/` → `Signals > 0` (não zero silencioso)
- `_window(list(range(50)), 0)` → `[]`
- `python -m pytest sdk/tests/ -q` → 0 failed
