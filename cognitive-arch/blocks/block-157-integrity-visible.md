---
id: block-157
manifest: manifests/block-157-integrity-visible.md
status: done
gates_passed: 4/4
completed_at: 2026-05-30T00:00Z
agent: implementer
commit: a4b1c5a
duration_actual_days: 1
actual_duration_hours: 2.5
duration_source: estimated
tok_estimated: ~5600
tok_src: estimated
---

# Block 157 Retrospective — Integridade visível por padrão em toda a cadeia

## 1. What was built

- `sdk/integrity_check.py`: MISMATCH agora escala para ERROR (não WARN) no output padrão; `--strict` passa a falhar com exit code 1 quando há qualquer warning.
- `sdk/invariant_check.py`: INV1 bloqueante quando MISMATCH detectado em arquivo imutável.
- `sdk/session_start.py`: verificação de integridade agora roda por padrão (não só com flag explícito); `last_run` atualizado condicionalmente.
- `sdk/audit.py`: warnings >0 com `--strict` agora causa falha; legacy fallback logado visivelmente.
- `.integrity.lock`: regenerado após fix do MISMATCH em PROTOCOLS.md.
- `sdk/tests/test_integrity_check.py`, `test_invariant_check.py`, `test_invariant_gate.py`: testes cobrindo cada caminho novo.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| `test_mismatch_is_error_not_warn` | unit | pass |
| `test_strict_fails_on_warnings` | unit | pass |
| `test_inv1_blocks_on_mismatch` | unit | pass |
| `test_session_start_runs_integrity` | integration | pass |
| `test_last_run_conditional_update` | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| tests-pass | ✓ | `pytest sdk/tests/ -q` 0 failed |
| audit-pass | ✓ | `audit.py` PASS, 0 errors |
| audit-strict | ✓ | `audit.py --strict` falha se e somente se MISMATCH real |
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md, .integrity.lock atualizados |

## 4. Decisions made

- MISMATCH elevado para ERROR (bloqueante) em toda a cadeia — qualquer divergência de checksum impede operação silenciosa.

## 5. Deferred to future blocks

- Corrupção cp1252 no apply → block-158.

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `sdk/integrity_check.py` | ~7200 | ~1800 |
| `sdk/invariant_check.py` | ~6000 | ~1500 |
| `sdk/session_start.py` | ~5200 | ~1300 |
| `sdk/audit.py` | ~4000 | ~1000 |

```
tok_estimated: ~5600  tok_src:estimated
```

## 7. Issues / surprises

- PROTOCOLS.md tinha MISMATCH real no .integrity.lock (confirmado no bug hunt) — regeneração necessária como parte deste bloco.

## 8. Files actually touched

As manifest.

---

End of retrospective.
