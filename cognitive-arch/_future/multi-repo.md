# _future: Multi-repo evolution

BRIEF: How to evolve from single-repo cognitive architecture to multi-repo workspace. Deferred to when project actually needs it.

## Why this is in _future

v1 assumes single-repo. Most projects start single-repo and stay there. Multi-repo introduces complexity:
- Workspace root vs per-repo state
- Cross-repo dependencies
- Coordinated integrations
- Multiple AGENT.md per repo

Don't pay this cost until you need it.

## When to evolve

Evolve to multi-repo when:
- Project naturally splits into independently-deployable components (e.g., frontend + backend + shared lib)
- Different teams own different repos
- You want different release cadences per component
- A single repo exceeds 100K LOC with weak internal boundaries

## Architecture (designed)

```
workspace-root/
├── cognitive-arch/                ← workspace-level cognitive arch
│   ├── STATE.md                    ← cross-repo state
│   ├── NEXT.md                     ← cross-repo pointer
│   ├── PROJECT.md                  ← whole-project identity
│   ├── design/                     ← cross-cutting domain
│   ├── phases/                     ← cross-cutting phases
│   ├── manifests/                  ← cross-repo blocks (rare)
│   └── ... (rest of architecture)
│
├── repo-1/                        ← e.g., backend
│   ├── cognitive-arch/             ← per-repo arch
│   │   ├── STATE.md                ← repo-local state
│   │   ├── NEXT.md
│   │   ├── manifests/              ← repo-local block manifests
│   │   ├── design/                 ← repo-specific design
│   │   └── ... (subset)
│   └── src/
│
├── repo-2/                        ← e.g., frontend
│   └── cognitive-arch/
│
└── repo-3/                        ← e.g., shared lib
    └── cognitive-arch/
```

## Workspace cognitive-arch vs per-repo

Workspace level has:
- Cross-repo STATE, NEXT, INDEX
- Cross-cutting design docs
- Cross-repo phase plans
- Multi-repo manifests (Tier L cross-repo)
- Single Governor for the workspace

Per-repo cognitive-arch has:
- Repo-local STATE, NEXT
- Repo-specific design (subset of workspace design + repo-only)
- Repo-local block manifests (most blocks)
- Implementer agents work in their repo

## Governance changes

In multi-repo:
- Governor coordinates across repos (operates at workspace level)
- Each repo may have its own implementer agents
- Integration involves multiple `git merge` operations across repos
- Audit runs across all repos

## Cross-repo manifests

A block that touches multiple repos uses Tier L (large) manifest with `cross_repo_impact`:

```yaml
cross_repo_impact:
  affected_repos: [repo-1, repo-2]
  protocol_bump: false
  migration_order: ["repo-1 first (provides interface)", "repo-2 follows (consumes)"]
```

Such blocks are RARE — most work stays in one repo. When cross-repo work is needed, the Tier L review by Governor is critical.

## Branch / worktree model

Per-repo branches:
- `repo-1/main`, `repo-1/claude/feature-x`
- `repo-2/main`, `repo-2/claude/feature-x`

Worktree-per-agent applies per-repo.

## How to evolve from single-repo to multi-repo

1. Identify split candidates (which subfolders are cohesive units?)
2. Create new repos (`git subtree split` or fresh history)
3. Create workspace folder containing the new repos as siblings
4. Set up `workspace/cognitive-arch/` with cross-repo state
5. Adapt per-repo `cognitive-arch/` (subset of files; reference workspace where applicable)
6. Update all PROJECT.md files (whole-project at workspace level; repo identity per repo)
7. Migrate active blocks: each goes to the repo that owns it
8. Update Governor: now multi-repo aware

This is a major migration. Plan a dedicated phase for it.

## Risks of multi-repo

- Coordination overhead (every cross-repo change is heavier)
- Versioning complexity (each repo has its own version)
- Easier to drift (different repos may stale separately)
- CI/CD complexity

Only evolve when the benefits clearly exceed these costs.

End of multi-repo design.
