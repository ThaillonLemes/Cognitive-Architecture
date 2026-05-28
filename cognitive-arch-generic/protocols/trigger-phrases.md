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
