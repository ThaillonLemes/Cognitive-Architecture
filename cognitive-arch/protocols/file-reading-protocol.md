# Protocol: File reading

BRIEF: How the AI reads files efficiently. Use partial-read for large files; full-read for HOT files. Briefs at top let you decide what to load.

## Read tool behavior

The `Read` tool, by default, reads the ENTIRE file (up to 2000 lines). You can specify partial reads:

- `Read(file, limit:N)` — read first N lines only
- `Read(file, offset:M, limit:N)` — read N lines starting at line M+1
- `Read(file)` — read everything (default)

## When to use partial-read

### Always partial-read these (scan first):

- Large markdown docs (> 500 lines) — read brief first
- Code files (> 200 lines) when scanning for relevance — read header (5 lines) per `protocols/code-header-protocol.md`
- Archives (`manifests/_archive/*.md`) — read frontmatter only unless investigating

### Always full-read these (small, must-have):

- CLAUDE.md
- STATE.md
- NEXT.md
- INDEX.md (use as catalog)
- _syntax.md
- board.md
- AGENT.md for your role
- The active block manifest you're working on
- All files in `commands/` when you're following one

### Decide per case:

- Files 50-500 lines: read full unless you only want the brief
- `phases/phase-<N>.md` for non-active phase: read brief (limit:30) to learn what it covered
- `blocks/block-<NNN>-*.md` retrospectives: read frontmatter only unless investigating

## The brief-scan pattern

For large files, use this pattern:

1. `Read(file, limit:30)` — get the brief and YAML frontmatter
2. Decide: do you need more?
   - Yes → `Read(file)` for full content
   - No → move on, you have enough

This saves tokens when scanning many files.

## Example: scanning manifests

You want to find all manifests that touch file `src/auth.ts`:

**Inefficient:** read all manifests in full, scan each.
**Efficient:** use `Grep('src/auth.ts', 'manifests/')` to find matches, then `Read` only the matching files.

For Claude Code, prefer `Grep` for content search and `Glob` for path matching BEFORE reading.

## Token cost awareness

| Pattern | Cost (rough) | When to use |
|---------|--------------|-------------|
| Full read 50-line file | 500 tokens | Small files, must-have HOT files |
| Full read 500-line file | 5,000 tokens | Active block work; need details |
| Partial read 30 lines | 300 tokens | Scanning; just want brief |
| Grep then read 1-2 files | 1,000 + 5,000 = 6,000 | Searching across many files |
| Read all manifests in archive | 50,000+ | Almost always wrong — use Grep first |

## Boot-time reading order

At session start:
1. `Read(CLAUDE.md)` — ~50 lines
2. `Read(STATE.md)` — ~5 lines (AI-only, dense)
3. `Read(NEXT.md)` — ~3 lines
4. `Read(_syntax.md, limit:30)` — only on first session of project; cached after
5. If multi-agent: `Read(AGENT.md for your role)` — ~30 lines
6. If working a block: `Read(active manifest)` — ~50-200 lines
7. Need more? `Read(INDEX.md)` — ~100 lines; decide what else from briefs

Total boot: ~300-500 lines = ~3K-5K tokens. This is the slim boot target.

## When to RE-read

- File explicitly changed (you wrote to it; need to verify it actually changed — but the Write tool usually doesn't lie)
- It's been a long session and you're not sure of current state
- User says "re-read X" or "what's in X right now?"

Avoid re-reading files you wrote in the same session — wasteful.

## Code file reading

For code files, the header (per `protocols/code-header-protocol.md`) gives you orientation in 5 lines. After header:

- If you need the full file: `Read(file)`
- If you just need a specific function: `Grep` for function name, then read around the match
- If you need a quick summary: `Read(file, limit:50)` usually has imports + top declarations

## Partial-read pitfalls

- Limit must be high enough to capture useful content. Header is 5 lines; brief is 3-30 lines. limit:30 is a safe baseline.
- If the file is dense AI-only key:value, 5 lines might be 50 facts. Adjust by file type.

## Token efficiency checklist

When reading files, ask yourself:
- [ ] Do I need this file at all? (Check INDEX.md brief first)
- [ ] Do I need it FULL or partial?
- [ ] Have I already read it this session?
- [ ] Could `Grep` get me what I need faster?

If you can answer the question without reading more, don't read more.

End of file-reading-protocol.
