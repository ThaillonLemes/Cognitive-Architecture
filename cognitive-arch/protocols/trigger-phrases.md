# Trigger phrases — full routing logic

BRIEF: Complete phrase tables and detection markers for AI auto-routing at session start. Referenced by `CLAUDE.md` (slim entry). Read this when you need the full phrase list or detection rules.

---

## Retrofit triggers (EXISTING project)

If the user's message contains ANY phrase below, AUTO-EXECUTE the retrofit flow without asking for confirmation.

| Trigger phrase (Portuguese) | Trigger phrase (English) |
|------------------------------|--------------------------|
| "quero integrar arquitetura cognitiva com [o] meu projeto" | "integrate cognitive architecture with my project" |
| "integrar arquitetura cognitiva" | "integrate cognitive architecture" |
| "configurar arquitetura cognitiva no meu projeto" | "set up cognitive architecture in my project" |
| "instalar arquitetura cognitiva" | "install cognitive architecture" |
| "adicionar arquitetura cognitiva" | "add cognitive architecture" |
| "retrofit do meu projeto" | "retrofit my project" |

**Action:** Read `RETROFIT.md` and execute the 10-step flow (Steps 0–9). Announce: "Detected: existing project + retrofit request. Reading RETROFIT.md and starting the analysis." Then begin Step 1 (read CLAUDE.md + PROTOCOLS + PROJECT + INDEX) and continue through the flow.

## Bootstrap triggers (NEW project)

| Trigger phrase (Portuguese) | Trigger phrase (English) |
|------------------------------|--------------------------|
| "começar novo projeto com arquitetura cognitiva" | "start new project with cognitive architecture" |
| "iniciar projeto do zero com arquitetura cognitiva" | "set up cognitive architecture from scratch" |
| "novo projeto" + "arquitetura cognitiva" | "new project" + "cognitive architecture" |

**Action:** Read `BOOTSTRAP.md` and execute the interactive Phase 0 flow.

## Generic greeting — auto-detect

| Trigger | Action |
|---------|--------|
| "oi", "olá", "hello", "hi" with WORKSPACE EMPTY (only cognitive-arch/ exists) | Treat as bootstrap. Read BOOTSTRAP.md. |
| "oi", "olá", "hello", "hi" with EXISTING CODE detected | Ask: "Vejo que tem código no projeto. Está adicionando a arquitetura cognitiva a um projeto existente, ou começando do zero?" Based on response, route to RETROFIT.md or BOOTSTRAP.md. |

## Brainstorm / Questionnaire triggers

If the user's message contains ANY phrase below (or the word "brainstorm" alone),
AUTO-EXECUTE the brainstorm v2 flow WITHOUT asking for confirmation.

| Trigger phrase (Portuguese) | Trigger phrase (English) |
|------------------------------|--------------------------|
| "brainstorm" (palavra isolada ou composta) | "brainstorm" |
| "fazer um brainstorm" | "do a brainstorm" |
| "vamos brainstormar" | "let's brainstorm" |
| "brainstorming" | "brainstorming" |
| "questionário" (sobre tema) | "questionnaire" |
| "motor de brainstorm" | "brainstorm engine" |
| "quero um brainstorm" | "I want a brainstorm" |
| "me faz um brainstorm" | "make me a brainstorm" |
| "brainstorm de [tema]" | "brainstorm about [topic]" |

**Action — executar obrigatoriamente, na ordem:**

1. Ler `protocols/brainstorm-pattern-v2.md` (protocolo completo v2).
2. Identificar o TOPIC a partir da mensagem do usuário (ex: "game design → sistemas de combate").
3. Carregar contexto: rodar `sdk/brainstorm_context.py` ou ler manualmente retros relevantes, padrões ativos (governance/patterns.md), ADRs relacionados, STATE.md fase atual.
4. Gerar as perguntas adequadas ao tópico (quantidade variável, regra P2).
5. Para cada pergunta: gerar recomendação + banda de confiança (🟢/🟡/🔴) + rationale com evidência.
6. Preencher o template `templates/brainstorm-v2-questionnaire.md` com as predições e salvar em `_brainstorm/<topic>-v2-questionnaire.md`.
7. Apresentar o questionário preenchido ao usuário para resposta.
8. Após respostas: executar síntese via `sdk/brainstorm_synthesis.py` → salvar em `design/<topic>.md`.

Anunciar: *"Detectado: brainstorm request. Lendo protocols/brainstorm-pattern-v2.md e iniciando fluxo v2."*

**NUNCA** fazer brainstorm em formato livre (lista de bullet points ad hoc).
**SEMPRE** usar o template v2 com recomendações, confiança e campo de resposta aberta.

## Code Review / Bugbot triggers

If the user's message contains ANY phrase below, AUTO-EXECUTE the code review flow WITHOUT asking for confirmation.

| Trigger phrase (Portuguese) | Trigger phrase (English) |
|------------------------------|--------------------------|
| "bugbot" | "bugbot" |
| "code review da fase" | "code review for the phase" |
| "revisar a fase" | "review the phase" |
| "review da fase" | "phase review" |
| "rodar o bugbot" | "run bugbot" |
| "analisar o diff" | "analyze the diff" |

**Action — executar obrigatoriamente, na ordem:**

1. Obter o diff atual: rodar `git diff HEAD~1 HEAD` ou `git diff --cached`.
2. Ler `governance/review-rules.md` para as regras ativas.
3. Rodar `python sdk/code_review.py --block-id <block_atual> --arch-root .`
   - Se diff disponível: passar via `--diff <arquivo>`.
4. Apresentar findings ao Piloto agrupados por severidade (security → bug → quality).
5. Para cada finding bloqueante: aguardar decisão do Piloto (fix | force | defer).
6. Atualizar status em `governance/bugs.md` conforme decisão.

Anunciar: *"Detectado: code review request. Executando bugbot via sdk/code_review.py."*

**NUNCA** bloquear automaticamente sem apresentar os findings ao Piloto.
**SEMPRE** logar findings em `governance/bugs.md` mesmo em modo force.

---

## How to detect existing code (quick check)

Glob in project root for any of these markers:

**Package manifests:**
- `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `pom.xml`, `CMakeLists.txt`, `Gemfile`, `composer.json`, `*.csproj`, `mix.exs`, `pubspec.yaml`

**Source folders:**
- `src/`, `app/`, `lib/`, `pkg/`, `cmd/`, `internal/`, `components/`

**Other signals:**
- `README.md` with substantive content (>50 lines)
- `.git/` with `git log` showing >1 commit

If ANY found → existing project (use RETROFIT).
If NONE found → new/empty project (use BOOTSTRAP).

---

End of trigger-phrases.md.
