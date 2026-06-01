# Template: Manifest — kind:intake
# Criado em: 2026-06-01 (design/block-phase-redesign.md)
# Modo: corporate (intake é exclusivo do modo corporativo)

BRIEF: Primeiro bloco de um ticket corporativo. Lê o ticket, escaneia a área de toque na codebase,
e GERA o manifest do bloco de ticket (kind:ticket) como saída. Nunca modifica código do cliente.
Sempre size:XS. Duração típica: 20–40 minutos.

Copiar para `manifests/block-<NNN>-intake-<slug>.md`.

---

```yaml
---
id: block-<NNN>
size: XS
importance: normal                    # pode ser critical se o ticket é crítico
kind: intake
phase: phase-<N>
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies:
  - block-<NNN>                       # bloco anterior na fase, se houver
files:
  read:
    - <path_to_ticket_area>           # arquivos da área que o ticket vai tocar (scan L2/L3)
    - governance/project-profile-<client_id>.md    # perfil do cliente (se existir)
  modify:
    - manifests/block-<NNN+1>-<ticket-slug>.md     # O MANIFEST DO PRÓXIMO BLOCO É A SAÍDA
  create: []                          # intake NÃO cria código do cliente
gates:
  - name: manifest-generated
    type: file-changed
    paths: [manifests/block-<NNN+1>-<ticket-slug>.md]
    note: "O manifest do bloco de ticket deve existir e estar preenchido"
  - name: scope-clean
    type: fmod-check
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-<NNN>-intake-<slug>.md]
# [corporate — obrigatório em kind:intake]
ticket_id: ~                          # ID do ticket que está sendo interpretado
client_id: ~                          # herdado da fase
ticket_source: ~                      # texto livre | jira | linear | github
created_at: YYYY-MM-DD
---
```

---

# Block <NNN> — Intake: <Título do Ticket>

- **Size:** XS | **Importance:** normal | critical
- **Kind:** intake
- **Output:** manifest de `block-<NNN+1>` (bloco de ticket)

## 1. Ticket Input

Colar aqui o texto original do ticket (sem modificação):

```
<texto original do ticket>
```

## 2. Purpose

Uma frase: o que este intake vai produzir.

Exemplo: "Entender o ticket #JIRA-123, escanear a área de auth, e gerar o manifest do bloco de implementação."

## 3. Scan Plan (L2/L3)

Que área da codebase vai ser escaneada:
- **Módulo/pasta:** <onde o ticket vai mexer>
- **Nível:** L2 (padrões de arquitetura) + L3 (estética e convenções)
- **Ponto de integração:** <como o novo código vai se conectar ao existente>

## 4. Acceptance Criteria — Parsed

Extraídos do ticket (ou derivados quando o ticket é vago):

1. <critério 1 — mensurável>
2. <critério 2 — mensurável>
3. <edge case a cobrir>

## 5. Gates

- `manifest-generated`: o arquivo `manifests/block-<NNN+1>-<slug>.md` existe e tem todos os campos preenchidos
- `scope-clean`: nenhum arquivo de código foi modificado

## 6. Out of Scope

- **Não modifica código do cliente** — intake é leitura e geração de manifest apenas
- Implementação está no bloco seguinte (kind:ticket)

---

## OUTPUT: Manifest Gerado

*Preencher abaixo durante a execução do bloco. Este é o rascunho do manifest do bloco de ticket.*
*Após aprovação do Piloto, copiar para `manifests/block-<NNN+1>-<ticket-slug>.md`.*

```yaml
# manifests/block-<NNN+1>-<ticket-slug>.md (DRAFT — gerado pelo intake)
---
id: block-<NNN+1>
size: <S|M|L>                         # baseado na análise do ticket
importance: <normal|critical>
kind: ticket
phase: phase-<N>
scope: phase-bound
status: pending
wip_stage: ~
security: <true|false>
ticket_id: <ID>
acceptance_criteria: "<extraído/refinado do ticket>"
reviewer: <nome|to-define>
client_id: <client>
dependencies:
  - block-<NNN>                       # este intake
files:
  read:
    - <paths identificados no scan>
  modify:
    - <paths que o ticket vai modificar>
  create:
    - <paths novos>
gates:
  - name: functionality-check
    type: manual
    checklist:
      - "O acceptance_criteria está atendido?"
  - name: consistency-check
    type: script
    cmd: python sdk/consistency_checker.py --profile governance/project-profile-<client_id>.md
    expect: "consistency_score >= 0.80"
  - name: teach-ready
    type: manual
    checklist:
      - "Consigo explicar em 3 frases o que foi feito?"
      - "Consigo responder por que escolhi essa abordagem?"
      - "Consigo explicar o impacto para não-técnicos?"
  - name: scope-clean
    type: fmod-check
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: <YYYY-MM-DD>
---
```

End of manifest-intake template.
