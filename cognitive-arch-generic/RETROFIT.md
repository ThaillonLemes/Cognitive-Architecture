# RETROFIT — bootstrap for existing projects
# v2 — updated Phase 22. Original archived as RETROFIT-v1.md.

BRIEF: Adopt cognitive-arch in a project that ALREADY has code. Analyzes existing code; fills cognitive-arch files from what's found. No project code is modified.

## Detection

Use RETROFIT when ANY of: existing `src/`, `app/`, `lib/`; README with real content; git history with development commits; existing tests, build scripts, CI.

Use BOOTSTRAP only for brand-new empty projects.

---

## Step 0 — Session init (MANDATORY)

Run before anything else:
```bash
python sdk/session_start.py --arch-root .
```

Note health score, patterns, proposals, governor notifications.

---

## Step 1 — Read cognitive architecture

Read in order:
1. `CLAUDE.md`
2. `PROTOCOLS.md`
3. `PROJECT.md` (template)
4. `INDEX.md`

Confirm understanding to user before proceeding.

---

## Step 2 — Inspect project (read-only)

**DO NOT modify anything outside `cognitive-arch/`.**

Scan:
1. Root layout (exclude `cognitive-arch/`)
2. Stack manifest files: `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.
3. Build/test/lint commands from `Makefile`, scripts, README, CI files
4. Existing docs: `README.md`, `docs/`, `ARCHITECTURE.md`, `CHANGELOG.md`, ADRs
5. Code structure: `src/`, `lib/`, `app/`, `components/`, etc.
6. Tests: location, naming, approximate count
7. CI/CD: `.github/workflows/`, `.gitlab-ci.yml`, etc.
8. Git activity: `git log --oneline -20`, `git branch -a`

Report to user:

```
Detected project context:
- Language: <X>
- Framework: <Y>
- Build cmd: <cmd>
- Test cmd: <cmd>
- Lint cmd: <cmd>
- Code in: <folders>
- Tests in: <folders>
- Docs in: <folders>
- CI: <system or none>
- Recent git: <pattern>
- File count: ~N
```

---

## Step 3 — Ask clarifying questions

Code cannot answer the WHY. Ask the user (one at a time):

1. Vision: what does this deliver? (1-2 sentences)
2. Target users: who uses it?
3. Type: web app / SaaS / game / CLI / library / mobile / desktop / other?
4. Status: early dev / MVP / beta / production / maintenance?
5. Key constraints: performance, security, compliance, latency?
6. Next phase: immediate work direction for next 2-4 weeks?
7. Ambiguities: anything in code needing interpretation?

---

## Step 4 — Fill PROJECT.md

With Step 2 (inferred) + Step 3 (user confirmed):
- Open `PROJECT.md`, fill frontmatter + body
- Mark inferred content: `(inferred — confirm)` or `(user confirmed)`
- Save. Then:
  ```bash
  python sdk/state_manager.py --set-state "status:active phase:0 retrofitted_from:$(date +%Y-%m-%d)"
  ```

---

## Step 5 — Fill phase-0/ templates

Fill each (ask → write):
- `phase-0/00-project-overview.md` — vision, scope, risks
- `phase-0/01-stack-and-tools.md` — exact stack, commands, env vars
- `phase-0/02-domain-overview.md` — entities, flows, business rules (from code)
- `phase-0/03-roadmap-draft.md` — proposed phases based on git history + user answer

Mark inferred content liberally with `(inferred — confirm)`.

---

## Step 6 — Populate design/ (if code is clear)

Extract if domain logic is readable:
- `design/entities.md` — main entities, data shapes
- `design/api-contracts.md` — API surface (if service)
- `design/<domain-specific>.md` — other project-specific docs

**DO NOT INVENT.** Mark `TBD — confirm with user` if code doesn't say. Incomplete > wrong.

---

## Step 7 — Generate Phase 1

Based on: user's next-phase answer + recent git activity + inferred focus.

Create `phases/phase-1.md` using `templates/phase.md` + `protocols/phase-generation.md`.

Phase 1 = first phase DEFINED under cognitive-arch (not the project's first phase).

---

## Step 8 — Update HOT files

```bash
python sdk/state_manager.py --set-state "phase:1 status:active"
python sdk/state_manager.py --set-next "next_action:block-001 phase:phase-1"
```

Update `INDEX.md` if new `design/` docs added.

---

## Step 9 — Governor mode + notifications

Ask user: Manual or SDK governor mode? (See BOOTSTRAP.md §Step 4 for details.)

Check governor notifications:
```bash
python sdk/notification_manager.py list --pending
```

Surface any critical/high notifications before starting block work.

---

## Step 10 — Final report

```
=== RETROFIT COMPLETE ===

Discovered: <summary>

Filled:
- PROJECT.md (N inferred markers)
- phase-0/* (4 files, M TBDs)
- design/* (K files, L TBDs)
- phases/phase-1.md (N planned blocks)

Open TBDs:
1. <list>

Next: review TBDs, then start block-001 via commands/block-start.md
```

---

## Rules

- NEVER modify files outside `cognitive-arch/`
- NEVER invent domain logic not in code
- NEVER presume intent — ask when ambiguous
- Mark `(inferred — confirm)` and `TBD` liberally
- All state updates via SDK tools (`state_manager.py`, not manual edits)
- RETROFIT runs ONCE per project

---

## SDK tool reference

| Operation | Command |
|-----------|---------|
| Session init | `python sdk/session_start.py --arch-root .` |
| Update state | `python sdk/state_manager.py --set-state "key:val"` |
| Update next | `python sdk/state_manager.py --set-next "key:val"` |
| Close block | `python sdk/block_close.py --block-id X --next Y --actual-hours N` |
| Check notifications | `python sdk/notification_manager.py list --pending` |
| Generate dashboard | `python sdk/dashboard_generator.py --arch-root .` |
| Add notification | `python sdk/notification_manager.py add "msg" --type custom --priority high` |

---

## Difference from BOOTSTRAP.md

| Aspect | BOOTSTRAP | RETROFIT |
|--------|-----------|----------|
| Project state | Empty / new | Existing code |
| Source of truth | User answers | Code inspection + user answers |
| Output speed | Fast (template-driven) | Slower (analysis + iteration) |
| TBD markers | None expected | Many expected |
| Risk | Low | Higher (must not modify existing) |
| Domain population | User describes | Extracted from code, marked inferred |
