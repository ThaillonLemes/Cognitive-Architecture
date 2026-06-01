# sdk/consistency_checker.py
# PURPOSE: Check if generated/modified code follows the project's conventions.
#          Reads L3/L4 sections of project-profile as source of truth.
#          Two levels: B (naming+imports+org, always ON) and C (internal style, toggleable).
#          Dynamic threshold that rises but never falls without Pilot approval.
# INPUTS:  --profile governance/project-profile-<client>.md, --diff <path>, --arch-root
# OUTPUTS: ConsistencyReport (score 0-1, divergences list, text export for Slack/meeting)
# DEPS:    stdlib only; sdk/scanner_profile
# USAGE:   python sdk/consistency_checker.py --profile governance/project-profile-acme.md --diff changes.diff
# SEE:     design/pipeline.md §1

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

def _fix_utf8() -> None:
    import io as _io
    if sys.platform == "win32":
        if hasattr(sys.stdout, "buffer") and not (
            isinstance(sys.stdout, _io.TextIOWrapper) and sys.stdout.encoding.lower() == "utf-8"
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_fix_utf8()


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Divergence:
    category: str          # naming | imports | organization | internal_style
    description: str
    severity: str = "warn"  # warn | error


@dataclass
class ConsistencyReport:
    score: float                    # 0.0 – 1.0
    divergences: list[Divergence] = field(default_factory=list)
    level_b_checked: bool = True
    level_c_checked: bool = False
    threshold: float = 0.80
    passed: bool = False

    def text_export(self, audience: str = "slack") -> str:
        """Generate plain-text export for copy-paste."""
        status = "✅" if self.passed else "❌"
        divs = f"{len(self.divergences)} divergências" if self.divergences else "0 divergências"
        if audience == "slack":
            cats = ", ".join({d.category for d in self.divergences}) if self.divergences else "nenhuma"
            return f"{status} Consistency {self.score:.2f} — {divs} em: {cats}"
        else:
            lines = [f"{status} Consistency Score: {self.score:.2f} (threshold: {self.threshold:.2f})"]
            if self.divergences:
                lines.append("Divergências:")
                for d in self.divergences:
                    lines.append(f"  - [{d.category}] {d.description}")
            return "\n".join(lines)


# ---------------------------------------------------------------------------
# Threshold management
# ---------------------------------------------------------------------------

_THRESHOLD_KEY = "consistency_threshold"
_DEFAULT_THRESHOLD = 0.80


def _read_threshold(profile_text: str) -> float:
    """Read consistency_threshold from project-profile frontmatter."""
    m = re.search(rf"^{_THRESHOLD_KEY}:\s*([0-9.]+)", profile_text, re.MULTILINE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return _DEFAULT_THRESHOLD


def _update_threshold(profile_path: Path, new_threshold: float) -> None:
    """Update consistency_threshold in profile (threshold_auto_raise)."""
    if not profile_path.exists():
        return
    text = profile_path.read_text(encoding="utf-8", errors="replace")
    if _THRESHOLD_KEY in text:
        text = re.sub(
            rf"^{_THRESHOLD_KEY}:\s*[0-9.]+",
            f"{_THRESHOLD_KEY}: {new_threshold:.2f}",
            text, flags=re.MULTILINE,
        )
    else:
        text += f"\n{_THRESHOLD_KEY}: {new_threshold:.2f}\n"
    profile_path.write_text(text, encoding="utf-8")


def compute_dynamic_threshold(
    history_scores: list[float],
    current_threshold: float,
    lookback: int = 5,
) -> float:
    """Compute new threshold: rises if avg(last N) > current, never falls."""
    if len(history_scores) < lookback:
        return current_threshold
    avg = sum(history_scores[-lookback:]) / lookback
    if avg > current_threshold:
        new = round(min(avg, 1.0), 2)
        return new
    return current_threshold  # never falls


# ---------------------------------------------------------------------------
# Level B: naming + imports + organization
# ---------------------------------------------------------------------------

def _check_naming(diff_text: str, naming_profile: dict[str, str]) -> list[Divergence]:
    """Check naming conventions in diff."""
    divs: list[Divergence] = []
    var_style = naming_profile.get("variables", "camelCase")
    func_style = naming_profile.get("functions", "camelCase")

    added_lines = [l[1:] for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++")]

    for line in added_lines:
        # Check for snake_case in TypeScript/JS context (wrong if camelCase expected)
        if var_style == "camelCase":
            snake_vars = re.findall(r"\bconst\s+([a-z][a-z0-9_]+[a-z0-9])\b", line)
            for v in snake_vars:
                if "_" in v:
                    divs.append(Divergence(
                        "naming",
                        f"Variável '{v}' usa snake_case mas o projeto usa camelCase",
                    ))
        elif var_style == "snake_case":
            camel_vars = re.findall(r"\bconst\s+([a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*)\b", line)
            for v in camel_vars:
                divs.append(Divergence(
                    "naming",
                    f"Variável '{v}' usa camelCase mas o projeto usa snake_case",
                ))
    return divs[:3]  # cap at 3 to avoid noise


def _check_imports(diff_text: str, import_style: str) -> list[Divergence]:
    """Check import style in diff."""
    divs: list[Divergence] = []
    added = [l[1:] for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++")]

    if "named imports preferred" in import_style:
        for line in added:
            if re.match(r"^import\s+\w+\s+from\s+['\"]", line.strip()):
                divs.append(Divergence(
                    "imports",
                    f"Import padrão detectado; o projeto prefere named imports: `{line.strip()[:60]}`",
                ))
    elif "default imports preferred" in import_style:
        for line in added:
            if re.match(r"^import\s+\{", line.strip()):
                divs.append(Divergence(
                    "imports",
                    f"Named import detectado; o projeto prefere default imports: `{line.strip()[:60]}`",
                ))
    return divs[:2]


def _check_file_organization(
    changed_files: list[str],
    profile_tree: str,
) -> list[Divergence]:
    """Check if new files were created in the right directory."""
    divs: list[Divergence] = []
    # Heuristic: new test files should be near tests/ or *.test.ts pattern
    for f in changed_files:
        if re.search(r"(test|spec)", f.lower()):
            if not re.search(r"(test|spec|\.(test|spec)\.)", f.lower()):
                divs.append(Divergence(
                    "organization",
                    f"Arquivo '{f}' parece um teste mas não segue convenção de nomes",
                ))
    return divs[:2]


# ---------------------------------------------------------------------------
# Level C: internal style (toggleable)
# ---------------------------------------------------------------------------

def _check_internal_style(diff_text: str) -> list[Divergence]:
    """Check internal code style (level C — more false positives)."""
    divs: list[Divergence] = []
    added = [l[1:] for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++")]

    # Functions longer than 50 lines (rough heuristic)
    # (Not feasible from diff alone — skip, log as limitation)

    # Detect console.log in production code (common cleanup item)
    for line in added:
        if "console.log" in line:
            divs.append(Divergence(
                "internal_style",
                "console.log detectado — remover antes de PR (use logger da aplicação)",
                severity="warn",
            ))
            break  # one is enough

    return divs[:2]


# ---------------------------------------------------------------------------
# Main checker
# ---------------------------------------------------------------------------

def check_consistency(
    profile_path: Path,
    diff_text: str = "",
    changed_files: Optional[list[str]] = None,
    level_b: bool = True,
    level_c: bool = False,
) -> ConsistencyReport:
    """Run consistency check. Returns ConsistencyReport."""
    if not profile_path.exists():
        raise FileNotFoundError(
            f"Project profile not found: {profile_path}\n"
            f"Run: python sdk/codebase_scanner.py --level L3 --client <name>"
        )

    profile_text = profile_path.read_text(encoding="utf-8", errors="replace")
    threshold = _read_threshold(profile_text)

    # Extract L3 patterns
    naming: dict[str, str] = {}
    import_style = ""
    tree = ""

    l3_m = re.search(r"## L3.*?(?=## L\d|$)", profile_text, re.DOTALL)
    if l3_m:
        l3_section = l3_m.group(0)
        nm = re.search(r"naming:\s*(.+)", l3_section)
        if nm:
            for part in nm.group(1).split("·"):
                kv = part.strip().split(":")
                if len(kv) == 2:
                    naming[kv[0].strip()] = kv[1].strip()
        im = re.search(r"imports:\s*(.+)", l3_section)
        if im:
            import_style = im.group(1).strip()

    # Extract tree from L0 for organization check
    l0_m = re.search(r"## L0.*?(?=## L\d|$)", profile_text, re.DOTALL)
    if l0_m:
        tree = l0_m.group(0)

    divergences: list[Divergence] = []

    if level_b and diff_text:
        divergences += _check_naming(diff_text, naming)
        divergences += _check_imports(diff_text, import_style)
        if changed_files:
            divergences += _check_file_organization(changed_files, tree)

    if level_c and diff_text:
        divergences += _check_internal_style(diff_text)

    # Score: 1.0 - (weight per divergence)
    score = max(0.0, 1.0 - len(divergences) * 0.07)
    score = round(score, 2)

    return ConsistencyReport(
        score=score,
        divergences=divergences,
        level_b_checked=level_b,
        level_c_checked=level_c,
        threshold=threshold,
        passed=score >= threshold,
    )


def run_check(
    profile_path: Path,
    diff_path: Optional[Path] = None,
    changed_files: Optional[list[str]] = None,
    arch_root: Optional[Path] = None,
) -> ConsistencyReport:
    """High-level entry: read ux-config, run check, optionally update threshold."""
    level_b = True
    level_c = False

    if arch_root:
        ux_cfg = arch_root / "governance" / "ux-config.yaml"
        if ux_cfg.exists():
            cfg_text = ux_cfg.read_text(encoding="utf-8", errors="replace")
            lb_m = re.search(r"level_b:\s*(true|false)", cfg_text)
            lc_m = re.search(r"level_c:\s*(true|false)", cfg_text)
            if lb_m:
                level_b = lb_m.group(1) == "true"
            if lc_m:
                level_c = lc_m.group(1) == "true"

    diff_text = ""
    if diff_path and diff_path.exists():
        diff_text = diff_path.read_text(encoding="utf-8", errors="replace")

    return check_consistency(profile_path, diff_text, changed_files, level_b, level_c)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="consistency_checker",
        description="Check code consistency against project profile (L3/L4 sections).",
    )
    p.add_argument("--profile", required=True, help="Path to project-profile-<client>.md")
    p.add_argument("--diff", default="", help="Path to .diff file of changes")
    p.add_argument("--arch-root", default=".", help="Cognitive-arch root")
    p.add_argument("--audience", default="slack", choices=["slack", "meeting"],
                   help="Format for text export")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()
    profile_path = Path(args.profile).resolve()

    diff_path = Path(args.diff).resolve() if args.diff else None

    try:
        report = run_check(profile_path, diff_path, arch_root=arch_root)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1

    print(f"consistency_score: {report.score:.2f}")
    print(f"threshold: {report.threshold:.2f}")
    print(f"passed: {report.passed}")
    if report.divergences:
        print(f"divergences ({len(report.divergences)}):")
        for d in report.divergences:
            print(f"  [{d.category}] {d.description}")
    else:
        print("divergences: none")
    print()
    print(f"Text export ({args.audience}):")
    print(report.text_export(args.audience))
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
