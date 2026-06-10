# governance/review-rules.md
# Configurable rules for sdk/code_review.py (Bugbot-equivalent).
# Edit this file to add, disable, or tune rules.
#
# IMPORTANT: Do NOT use regex alternation (|) inside pattern cells — the | character
# is also the markdown table separator. Instead, create one rule per alternative (R02, R02b, R02c).
#
# Column format:
#   id       — unique rule ID (R01, R02, ...)
#   severity — security | bug | quality
#   category — slug label (injection, secrets, sql, xss, null-check, exception, console, todo, complexity)
#   pattern  — Python-compatible regex (applied to each ADDED line in the diff)
#   message  — human-readable finding description
#   suggestion — remediation hint
#   languages — comma-separated: py, js, ts  |  use "all" for language-agnostic
#   enabled  — yes | no

| id | severity | category | pattern | message | suggestion | languages | enabled |
|----|----------|----------|---------|---------|------------|-----------|---------|
| R01 | security | injection | \beval\s*\( | eval() detected — arbitrary code execution risk | Replace with safe alternatives (avoid eval entirely) | js,ts,py | yes |
| R02 | security | secrets | password\s*=\s*['"][^'"]{4,} | Hardcoded password detected | Use environment variables or secrets manager | py,js,ts | yes |
| R02b | security | secrets | api_key\s*=\s*['"][^'"]{4,} | Hardcoded API key detected | Use environment variables or secrets manager | py,js,ts | yes |
| R02c | security | secrets | secret\s*=\s*['"][^'"]{4,} | Hardcoded secret detected | Use environment variables or secrets manager | py,js,ts | yes |
| R02d | security | secrets | token\s*=\s*['"][^'"]{4,} | Hardcoded token detected | Use environment variables or secrets manager | py,js,ts | yes |
| R03 | security | sql | ['"].*SELECT.*\+\s*\w | String-concatenated SQL SELECT — SQL injection risk | Use parameterized queries or ORM | py,js,ts | yes |
| R03b | security | sql | ['"].*INSERT.*\+\s*\w | String-concatenated SQL INSERT — SQL injection risk | Use parameterized queries or ORM | py,js,ts | yes |
| R04 | security | xss | innerHTML\s*= | innerHTML assignment — potential XSS | Use textContent or a sanitization library | js,ts | yes |
| R05 | bug | null-check | undefined.*\.\w+(?!\?) | Potential null dereference on undefined | Add null check or use optional chaining (?.) | js,ts | yes |
| R06 | bug | exception | except\s*: | Bare except clause — swallows all exceptions | Catch specific exceptions (except ValueError: etc.) | py | yes |
| R08 | quality | console | console\.log\( | console.log left in production code | Remove or replace with proper logger | js,ts | yes |
| R09 | quality | todo | \bTODO\b | TODO comment left unresolved | Resolve or file a tracked issue | all | yes |
| R09b | quality | todo | \bFIXME\b | FIXME comment left unresolved | Resolve or file a tracked issue | all | yes |

# ─── How to add a rule ───────────────────────────────────────────────────────
# 1. Pick the next ID (R10, R11, ...).
# 2. Choose severity: security (blocks normal+corporate), bug (blocks both),
#    quality (blocks corporate only; logged to bugs.md in normal mode).
# 3. Write a Python-compatible regex WITHOUT alternation (|) — use separate rules instead.
#    Test: python -c "import re; print(re.search(r'<pattern>', '<line>'))"
# 4. Set enabled: yes. Save. Run sdk/code_review.py --block-id block-XXX --arch-root .
#
# ─── Severity semantics ──────────────────────────────────────────────────────
# security  → BLOCKS in normal AND corporate mode
# bug       → BLOCKS in normal AND corporate mode
# quality   → BLOCKS only in corporate mode; NOTIFY + log to bugs.md in normal mode
