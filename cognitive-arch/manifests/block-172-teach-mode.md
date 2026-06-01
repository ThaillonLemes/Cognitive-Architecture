---
id: block-172
size: M
importance: critical
kind: implementation
phase: phase-31
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies:
  - block-170
parallel_with:
  - block-171
files:
  read:
    - design/pipeline.md
    - sdk/block_close.py
    - governance/ux-config.yaml
  modify:
    - sdk/block_close.py
    - governance/ux-config.yaml
  create:
    - sdk/teach_mode.py
    - sdk/tests/test_teach_mode.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-172-teach-mode.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_teach_mode.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 2
---

# Block 172 — Teach Mode

- **Size:** M | **Importance:** critical
- **Kind:** implementation
- **Status:** pending
- **Mode:** corporate + shared (ad-hoc pode ser chamado em qualquer modo)

## 1. Purpose

Implementa o teach mode — sempre obrigatório antes de fechar qualquer bloco de ticket.
O teach é o ponto de revisão final onde o Piloto confirma que entende o que foi feito.
Pode loopback para implementar. Gera 3 HTMLs por audiência + export textual. Dial de
abstração global configurável em ux-config.yaml.

## 2. Dependencies

- block-170 (estrutura do pipeline estabelecida; block_close.py já integrado pelo block-171)

## 3. Files

- **Read:** `design/pipeline.md`, `sdk/block_close.py`, `governance/ux-config.yaml`
- **Modify:**
  - `sdk/block_close.py` — garantir que `wip_stage: teaching` passa pelo teach mode antes de `done`
  - `governance/ux-config.yaml` — adicionar `abstraction_level`, `teach_html.*`, export settings
- **Create:**
  - `sdk/teach_mode.py` — gerador de 3 HTMLs, dial de abstração, export textual, prompt loopback
  - `sdk/tests/test_teach_mode.py`

## 4. Validation

- `pytest sdk/tests/test_teach_mode.py -v` → 0 failed
- `python sdk/teach_mode.py --block-id block-XXX --arch-root .` → 3 HTMLs gerados (technical, team, learning)
- Dial: `abstraction_level: leigo` → HTML sem jargão técnico; `tecnico` → decisões arquiteturais detalhadas
- `teach_html.team: false` → HTML de equipe não gerado; outros sim
- Export textual: arquivo de texto puro para cada HTML habilitado
- Loopback prompt: se Piloto escolhe B (retornar), bloco volta para `wip_stage: implementing`
- Ad-hoc: `python sdk/teach_mode.py --block-id block-XXX --level learning` funciona fora do pipeline
- `block_close.py`: bloco `kind: ticket` com `wip_stage: implementing` → rejeita `done` (exige teach primeiro)

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| 3 HTMLs muito similares entre si | Low | Cada HTML tem prompt de geração diferente (audiência explícita); Piloto desliga os redundantes |
| Teach obrigatório cria fricção percebida | Low | Design intencional — é o que garante qualidade. Sem teach, bloco não fecha. |
| Loopback cria ciclo infinito | Low | Sem limite automático de iterações; Piloto decide quando está satisfeito |

## 7. Out of Scope

- HTML do L0 do scanner ("teach do projeto") — já implementado na phase-30
- Integração de teach com histórico de decisões do Piloto (futura feature de pattern mining)

## 8. New Abstraction

**`TeachReport`**: dataclass com `technical_html`, `team_html`, `learning_html`, `text_exports`,
`loopback_requested` (bool). O `loopback_requested = True` sinaliza para `block_close.py` que
o bloco deve voltar para `wip_stage: implementing`.
