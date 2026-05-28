# BOOTSTRAP — first-session interactive flow (new projects)

BRIEF: this file guides the AI through the first session of a NEW (empty) project. For projects that ALREADY have code, use `RETROFIT.md` instead.

## When to run BOOTSTRAP (vs RETROFIT)

Read BOOTSTRAP when ALL of:
- The project has NO source code outside `cognitive-arch/`
- `STATE.md` has `status:bootstrap`
- `PROJECT.md` has unfilled placeholders

Read **RETROFIT.md** instead when ANY of:
- The project has existing source code (`src/`, `app/`, `lib/`, etc.)
- Existing docs (README.md beyond a placeholder, ARCHITECTURE.md, etc.)
- Git history with real development activity
- Existing tests, build scripts, CI

If unsure: ask the user "Is this a brand-new project from zero, or an existing project?"

## When to run (after the distinction)

If it IS a new project, BOOTSTRAP runs when ANY of:
- User says "oi", "hello", "hi", "começar", "let's start", or similar opener
- User explicitly asks: "where do we start?", "what do I do first?"

## Mode for this flow

Use `guidance` mode (see `protocols/modes.md`). Conversational, friendly, ask one thing at a time. This is the ONE place where chatty is correct.

## Flow

### Step 0 — Greet and orient

Greet the user. Briefly explain what this is (1-2 sentences):
> "This is a cognitive architecture for AI-assisted projects. We'll set up your project together — first identity, then domain, then your first block of work. Take 10-15 minutes."

Offer a quick tour:
> "Want a 2-minute tour of the structure, or jump straight to Phase 0?"

If tour: walk through the folder map (from `README.md`), highlight `phases/`, `manifests/`, `design/`, `commands/`. Then move on.

### Step 1 — Fill PROJECT.md (project identity)

Ask the user, one question at a time. Confirm understanding before writing.

1. "What's the project name?"
2. "What type is it? (web app, SaaS, game, CLI, library, mobile, desktop, other)"
3. "What's the primary language? (e.g., TypeScript, Python, Rust, Go, C++)"
4. "What framework, if any? (e.g., Next.js, FastAPI, Bevy)"
5. "What's the build command?"
6. "What's the test command?"
7. "What's the lint command?"
8. "Describe the project in one paragraph — what does it deliver?"
9. "Who are the target users? Be specific."
10. "What are the key constraints? (performance, security, compliance, latency, etc.)"

After all 10 answers, write `PROJECT.md` with the filled values. Update `STATE.md` to reflect `status:active`.

### Step 2 — Walk through Phase 0 templates

Open and fill, in order:

1. `phase-0/00-project-overview.md` — expanded project overview
2. `phase-0/01-stack-and-tools.md` — stack details, tools, environment
3. `phase-0/02-domain-overview.md` — gateway to `design/`; what is the domain?
4. `phase-0/03-roadmap-draft.md` — phases envisioned (high-level)

For each: ask user, fill in, save. Keep it light — these are skeletons, not exhaustive docs.

### Step 3 — Generate first phase

Once Phase 0 is complete:

1. Read `protocols/phase-generation.md`.
2. Use the user's roadmap from `03-roadmap-draft.md` to write `phases/phase-1.md`.
3. Identify parallel groups within Phase 1 (per `protocols/parallelism.md`).
4. Update `STATE.md`: `p:1 status:planned`.
5. Update `NEXT.md` to point to phase-1 first block.
6. Update `INDEX.md` if new files added to catalog.

### Step 4 — Offer multi-agent setup

Look at `phases/phase-1.md` parallel_execution_plan. If multiple parallel groups exist:

Tell the user:
> "Phase 1 has N parallel groups. You can spawn up to N agents to work in parallel (faster), OR run sequentially with 1 agent (simpler). Which do you want?"

If multi-agent:
- Read `templates/agent-roles/implementer.md` and `protocols/agents.md`.
- Generate `agents/agent-1a.md`, `agents/agent-1b.md`, ... one per parallel group.
- Generate a Governor session: `agents/governor.md` from `templates/agent-roles/governor.md`.
- Output a list of "boot prompts" the user can paste into each new Claude Code session.

If single-agent:
- Generate just one AGENT.md (or none — user uses default implementer behavior).

### Step 5 — Hand off to block work

Tell the user:
> "Phase 1 is planned. Block 001 manifest is ready. To start work, follow `commands/block-start.md`. If you want me to start it now, say 'start'."

Mark BOOTSTRAP as complete by updating `STATE.md`: `status:active`. BOOTSTRAP.md is not re-read in subsequent sessions.

## After BOOTSTRAP

- `PROJECT.md` is filled
- `phase-0/` files filled
- `design/` has at least placeholder `02-domain-overview.md`
- `phases/phase-1.md` exists
- `STATE.md` reflects Phase 1
- (Optional) Multi-agent files in `agents/`
- The AI returns to normal flow: read PROTOCOLS → STATE → NEXT → block manifest.

## Notes for the AI conducting BOOTSTRAP

- Confirm understanding before writing files. Echo back the user's answer in your own words.
- If the user is vague, ask follow-ups. Don't invent values.
- If the user wants to skip a section, allow it but warn what context is being lost.
- Save incremental progress. If the user pauses, they can resume at any step.
- BOOTSTRAP runs ONCE per project. Do not re-prompt in later sessions.

---

## Appendix A — Governor v2 (optional SDK tier)

> Added in v2.0 (Phase 6). Ask after Step 4 (multi-agent setup decision).

After the user decides between single-agent and multi-agent (Step 4), ask:

> "Do you want to use the Governor v2 SDK for automated block dispatch? It requires Python 3.9+ and an Anthropic API key — but it lets the Governor spawn sub-agents and update state files automatically. Or you can stay in manual mode (the default) where the AI handles everything in the current session."

### Governor mode: `manual` (default — recommended to start)

No extra steps. The AI reads manifests and executes blocks in the current session. Works in any editor or LLM. **Start here.**

Update `STATE.md` after PROJECT.md is saved:
```
governor_mode:manual
```
(If the field is already there, leave it. If absent, add it.)

### Governor mode: `sdk` (automated dispatch — optional)

Enable when the user explicitly wants autonomous multi-block execution:

1. **Install SDK dependencies:**
   ```bash
   pip install -r cognitive-arch/sdk/requirements.txt
   ```

2. **Set your Anthropic API key:**
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```
   Get at [console.anthropic.com/settings/api-keys](https://console.anthropic.com/settings/api-keys). Billed separately from Claude Max.

3. **Update STATE.md:**
   ```
   governor_mode:sdk
   ```

4. **Verify:**
   ```bash
   python cognitive-arch/sdk/governor.py --mode sdk --dry-run
   ```

### What to tell the user

```
Governor modes:
  manual (default) — AI runs blocks in this session. Zero extra setup.
  sdk — Governor auto-dispatches sub-agents via Anthropic API. Needs Python + API key.

Recommendation: start with manual. Switch to sdk when you want autonomous execution.
```

See `RETROFIT.md Appendix A` for the full env-vars table and `design/governor-v2.md` for architecture detail.

End of BOOTSTRAP.md.
