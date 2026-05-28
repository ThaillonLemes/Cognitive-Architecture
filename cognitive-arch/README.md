# Cognitive Architecture for AI-assisted code projects

A markdown-only scaffold that brings structured AI collaboration to any code project. Drop the `cognitive-arch/` folder into your repository and the AI uses it as a shared cognitive workspace.

## What this is

This is a **scaffold**, not a runtime. It's pure markdown (plus one optional bash audit script and an optional Python SDK). The AI reads the structure to:

- Understand your project quickly (slim boot — ~3K tokens vs 10K+ for traditional setups)
- Plan work in numbered blocks with manifests, gates, and retrospectives
- Coordinate multiple AI agents in parallel via a Governor agent
- Maintain consistency over time and across sessions
- Audit itself for drift and broken pointers

## What it provides

- **Slim boot:** AI initializes with ~3K tokens
- **Block-based methodology:** each block has a manifest, gates, and retrospective
- **Governor v2:** two-tier orchestration — manual (zero setup) or SDK (Python + Anthropic API, fully automated)
- **Gates with evidence:** blocks don't close without proof (tests pass, files updated, dependencies met)
- **Stack addenda:** Python/FastAPI, React/Next.js, Node/Express convention overlays
- **Project-agnostic:** works for SaaS, games, CLIs, libraries, mobile apps
- **No installation:** copy the folder — that's it for the markdown tier

## Quick start

### New project (blank slate)

```bash
cp -r path/to/cognitive-arch ./cognitive-arch
```

Open Claude Code in your repo and say `"oi"` — the AI reads [`BOOTSTRAP.md`](BOOTSTRAP.md) and runs Phase 0 interactively (~10 minutes).

### Existing project (retrofit)

```bash
cp -r path/to/cognitive-arch ./cognitive-arch
```

Open Claude Code and say `"retrofit"` — the AI reads [`RETROFIT.md`](RETROFIT.md), analyzes your code, and fills the architecture from what's already there.

## Governor v2 (optional SDK tier)

By default, the AI runs blocks **manually** in the current session — no extra setup.

To enable **automated dispatch** (Governor spawns Claude sub-agents and integrates results automatically):

```bash
pip install -r cognitive-arch/sdk/requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
# In STATE.md: change governor_mode:manual → governor_mode:sdk
python cognitive-arch/sdk/governor.py --mode sdk --dry-run
```

See [`BOOTSTRAP.md` Appendix A](BOOTSTRAP.md) / [`RETROFIT.md` Appendix A](RETROFIT.md) for the full setup guide.

## Stack addenda

Stack-specific convention overlays under `protocols/stack-addenda/`:

| Stack | File |
|-------|------|
| Python / FastAPI | `protocols/stack-addenda/python-fastapi.md` |
| React / Next.js (App Router) | `protocols/stack-addenda/react-nextjs.md` |
| Node.js / Express | `protocols/stack-addenda/node-express.md` |

## File map (top level)

| Path | What |
|------|------|
| `CLAUDE.md` | AI entry point |
| `PROTOCOLS.md` | Universal axioms (P/Q/C) + Charter |
| `STATE.md` / `NEXT.md` / `INDEX.md` | Orientation (AI-only, dense) |
| `PROJECT.md` | Project identity (filled in Phase 0) |
| `BOOTSTRAP.md` | Interactive first-session guide (new projects) |
| `RETROFIT.md` | First-session guide for existing projects |
| `sdk/` | Governor v2 Python package (optional; Phase 5+) |
| `audit.sh` | Light structural validation script |

## Quick concepts

- **Phase:** a coherent chunk of work with exit criteria. Phase 0 = onboarding.
- **Block:** one unit of work. Has a manifest (contract), implementation, gates, retrospective.
- **Manifest:** the block contract — files touched, dependencies, gates, validation.
- **Gates:** evidence a block must produce to close (tests pass, files updated, deps met).
- **Governor:** the integrator agent — merges parallel work, runs audits, never implements.
- **`governor_mode: manual`** — AI executes blocks in the current session (default, zero setup).
- **`governor_mode: sdk`** — Governor dispatches sub-agents via Anthropic API automatically.

## How it's different

Existing AI-coding tools focus on the chat loop. This focuses on the **knowledge structure** the AI navigates:

- Stack-agnostic — works with any language or framework
- Runtime-free — no daemon, no server, no compile step
- Multi-LLM friendly — works with Claude, GPT-4, Gemini, local LLMs
- Auditable — `audit.sh` validates structure; drift is detected, not silently absorbed
- Forkable — you own every file; copy and modify freely

## License

MIT (or your preference — the scaffold is yours to keep).
