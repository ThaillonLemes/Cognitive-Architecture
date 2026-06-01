---
id: block-159
manifest: manifests/block-159-health-score-consistency.md
status: done
gates_passed: 4/4
completed_at: 2026-05-30T00:00Z
agent: implementer
commit: a4b1c5a
duration_actual_days: 1
actual_duration_hours: 2.0
duration_source: estimated
tok_estimated: ~4400
tok_src: estimated
---

# Block 159 Retrospective — Consistência health/score entre ferramentas

## 1. What was built

- `sdk/health_model.py`: `label_for(score)` como fonte única de label (WARNING/DEGRADED/HEALTHY); todas as ferramentas delegam para este método (MEDIUM-warning-vs-degraded-label).
- `sdk/audit.py`: legacy fallback agora loga WARN visível antes de usar estimativa local; score delegado a health_model como padrão (MEDIUM-audit-silent-legacy-fallback).
- `sdk/health_report.py`: crash em `stagnation_count` quando lista vazia corrigido (MEDIUM-stagnation-count-crash).
- `sdk/session_start.py`: scrape do health label atualizado para usar regex compatível com novo `label_for()`.
- `sdk/tests/test_health_model.py`, `test_health_consistency.py`: cobertura dos novos caminhos.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| `test_label_for_all_tiers` | unit | pass |
| `test_audit_uses_health_model_label` | integration | pass |
| `test_stagnation_count_empty_list` | unit | pass |
| `test_session_start_scrape_label` | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| tests-pass | ✓ | `pytest sdk/tests/ -q` 0 failed |
| audit-pass | ✓ | `audit.py` PASS, 0 errors |
| label-unified | ✓ | health_model, audit, session_start retornam mesmo label |
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md atualizados |

## 4. Decisions made

- `label_for()` em health_model como única fonte de verdade para labels — elimina divergência entre ferramentas sem acoplamento circular (audit importa health_model com lazy import).
- DISPUTED-measured-estimated-label: decidido como não-bug — rótulo "estimated" é correto para tok_src quando não há API key.

## 5. Deferred to future blocks

- Robustez CLI cp1252 → block-160.

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `sdk/health_model.py` | ~7200 | ~1800 |
| `sdk/session_start.py` | ~5200 | ~1300 |
| `sdk/health_report.py` | ~4800 | ~1200 |
| `sdk/audit.py` | ~4000 | ~1000 |

```
tok_estimated: ~4400  tok_src:estimated
```

## 7. Issues / surprises

- None.

## 8. Files actually touched

As manifest.

---

End of retrospective.
