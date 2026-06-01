---
id: block-161
manifest: manifests/block-161-forecasts-reports.md
status: done
gates_passed: 4/4
completed_at: 2026-05-30T00:00Z
agent: implementer
commit: a4b1c5a
duration_actual_days: 1
actual_duration_hours: 2.0
duration_source: estimated
tok_estimated: ~4800
tok_src: estimated
---

# Block 161 Retrospective — Forecasts, relatórios & ruído de audit

## 1. What was built

- `sdk/phase_forecast.py`: regex de contagem de blocos ancorado (`^block-\d+`) para eliminar over-count por match em conteúdo arbitrário (HIGH-phase-block-counts-overcount).
- `sdk/velocity_inference.py`: trend de velocidade agora agrupa por tier antes de calcular média; evita distorção por mix de tiers (LOW-velocity-trend-tier-grouped).
- `sdk/risk_forecast.py`: `locate_manifest` retorna primeiro match exato de ID antes de fallback por prefixo; resolve ambiguidade em multi-match (LOW-locate-manifest-multi-match).
- `sdk/health_report.py`: cap de 600 bytes em seções H4 corrigido para 600 *chars* (não bytes) para suportar multibyte (LOW-h4-600-byte-cap).
- `sdk/audit.py`: pointer checker agora ignora âncoras internas (`#section`) em links relativos; elimina falsos positivos de doc (MEDIUM-pointer-false-positives-doc); base de resolução de path relativo corrigida para root do arquivo, não arch_root (MEDIUM-pointer-root-relative-base).
- `sdk/tests/test_phase_forecast.py`, `test_velocity_inference.py`: testes cobrindo os paths corrigidos.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| `test_block_count_anchored_regex` | unit | pass |
| `test_velocity_trend_grouped_by_tier` | unit | pass |
| `test_locate_manifest_exact_id_first` | unit | pass |
| `test_pointer_anchor_ignored` | unit | pass |
| `test_pointer_relative_base_correct` | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| tests-pass | ✓ | `pytest sdk/tests/ -q` 1060 passed, 0 failed |
| audit-pass | ✓ | `audit.py` PASS, 0 errors, score ≥90 |
| audit-strict | ✓ | `audit.py --strict` PASS |
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md atualizados |

## 4. Decisions made

- Pointer checker ignora âncoras de fragmento (`#`) — links internos válidos não são pointers para arquivos externos.

## 5. Deferred to future blocks

- dispatch.py, governor.py, notification_manager locks, block_close gate wiring → fase 29 (out-of-scope declarado).

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `sdk/phase_forecast.py` | ~5600 | ~1400 |
| `sdk/velocity_inference.py` | ~4800 | ~1200 |
| `sdk/audit.py` | ~4000 | ~1000 |
| `sdk/health_report.py` | ~4800 | ~1200 |

```
tok_estimated: ~4800  tok_src:estimated
```

## 7. Issues / surprises

- None.

## 8. Files actually touched

As manifest.

---

End of retrospective.
