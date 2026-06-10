# sdk/code_review.py
# PURPOSE: Semantic diff analysis (Bugbot-equivalent). Reads git diff of a block,
#          applies configurable rules from governance/review-rules.md, returns
#          structured findings. Blocks block-close on security/bug findings (normal mode)
#          or any finding (corporate mode). Non-blocking findings logged to governance/bugs.md.
# INPUTS:  block_id, arch_root, diff_text (str), mode (normal|corporate), force (bool)
# OUTPUTS: ReviewResult; appends to governance/bugs.md on critical findings
# DEPS:    stdlib only
# USAGE:   python sdk/code_review.py --block-id block-XXX --arch-root . [--diff file.diff]
# SEE:     governance/review-rules.md, governance/bugs.md

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

SEVERITY_RANK = {"security": 3, "bug": 2, "quality": 1}

BLOCKING_SEVERITIES_NORMAL = {"security", "bug"}
BLOCKING_SEVERITIES_CORPORATE = {"security", "bug", "quality"}


@dataclass
class Finding:
    id: str
    file: str
    line: int
    severity: str     # security | bug | quality
    category: str
    message: str
    suggestion: str


@dataclass
class ReviewResult:
    block_id: str
    findings: list[Finding] = field(default_factory=list)
    blocked: bool = False
    block_reason: str = ""
    mode: str = "normal"

    @property
    def blocking_findings(self) -> list[Finding]:
        sev = BLOCKING_SEVERITIES_CORPORATE if self.mode == "corporate" else BLOCKING_SEVERITIES_NORMAL
        return [f for f in self.findings if f.severity in sev]

    @property
    def log_only_findings(self) -> list[Finding]:
        return [f for f in self.findings if f not in self.blocking_findings]


# ---------------------------------------------------------------------------
# Rule loading from governance/review-rules.md
# ---------------------------------------------------------------------------

@dataclass
class Rule:
    id: str
    severity: str
    category: str
    pattern: str
    message: str
    suggestion: str
    languages: list[str]
    enabled: bool = True
    _compiled: object = field(default=None, compare=False, repr=False)

    def matches(self, line: str) -> bool:
        if not self.enabled:
            return False
        if self._compiled is None:
            try:
                object.__setattr__(self, "_compiled", re.compile(self.pattern, re.IGNORECASE))
            except re.error:
                return False
        return bool(self._compiled.search(line))


def _parse_rules(text: str) -> list[Rule]:
    """Parse review-rules.md table rows into Rule objects."""
    rules: list[Rule] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("| id") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 7:
            continue
        rid, severity, category, pattern, message, suggestion, langs_raw = cells[:7]
        enabled_raw = cells[7].strip() if len(cells) > 7 else "yes"
        langs = [l.strip() for l in langs_raw.split(",") if l.strip()] if langs_raw.strip() else []
        enabled = enabled_raw.lower() not in ("no", "false", "0", "disabled")
        rules.append(Rule(
            id=rid.strip(),
            severity=severity.strip(),
            category=category.strip(),
            pattern=pattern.strip(),
            message=message.strip(),
            suggestion=suggestion.strip(),
            languages=langs,
            enabled=enabled,
        ))
    return rules


_DEFAULT_RULES_MD = """\
| id | severity | category | pattern | message | suggestion | languages | enabled |
|----|----------|----------|---------|---------|------------|-----------|---------|
| R01 | security | injection | \\beval\\s*\\( | eval() detected — arbitrary code execution risk | Replace with safe alternatives (avoid eval entirely) | js,ts,py | yes |
| R02 | security | secrets | password\\s*=\\s*['\"][^'\"]{4,} | Hardcoded password detected | Use environment variables or secrets manager | py,js,ts | yes |
| R02b | security | secrets | api_key\\s*=\\s*['\"][^'\"]{4,} | Hardcoded API key detected | Use environment variables or secrets manager | py,js,ts | yes |
| R02c | security | secrets | secret\\s*=\\s*['\"][^'\"]{4,} | Hardcoded secret detected | Use environment variables or secrets manager | py,js,ts | yes |
| R02d | security | secrets | token\\s*=\\s*['\"][^'\"]{4,} | Hardcoded token detected | Use environment variables or secrets manager | py,js,ts | yes |
| R03 | security | sql | ['\"].*SELECT.*\\+\\s*\\w | String-concatenated SQL SELECT — SQL injection risk | Use parameterized queries or ORM | py,js,ts | yes |
| R03b | security | sql | ['\"].*INSERT.*\\+\\s*\\w | String-concatenated SQL INSERT — SQL injection risk | Use parameterized queries or ORM | py,js,ts | yes |
| R04 | security | xss | innerHTML\\s*= | innerHTML assignment — potential XSS | Use textContent or a sanitization library | js,ts | yes |
| R05 | bug | null-check | undefined.*\\.\\w+(?!\\?) | Potential null dereference on undefined | Add null check or use optional chaining (?.) | js,ts | yes |
| R06 | bug | exception | except\\s*: | Bare except clause — swallows all exceptions | Catch specific exceptions (except ValueError: etc.) | py | yes |
| R08 | quality | console | console\\.log\\( | console.log left in production code | Remove or replace with proper logger | js,ts | yes |
| R09 | quality | todo | \\bTODO\\b | TODO comment left unresolved | Resolve or file a tracked issue | all | yes |
| R09b | quality | todo | \\bFIXME\\b | FIXME comment left unresolved | Resolve or file a tracked issue | all | yes |
"""


