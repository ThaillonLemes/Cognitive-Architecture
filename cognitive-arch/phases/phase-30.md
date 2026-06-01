---
id: phase-30
status: planned
prev_phase: phase-29
exit_criteria_count: 6
blocks_count: 4
estimated_duration_minutes: 420
created_at: 2026-05-31
last_updated: 2026-05-31
owner: implementer
design_source: design/scanner.md
brainstorm_source: _brainstorm/scanner-v2-redesign.md
---

# Phase 30 — Scanner de Codebase

BRIEF: Implementa o scanner multi-nível (L0–L4) que lê codebases externas e persiste
um dossiê completo em `governance/project-profile-<cliente>.md`. Feature compartilhada
entre modo pessoal e corporativo. Fundação de tudo no modo corporativo — sem perfil,
não há consistência de código, não há padrão do time.

## 1. Purpose

O Piloto vai entrar em codebases que não são seus. Sem o scanner, precisa inferir padrões
manualmente — lento, impreciso, inconsistente. Com o scanner, tem um perfil persistente que:

1. Descreve a arquitetura, stack e lógica de domínio do projeto
2. Captura o "dialeto" do time (naming, imports, estilo, gestão de estado)
3. Detecta coexistência de padrões (vigente vs. legado)
4. Produz um HTML full dossier que o Piloto valida antes de implementar
5. Serve de input para o consistency checker (phase-29 / block-163)

## 2. Goals

- `sdk/codebase_scanner.py`: CLI principal com todas as flags (`--target-repo`, `--level`, `--context`, `--ticket`, `--area`, `--refresh-level`, `--client`, `--no-html`, `--arch-root`)
- `sdk/scanner_profile.py`: criação, atualização granular (por nível), leitura e multi-client do project-profile
- `sdk/scanner_deep.py`: detecção L2+L3+L4 (padrões arquiteturais, estilo, coexistência) + leitura de lógica de domínio
- `sdk/scanner_html.py`: gerador HTML full dossier (mapa, grafo de deps, prova de raciocínio, flags, custo)
- `sdk/scanner_adaptive.py`: pré-scan assessment, estimativa de custo de token, opções ao Piloto
- `sdk/scanner_ticket.py`: inferência de área a partir de texto de ticket + confirmação
- `sdk/tests/test_scanner_*.py`: suite de testes para todos os módulos
- `governance/project-profile-fixture.md` + `governance/scanner-output-fixture-*.html`: produzidos no dogfood

## 3. Invariants

- Scanner NUNCA armazena código real do cliente — só metadados, padrões, nomes, contagens
- Scanner NUNCA começa scan massivo sem exibir estimativa de custo e aguardar confirmação do Piloto
- `.gitignore` do projeto-alvo SEMPRE respeitado por padrão
- Relatório de cobertura emitido após cada scan: o que foi lido, o que foi excluído, por quê
- Relatório de custo de tokens emitido em todo scan (stdout + HTML footer)
- Todos os módulos têm `--arch-root` e `--help` funcionando sem crash em cp1252
- Suite verde após cada bloco (`pytest sdk/tests/ -q` → 0 failed)
- L3 e L4 devem estar no profile antes de qualquer run do consistency checker

## 4. Dependencies

- Phase 29 complete (fundação: block/phase redesign, tiers, estrutura base do mode corporativo)
- `governance/ux-config.yaml` existente com suporte a `html_output: true/false`
- Python ≥ 3.10 disponível no ambiente

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Custo de tokens maior que estimado no onboarding | Med | Pré-scan assessment obrigatório; baseline medida no dogfood (fixture) |
| Scanner não detecta padrão em projeto sem convenção de pasta | Med | Fallback: Claude lê arquivos-chave (Decision 4, Option C) |
| Leitura de lógica de negócio captura informação sensível | Med | Profile guarda só abstração (nomes, entidades, fluxos) — nunca trechos de código |
| HTML muito grande em projetos grandes | Low | Tamanho proporcional à área coberta; scan parcial por área reduz naturalmente |
| `--ticket` infere área errada | Low | Confirmação obrigatória antes de executar o scan; Piloto corrige |
| Projeto-alvo usa linguagem desconhecida | Low | Graceful degrade: L0/L1 universais; L2/L3 best-effort com aviso explícito |

## 6. Validation

- `pytest sdk/tests/ -q` → 0 failed após cada bloco
- Smoke test L0: `python sdk/codebase_scanner.py --target-repo <fixture> --level L0` gera `project-profile-fixture.md` com stack e domínio detectados
- Smoke test L2: `--ticket "implementar autenticação JWT"` infere área correta, confirma, atualiza perfil
- HTML gerado renderiza corretamente no browser com todas as seções obrigatórias
- Modo adaptativo: projeto com 500+ arquivos exibe pré-scan antes de qualquer leitura massiva
- Dogfood MMORPG: Piloto valida que o perfil gerado corresponde ao que ele sabe do projeto

## 7. Exit Criteria

1. `python sdk/codebase_scanner.py --target-repo <fixture> --level L0` gera `governance/project-profile-fixture.md` com stack, infra e lógica de domínio detectadas e corretas.
2. `python sdk/codebase_scanner.py --target-repo <path> --level L2 --ticket "texto"` infere a área, exibe confirmação ao Piloto, e atualiza o perfil com padrões detectados na área.
3. `governance/scanner-output-<cliente>-<timestamp>.html` gerado com todas as seções obrigatórias: mapa arquitetural, grafo de dependências, prova de raciocínio, flags de atenção, relatório de custo.
4. Modo adaptativo: projeto com 500+ arquivos exibe pré-scan assessment com estimativa de custo e aguarda confirmação antes de qualquer leitura massiva.
5. `--refresh-level L3` atualiza só a seção L3 do perfil sem apagar L0/L1/L2 (timestamps preservados).
6. Dogfood no MMORPG: perfil gerado é validado pelo Piloto como representação correta do projeto.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|---------|
| block-166 | Scanner Core — CLI + L0 + L1 + Profile | L · critical | planned | `manifests/block-166-scanner-core.md` |
| block-167 | Deep Scan — L2 + L3 + L4 + Business Logic | L · critical | planned | `manifests/block-167-scanner-deep.md` |
| block-168 | HTML Generator — Full Dossier | M · critical | planned | `manifests/block-168-scanner-html.md` |
| block-169 | Adaptive Mode + Ticket Inference + Profile Mgmt | M · normal | planned | `manifests/block-169-scanner-adaptive.md` |

## 9. Dependency Graph

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 1
  groups:
    - id: 30A
      blocks: [block-166]
      type: sequential
      depends_on: []
      note: "Core primeiro — cria CLI, profile foundation, L0+L1 scan"
    - id: 30B
      blocks: [block-167]
      type: sequential
      depends_on: [30A]
      note: "Deep scan lê e enriquece o profile criado no 166"
    - id: 30C
      blocks: [block-168, block-169]
      type: parallel
      depends_on: [30B]
      note: "HTML generator e adaptive mode são independentes entre si"
```

## 10. Out of Scope

- Consistency checker (phase-29 / block-163)
- Ticket intake e manifesto corporativo (phase-29)
- Multi-repo scan — um repo por sessão
- Integração com Jira/Linear API
- Análise de equipe, commits, autores (LGPD)
- Geração automática de PRs no repo da empresa
- GUI / dashboard interativo
