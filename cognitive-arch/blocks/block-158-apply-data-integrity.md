---
id: block-158
manifest: manifests/block-158-apply-data-integrity.md
status: done
gates_passed: 4/4
completed_at: 2026-05-30T00:00Z
agent: implementer
commit: a4b1c5a
duration_actual_days: 1
actual_duration_hours: 2.0
duration_source: estimated
tok_estimated: ~3800
tok_src: estimated
---

# Block 158 Retrospective — Corrupção de dados no apply & gate de verificação

## 1. What was built

- `sdk/proposal_apply.py`: leitura e escrita de arquivos agora preserva encoding original (bytes lidos → bytes escritos, sem round-trip UTF-8 forçado); bug crítico C1 (cp1252 0xE9 → U+FFFD) eliminado.
- `sdk/proposal_apply.py`: regex de status unanchored corrigido para `^status:` (LOW-re-sub-status-unanchored).
- `sdk/proposal_apply.py`: error marker de `run_verification` agora sempre gravado antes de relançar exceção (LOW-run-verification-error-marker).
- `sdk/tests/test_apply_e2e.py`: teste `test_hot_boot_keeps_headroom` adicionado (LOW-test-hot-boot-red).
- `INDEX.md`: ajuste de pointer documentando nova semântica de encoding.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| `test_cp1252_bytes_preserved_after_apply` | unit | pass |
| `test_status_regex_anchored` | unit | pass |
| `test_error_marker_written_on_exception` | unit | pass |
| `test_hot_boot_keeps_headroom` | integration | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| tests-pass | ✓ | `pytest sdk/tests/ -q` 0 failed |
| audit-pass | ✓ | `audit.py` PASS, 0 errors |
| integrity-ok | ✓ | immutable files unchanged |
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md atualizados |

## 4. Decisions made

- Apply preserva encoding original (bytes) em vez de normalizar para UTF-8 — decisão conservadora que elimina risco de corrupção silenciosa em qualquer encoding.

## 5. Deferred to future blocks

- Consistência de health/score entre ferramentas → block-159.

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `sdk/proposal_apply.py` | ~8400 | ~2100 |
| `sdk/tests/test_apply_e2e.py` | ~6800 | ~1700 |

```
tok_estimated: ~3800  tok_src:estimated
```

## 7. Issues / surprises

- None.

## 8. Files actually touched

As manifest.

---

End of retrospective.
