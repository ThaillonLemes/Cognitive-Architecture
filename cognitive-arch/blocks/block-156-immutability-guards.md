---
id: block-156
manifest: manifests/block-156-immutability-guards.md
status: done
gates_passed: 4/4
completed_at: 2026-05-30T00:00Z
agent: implementer
commit: a4b1c5a
duration_actual_days: 1
actual_duration_hours: 3.0
duration_source: estimated
tok_estimated: ~4200
tok_src: estimated
---

# Block 156 Retrospective — Guards de imutabilidade & autorização de bump

## 1. What was built

- `sdk/proposal_apply.py`: corrigido `_has_integrity_bump` para comparar path completo relativo ao arch_root, eliminando a colisão por basename (bug C2).
- `sdk/proposal_apply.py`: corrigido sticky end-marker que permanecia após bump rejeitado (LOW-end-marker-sticky).
- `sdk/tests/test_apply_guards.py`: testes cobrindo colisão de basename, bump legítimo vs. colisão, e marker cleanup.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| `test_basename_collision_blocked` | unit | pass |
| `test_legitimate_bump_allowed` | unit | pass |
| `test_end_marker_cleared_on_reject` | unit | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| tests-pass | ✓ | `pytest sdk/tests/ -q` 0 failed |
| audit-pass | ✓ | `audit.py` PASS, 0 errors |
| integrity-ok | ✓ | immutable files unchanged |
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md updated |

## 4. Decisions made

- Basename comparison substituída por path relativo normalizado ao arch_root — decisão conservadora que preserva todos os casos legítimos de bump cobertos por testes.

## 5. Deferred to future blocks

- Visibility de MISMATCH na cadeia de integrity → block-157.
- Corrupção UTF-8 no apply → block-158.

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `sdk/proposal_apply.py` | ~8400 | ~2100 |
| `manifests/block-156-immutability-guards.md` | ~2400 | ~600 |
| `protocols/governor-dispatch.md` | ~2400 | ~600 |
| `sdk/tests/test_apply_guards.py` | ~3600 | ~900 |

```
tok_estimated: ~4200  tok_src:estimated
```

## 7. Issues / surprises

- DISPUTED-integrity-ok-unlocked decidido como não-bug: o guard de imutabilidade já rejeita corretamente quando não há bump válido; o caso "unlocked" era um falso positivo do hunt.

## 8. Files actually touched

As manifest.

---

End of retrospective.
