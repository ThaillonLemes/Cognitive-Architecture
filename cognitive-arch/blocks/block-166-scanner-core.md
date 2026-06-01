---
id: block-166
manifest: manifests/block-166-scanner-core.md
status: done
gates_passed: 3/3
completed_at: 2026-06-01T00:20Z
agent: implementer
commit: ~
duration_actual_days: 1
actual_duration_hours: 3.0
duration_source: estimated
tok_estimated: ~5000
tok_src: estimated
wip_stage_reached: implementing
---

# Block 166 — Scanner Core: CLI + L0 + L1 + Profile

## 1. Summary

Núcleo do scanner implementado: CLI completo com todas as flags (--target-repo, --level, --client,
--context, --ticket, --area, --refresh-level, --no-html, --arch-root), scan L0 (macro arquitetural +
lógica de domínio) + L1 (estrutura e linguagens), e classe `ProjectProfile` para criação/leitura/update
granular do project-profile. Detecção de stack automática para Node/TS, Python, Go, Rust, JVM.

## 2. Gates

- [x] files-updated: STATE.md, NEXT.md, BLOCK_LOG.md atualizados
- [x] scope-clean: apenas arquivos declarados foram tocados
- [x] tests-pass: 7/7 pytest sdk/tests/test_scanner_core.py

## 3. What changed

| Arquivo | Mudança |
|---------|---------|
| sdk/codebase_scanner.py | Novo: CLI entry point, scan_l0(), scan_l1(), run_scan() |
| sdk/scanner_profile.py | Novo: ProjectProfile class com get/set_section, multi-client, validate_has_level |
| sdk/tests/test_scanner_core.py | 7 testes novos |

## 4. Decisions

- Profile stores only metadata (tipos, nomes, contagens) — teste explícito valida ausência de código real
- L0 e L1 sempre rodados juntos (economiza uma passada de arquivo)
- Stub calls para scanner_deep, scanner_html, scanner_adaptive com graceful ImportError fallback
- Stack detection via arquivos de config (package.json, pyproject, go.mod, etc.) — sem exec de comandos externos

## 5. Analytics

```yaml
analytics:
  complexity_felt: 3
  estimation_accuracy: on-track
  blockers: []
  rework_in_block: false
  pattern_learned: [graceful-stub-pattern]
```
