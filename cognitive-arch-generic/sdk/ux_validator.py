# PURPOSE: Validate AI output against governance/ux-voice.md rules. Always exits 0.
# INPUTS:  governance/ux-voice.md (rule source), target file or stdin string
# OUTPUTS: WARN lines per violation; exit code always 0
# DEPS:    stdlib only (pathlib, re, argparse, dataclasses)
# SEE:     governance/ux-voice.md, phases/phase-22.md block-134

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class Violation:
    line_num: int
    rule_id: str
    message: str
    excerpt: str


# ---------------------------------------------------------------------------
# Rule extraction from ux-voice.md
# ---------------------------------------------------------------------------

def _extract_prohibited(ux_voice_text: str) -> list[str]:
    """Extract prohibited phrases from the ```prohibited ... ``` fenced block."""
    m = re.search(r"```prohibited\s*\n(.*?)```", ux_voice_text, re.DOTALL)
    if not m:
        return []
    lines = m.group(1).strip().splitlines()
    return [ln.strip() for ln in lines if ln.strip()]


# ---------------------------------------------------------------------------
# UxValidator
# ---------------------------------------------------------------------------

class UxValidator:
    def __init__(self, prohibited_phrases: list[str]) -> None:
        self.prohibited_phrases = prohibited_phrases

    @classmethod
    def from_ux_voice(cls, arch_root: Path) -> "UxValidator":
        """Factory: reads governance/ux-voice.md and extracts rules."""
        ux_path = arch_root / "governance" / "ux-voice.md"
        try:
            text = ux_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        return cls(_extract_prohibited(text))

    def check(self, text: str) -> list[Violation]:
        """Scan text for violations. Skips ```prohibited blocks (rule definitions)."""
        violations: list[Violation] = []
        lines = text.splitlines()
        in_prohibited_block = False
        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped == "```prohibited":
                in_prohibited_block = True
                continue
            if in_prohibited_block:
                if stripped == "```":
                    in_prohibited_block = False
                continue
            for phrase in self.prohibited_phrases:
                if re.search(re.escape(phrase), line, re.IGNORECASE):
                    excerpt = stripped[:80]
                    violations.append(Violation(
                        line_num=line_num,
                        rule_id="UX-PROHIBITED",
                        message=f'Prohibited phrase: "{phrase}"',
                        excerpt=excerpt,
                    ))
        return violations


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _format_violations(violations: list[Violation], max_display: int = 20) -> str:
    if not violations:
        return "[ux_validator] OK — 0 violations\n"
    shown = violations[:max_display]
    lines = [f"[ux_validator] {len(violations)} violation(s) found:\n"]
    for v in shown:
        lines.append(f"  WARN  L{v.line_num}  {v.rule_id}: {v.message}\n")
        lines.append(f"        → {v.excerpt}\n")
    if len(violations) > max_display:
        lines.append(f"  ... and {len(violations) - max_display} more.\n")
    return "".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate text against ux-voice.md rules. Always exits 0."
    )
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--check", metavar="FILE_OR_STRING",
                        help="File path to validate, or literal string if --string is set")
    parser.add_argument("--string", action="store_true",
                        help="Treat --check value as literal text, not a file path")
    parser.add_argument("--max-violations", type=int, default=20)
    args = parser.parse_args(argv)

    root = Path(args.arch_root).resolve()
    validator = UxValidator.from_ux_voice(root)

    if not validator.prohibited_phrases:
        print("[ux_validator] WARNING: no prohibited phrases loaded from ux-voice.md")

    if args.check:
        if args.string:
            text = args.check
        else:
            target = Path(args.check)
            if not target.is_absolute():
                target = root / args.check
            try:
                text = target.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                print(f"[ux_validator] ERROR: cannot read {args.check}: {e}")
                return 0  # always exit 0
    else:
        text = sys.stdin.read()

    violations = validator.check(text)
    print(_format_violations(violations, max_display=args.max_violations), end="")
    return 0  # always exit 0


if __name__ == "__main__":
    raise SystemExit(main())
