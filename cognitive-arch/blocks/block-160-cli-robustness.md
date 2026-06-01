---
id: block-160
manifest: manifests/block-160-cli-robustness.md
status: done
gates_passed: 4/4
completed_at: 2026-05-30T00:00Z
agent: implementer
commit: a4b1c5a
duration_actual_days: 1
actual_duration_hours: 2.0
duration_source: estimated
tok_estimated: ~4000
tok_src: estimated
---

# Block 160 Retrospective — Robustez CLI: encoding cp1252 & flag-as-path

## 1. What was built

- `sdk/master_suggest.py`: stdout fixado para UTF-8 no Windows antes de qualquer saída (HIGH-master-suggest-cp1252-crash).
- `sdk/weekly_report.py`: mesmo fix de encoding UTF-8 no stdout (MEDIUM-weekly-report-stdout-cp1252).
- `sdk/pattern_analyzer.py`: `--arch-root` separado de patterns positional; argparse não mais confunde flag com path (HIGH-pattern-analyzer-flag-as-path).
- `sdk/patterns_report.py`: mesmo fix de argparse para `--arch-root`.
- `sdk/tests/test_pattern_analyzer_window.py`: cobertura do window zero retornando full range (MEDIUM-window-zero-returns-full).
- `sdk/tests/test_cli_smoke.py`: smoke tests para todos os CLIs com `--arch-root .` sob cp1252 simulado.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| `test_master_suggest_no_crash_cp1252` | integration | pass |
| `test_pattern_analyzer_arch_root_flag` | unit | pass |
| `test_patterns_report_arch_root_flag` | unit | pass |
| `test_window_zero_returns_all` | unit | pass |
| `test_help_no_crash[dispatch.py]` | smoke | pass |
| `test_help_no_crash[notification_manager.py]` | smoke | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| tests-pass | ✓ | `pytest sdk/tests/ -q` 0 failed |
| audit-pass | ✓ | `audit.py` PASS, 0 errors |
| cli-smoke | ✓ | todos os CLIs sobrevivem `--help` sob cp1252 |
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md atualizados |

## 4. Decisions made

- Fix de encoding aplicado no topo de cada CLI individualmente (não um wrapper global) — menor blast radius, mais fácil de auditar por arquivo.

## 5. Deferred to future blocks

- Forecasts & ruído de audit → block-161.

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `sdk/master_suggest.py` | ~4800 | ~1200 |
| `sdk/pattern_analyzer.py` | ~5200 | ~1300 |
| `sdk/patterns_report.py` | ~4400 | ~1100 |
| `sdk/tests/test_cli_smoke.py` | ~5600 | ~1400 |

```
tok_estimated: ~4000  tok_src:estimated
```

## 7. Issues / surprises

- None.

## 8. Files actually touched

As manifest.

---

End of retrospective.