def load_rules(arch_root: Path) -> list[Rule]:
    rules_path = arch_root / "governance" / "review-rules.md"
    text = rules_path.read_text(encoding="utf-8", errors="replace") if rules_path.exists() else _DEFAULT_RULES_MD
    rules = _parse_rules(text)
    return rules if rules else _parse_rules(_DEFAULT_RULES_MD)


# ---------------------------------------------------------------------------
# Diff analysis
# ---------------------------------------------------------------------------

def _file_ext(filename: str) -> str:
    return Path(filename).suffix.lstrip(".").lower()


def _lang_for_ext(ext: str) -> str:
    return {"py": "py", "js": "js", "ts": "ts", "tsx": "ts", "jsx": "js"}.get(ext, ext)


def analyze_diff(diff_text: str, rules: list[Rule], block_id: str) -> list[Finding]:
    """Scan added lines in diff against rules. Returns list of Finding."""
    findings: list[Finding] = []
    current_file = ""
    current_line = 0
    finding_counter = 0
    seen: set[tuple[str, int, str]] = set()

    for raw_line in diff_text.splitlines():
        # Track current file
        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:].strip()
            current_line = 0
            continue
        if raw_line.startswith("+++ "):
            current_file = raw_line[4:].strip()
            current_line = 0
            continue
        if raw_line.startswith("@@ "):
            m = re.search(r"\+(\d+)", raw_line)
            current_line = int(m.group(1)) if m else 0
            continue

        # Only check added lines
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            content = raw_line[1:]
            current_line += 1
            ext = _file_ext(current_file)
            lang = _lang_for_ext(ext)

            for rule in rules:
                if not rule.enabled:
                    continue
                if rule.languages and "all" not in rule.languages and lang not in rule.languages:
                    continue
                if not rule.matches(content):
                    continue
                dedup_key = (current_file, current_line, rule.id)
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)
                finding_counter += 1
                findings.append(Finding(
                    id=f"{block_id}-R{finding_counter:03d}",
                    file=current_file,
                    line=current_line,
                    severity=rule.severity,
                    category=rule.category,
                    message=f"[{rule.id}] {rule.message}",
                    suggestion=rule.suggestion,
                ))
        elif not raw_line.startswith("-"):
            current_line += 1

    # Sort by severity rank desc, then file, then line
    findings.sort(key=lambda f: (-SEVERITY_RANK.get(f.severity, 0), f.file, f.line))
    return findings


# ---------------------------------------------------------------------------
# bugs.md persistence
# ---------------------------------------------------------------------------

_BUGS_HEADER = """\
# governance/bugs.md
# Persistent bug log — written by sdk/code_review.py at block-close.
# Status lifecycle: open → resolved | deferred
# Do not edit the header row.

| id | block | severity | file | line | description | status | date |
|----|-------|----------|------|------|-------------|--------|------|
"""


def _ensure_bugs_md(arch_root: Path) -> Path:
    path = arch_root / "governance" / "bugs.md"
    if not path.exists():
        path.parent.mkdir(exist_ok=True)
        path.write_text(_BUGS_HEADER, encoding="utf-8")
    return path


def append_bugs(arch_root: Path, findings: list[Finding], block_id: str) -> None:
    """Append findings to governance/bugs.md (deduplicates by id)."""
    if not findings:
        return
    bugs_path = _ensure_bugs_md(arch_root)
    existing = bugs_path.read_text(encoding="utf-8", errors="replace")
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_rows: list[str] = []
    for f in findings:
        if f.id in existing:
            continue
        short_desc = f.message.replace("|", "/")[:80]
        new_rows.append(
            f"| {f.id} | {block_id} | {f.severity} | {f.file} | {f.line} | {short_desc} | open | {date_str} |"
        )
    if new_rows:
        with open(bugs_path, "a", encoding="utf-8") as fh:
            for row in new_rows:
                fh.write(row + "\n")
        print(f"  bugs.md: {len(new_rows)} finding(s) logged")


# ---------------------------------------------------------------------------
# Main review function
# ---------------------------------------------------------------------------

