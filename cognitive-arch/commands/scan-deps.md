# Command: scan-deps

Mode required: guardrails

BRIEF: One-off dependency scan. Check for outdated, vulnerable, or unused dependencies.

## Usage

- Manual: "run scan-deps"
- Auto-triggered: monthly or at phase-close

## What to scan

Depends on stack (PROJECT.md). Common cases:

### TypeScript / Node.js
- `npm outdated`
- `npm audit` (security)
- Check `package.json` for unused dependencies

### Python
- `pip list --outdated`
- `pip-audit` (security)
- `pipreqs` for unused imports

### Rust
- `cargo outdated`
- `cargo audit` (security)
- `cargo udeps` for unused dependencies

### Go
- `go list -u -m all` (outdated)
- `nancy sleuth` or `govulncheck` (security)

### Generic / other
- Read PROJECT.md for stack
- Run stack-appropriate tool
- If none configured: warn user

## Output

Generate `governance/scan-deps-<YYYY-MM-DD>.md`:

```markdown
# Dependency scan — <YYYY-MM-DD>

## Summary
- Outdated: <count>
- Vulnerable: <count>
- Unused: <count>

## Outdated dependencies

| Package | Current | Latest | Major? | Recommended action |
|---------|---------|--------|--------|--------------------|
| <pkg> | <v> | <v> | yes/no | upgrade / wait / skip |

## Security vulnerabilities

| Package | Severity | Description | Fix |
|---------|----------|-------------|-----|
| <pkg> | critical/high/medium/low | <CVE or summary> | upgrade to <v> |

## Unused dependencies

- <pkg> — appears in <manifest> but no imports found

## Recommendations

- Block proposed: upgrade <critical-vulnerable-pkg> immediately
- Block proposed: review and remove unused deps
- Backlog: schedule major version upgrades for phase <X>
```

## Triggering blocks from findings

For critical vulnerabilities: auto-propose a block manifest with high priority.

For major version upgrades: propose blocks with caveats (test thoroughly).

For unused deps: low-priority cleanup block.

User approves each before block goes to `manifests/`.

## Cost

Per scan: ~2K-5K tokens.

End of scan-deps command.
