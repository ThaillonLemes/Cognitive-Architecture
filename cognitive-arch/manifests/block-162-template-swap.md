---
id: block-162
size: M
importance: critical
kind: refactor
phase: phase-29
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies: []
files:
  read:
    - design/block-phase-redesign.md
    - templates/manifest-small.md
    - templates/manifest-medium.md
    - templates/manifest-large.md
    - templates/block-retrospective.md
    - templates/manifest-small-v2.md
    - templates/manifest-medium-v2.md
    - templates/manifest-large-v2.md
    - templates/manifest-intake.md
    - templates/block-retrospective-v2.md
  modify:
    - sdk/audit.py
    - protocols/manifest-generation.md
  create:
    - sdk/tests/test_template_swap.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-162-template-swap.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_template_swap.py -q
    expect: "0 failed"
  - name: v1-removed
    type: manual
    checklist:
      - "templates/manifest-small.md não existe mais (foi removido ou renomeado)"
      - "templates/manifest-medium.md não existe mais"
      - "templates/manifest-large.md não existe mais"
      - "templates/block-retrospective.md não existe mais"
created_at: 2026-05-31
estimated_duration_hours: 2
---

# Block 162 — Template Swap: v1 → v2

- **Size:** M | **Importance:** critical
- **Kind:** refactor
- **Status:** pending

## 1. Purpose

Substituição formal dos templates imutáveis v1 pelos v2 aprovados em `design/block-phase-redesign.md`.
Os templates v2 já existem como rascunho. Este bloco usa `proposal_apply` para fazer o swap com
confirmação do Piloto e valida que o `audit.py` continua funcionando após a troca.

## 2. Dependencies

Nenhuma dependência de blocos anteriores.

## 3. Files

- **Read:** templates v1 (referência) + templates v2 (novos canônicos) + design doc
- **Modify:**
  - `sdk/audit.py` — atualizar qualquer referência hardcoded a templates v1
  - `protocols/manifest-generation.md` — apontar para templates v2
- **Create:**
  - `sdk/tests/test_template_swap.py` — valida que parsers do audit funcionam com v2

**Ação destrutiva (via proposal_apply):**
- Remover `templates/manifest-small.md` → substituído por `templates/manifest-small-v2.md`
- Remover `templates/manifest-medium.md` → substituído por `templates/manifest-medium-v2.md`
- Remover `templates/manifest-large.md` → substituído por `templates/manifest-large-v2.md`
- Remover `templates/block-retrospective.md` → substituído por `templates/block-retrospective-v2.md`

## 4. Validation

- `pytest sdk/tests/test_template_swap.py -v` → 0 failed
- `python sdk/audit.py --arch-root .` → sem erros relacionados a templates
- `ls templates/manifest-*.md` → lista só `-v2` variants + `manifest-intake.md`
- Manifests existentes (`manifests/block-*.md`) continuam sendo parseados corretamente

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`
- `v1-removed`: verificação manual que todos os templates v1 foram removidos

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `audit.py` hardcoded em nomes de templates v1 | High | Ler audit.py completamente antes do swap; atualizar referências |
| Manifests existentes incompatíveis com v2 | Med | v2 é compatível com v1 (adiciona campos, não remove) — validar no teste |

## 7. Out of Scope

- Conversão dos manifests existentes para usar novos campos v2 (isso é gradual, blocos futuros)
- Swap do `manifest-intake.md` (já é novo, sem v1 equivalente)

## 8. New Abstraction

None. Refactor puro — troca de arquivos, zero nova lógica.