def _get_git_diff(arch_root: Path, block_id: str) -> str:
    """Try to get git diff for the block. Returns empty string on failure."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD", "--unified=3"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(arch_root), timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
        # Fallback: staged diff
        result2 = subprocess.run(
            ["git", "diff", "--cached", "--unified=3"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(arch_root), timeout=15,
        )
        return result2.stdout if result2.returncode == 0 else ""
    except Exception:
        return ""


def _read_mode(arch_root: Path, block_id: str) -> str:
    """Detect mode from manifest or STATE.md."""
    manifests_dir = arch_root / "manifests"
    candidates = list(manifests_dir.glob(f"{block_id}-*.md"))
    if candidates:
        text = candidates[0].read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^mode:\s*(\S+)", text, re.MULTILINE)
        if m:
            return m.group(1)
    state = arch_root / "STATE.md"
    if state.exists():
        text = state.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^mode:\s*(\S+)", text, re.MULTILINE)
        if m:
            return m.group(1)
    return "normal"


def review_block(
    block_id: str,
    arch_root: Path,
    diff_text: str = "",
    mode: str = "",
    force: bool = False,
) -> ReviewResult:
    """Run code review for a block. Core entry point."""
    if not mode:
        mode = _read_mode(arch_root, block_id)

    if not diff_text:
        diff_text = _get_git_diff(arch_root, block_id)

    result = ReviewResult(block_id=block_id, mode=mode)

    if not diff_text.strip():
        print(f"  [code_review] No diff available for {block_id} — skipping review")
        return result

    rules = load_rules(arch_root)
    result.findings = analyze_diff(diff_text, rules, block_id)

    blocking = result.blocking_findings
    log_only = result.log_only_findings

    if blocking and not force:
        sev_list = ", ".join(sorted({f.severity for f in blocking}))
        result.blocked = True
        result.block_reason = (
            f"Code review: {len(blocking)} blocking finding(s) [{sev_list}]. "
            "Fix before closing or use --force to override."
        )

    # Always log findings to bugs.md
    append_bugs(arch_root, result.findings, block_id)

    _print_summary(result, mode)
    return result


def _print_summary(result: ReviewResult, mode: str) -> None:
    n = len(result.findings)
    if n == 0:
        print(f"  [code_review] {result.block_id}: no findings ✓")
        return
    print(f"\n  [code_review] {result.block_id}: {n} finding(s) — mode={mode}")
    for f in result.findings:
        marker = "⛔" if f.severity == "security" else ("\U0001f41e" if f.severity == "bug" else "\U0001f4dd")
        print(f"    {marker} [{f.severity.upper()}] {f.file}:{f.line} — {f.message}")
        if f.suggestion:
            print(f"       → {f.suggestion}")
    if result.blocked:
        print(f"\n  HALT: {result.block_reason}")


# ---------------------------------------------------------------------------
# HTML report section (for review_pipeline integration)
# ---------------------------------------------------------------------------

def build_html_section(result: ReviewResult) -> str:
    if not result.findings:
        return "<h2>\U0001f916 Code Review (Bugbot)</h2><div class='card'><p class='ok'>Nenhuma issue detectada ✓</p></div>"

    rows = ""
    for f in result.findings:
        sev_class = "err" if f.severity == "security" else ("warn" if f.severity == "bug" else "")
        rows += (
            f"<tr>"
            f"<td class='{sev_class}'>{f.severity}</td>"
            f"<td>{f.category}</td>"
            f"<td><code>{f.file}:{f.line}</code></td>"
            f"<td>{f.message}</td>"
            f"<td style='color:var(--muted)'>{f.suggestion}</td>"
            f"</tr>"
        )
    blocked_badge = (
        "<span class='badge err'>BLOQUEADO</span>" if result.blocked
        else "<span class='badge ok'>PASS</span>"
    )
    return (
        "<h2>\U0001f916 Code Review (Bugbot)</h2>"
        "<div class='card'>"
        f"<p>{blocked_badge} &nbsp; {len(result.findings)} finding(s)</p>"
        "<table>"
        "<tr><th>Severity</th><th>Category</th><th>Location</th><th>Message</th><th>Suggestion</th></tr>"
        f"{rows}"
        "</table>"
        "</div>"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Code review gate (Bugbot-equivalent)")
    parser.add_argument("--block-id", required=True)
    parser.add_argument("--arch-root", default=".")
    parser.add_argument("--diff", default="", help="Path to diff file (or stdin)")
    parser.add_argument("--mode", default="", help="normal|corporate (auto-detected if omitted)")
    parser.add_argument("--force", action="store_true", help="Log findings but don't block")
    args = parser.parse_args(argv)

    arch_root = Path(args.arch_root).resolve()
    diff_text = ""
    if args.diff:
        p = Path(args.diff)
        diff_text = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

    result = review_block(args.block_id, arch_root, diff_text, args.mode, args.force)
    return 1 if result.blocked else 0


if __name__ == "__main__":
    sys.exit(main())
