---
id: block-166
size: L
importance: critical
kind: implementation
phase: phase-30
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies: []
files:
  read:
    - design/scanner.md
    - governance/tools-registry.yaml
    - governance/ux-config.yaml
  modify:
    - governance/tools-registry.yaml
  create:
    - sdk/codebase_scanner.py
    - sdk/scanner_profile.py
    - sdk/tests/test_scanner_core.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-166-scanner-core.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_scanner_core.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 3
---

# Block 166 — Scanner Core: CLI + L0 + L1 + Profile

- **Size:** L | **Importance:** critical
- **Kind:** implementation
- **Status:** pending
- **Mode:** shared (pessoal + corporativo)

## 1. Purpose

Implementa o núcleo do scanner: CLI com todas as flags, leitura de L0 (macro arquitetural +
lógica de domínio) + L1 (estrutura e linguagens), e criação/leitura do project-profile.
É o bloco fundacional que os demais blocos da phase-30 estendem.

## 2. Dependencies

Nenhuma dependência de blocks anteriores nesta fase.
(Phase 29 completa é pré-requisito da fase, não do bloco individual.)

## 3. Files

- **Read:** `design/scanner.md`, `governance/tools-registry.yaml`, `governance/ux-config.yaml`
- **Modify:** `governance/tools-registry.yaml` (registrar novo tool)
- **Create:**
  - `sdk/codebase_scanner.py` — CLI entry point com argparse completo
  - `sdk/scanner_profile.py` — criação, leitura, update por seção, multi-client
  - `sdk/tests/test_scanner_core.py`

## 4. Validation

- `pytest sdk/tests/test_scanner_core.py -v` → 0 failed
- `python sdk/codebase_scanner.py --help` → exibe todas as flags sem crash
- `python sdk/codebase_scanner.py --target-repo <fixture> --level L0 --arch-root .` gera `governance/project-profile-fixture.md` com seção L0 (`scanned_at`, tipo, stack, infra, lógica de domínio) e seção L1 (linguagens, entry points, dependências)
- `--no-html` suprime geração de HTML

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Leitura de lógica de domínio captura código real | Med | `scanner_profile.py` armazena só abstrações — teste explícito que nenhum trecho de código aparece no profile |
| `.gitignore` do projeto-alvo não é lido corretamente | Low | Testar com fixture que tem `.gitignore` real incluindo `node_modules/` |

## 7. Out of Scope

- L2, L3, L4 (block-167)
- HTML generation (block-168)
- Adaptive mode / cost estimation (block-169)
- `--ticket` inference (block-169)

## 8. New Abstraction

**`ProjectProfile`** (em `scanner_profile.py`): classe que encapsula leitura, escrita e update
granular do `project-profile-<cliente>.md`. Justificativa: múltiplos módulos (scanner, checker,
HTML generator) precisam ler e escrever o perfil — abstração evita parsing duplicado.
