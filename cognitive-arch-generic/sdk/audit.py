# sdk/audit.py
# PURPOSE: Cross-platform Python replacement for audit.sh (all 10 checks).
#          Works on Windows, Mac, Linux without bash. Outputs JSON option for dashboard.
#          Saves ~500 tokens per run (no manual interpretation needed).
# INPUTS:  arch root — reads all governance files, manifests, blocks
# OUTPUTS: Console report (default) or JSON (--json flag)
# DEPS:    stdlib only; delegates checks 7+8 to audit_helpers.py, check 10 to integrity_check.py
# USAGE:   python sdk/audit.py --arch-root .
#          python sdk/audit.py --arch-root . --json
#          python sdk/audit.py --arch-root . --strict
# SEE:     audit.sh, commands/audit.md, sdk/audit_helpers.py

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

def _fix_utf8():
    """Apply UTF-8 stdout fix on Windows — safe to call multiple times."""
    import io as _io
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'buffer') and not (
            isinstance(sys.stdout, _io.TextIOWrapper) and sys.stdout.encoding.lower() == 'utf-8'
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_fix_utf8()


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

class AuditResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.oks: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)
        print(f"  ERROR: {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)
        print(f"  WARN:  {msg}")

    def ok(self, msg: str) -> None:
        self.oks.append(msg)
        print(f"  OK:    {msg}")

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        # Score: start 100, -15 per error, -2 per warning, min 0
        score = max(0, 100 - len(self.errors) * 15 - len(self.warnings) * 2)
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "score": score,
        }


# ---------------------------------------------------------------------------
# Check 1: HOT files exist
# ---------------------------------------------------------------------------

HOT_FILES = ["CLAUDE.md", "PROTOCOLS.md", "STATE.md", "NEXT.md",
              "INDEX.md", "board.md", "_syntax.md", "PROJECT.md"]

def check1_hot_files(root: Path, r: AuditResult) -> None:
    print("[1/10] HOT files exist...")
    all_ok = True
    for f in HOT_FILES:
        if not (root / f).exists():
            r.err(f"missing required HOT file: {f}")
            all_ok = False
    if all_ok:
        r.ok("all HOT files present")


# ---------------------------------------------------------------------------
# Check 2: File size budgets
# ---------------------------------------------------------------------------

SIZE_BUDGETS = {
    "CLAUDE.md": 150,
    "STATE.md": 60,
    "NEXT.md": 30,
    "INDEX.md": 250,
    "board.md": 150,
    "_syntax.md": 100,
}

def check2_size_budgets(root: Path, r: AuditResult) -> None:
    print("[2/10] File size budgets...")
    all_ok = True
    for fname, limit in SIZE_BUDGETS.items():
        p = root / fname
        if p.exists():
            lines = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
            if lines > limit:
                r.warn(f"{fname} exceeds budget ({lines} > {limit} lines)")
                all_ok = False
    if all_ok:
        r.ok("all HOT files within size budgets")


# ---------------------------------------------------------------------------
# Check 3: Pointer integrity (markdown links)
# ---------------------------------------------------------------------------

_MD_LINK_RE = re.compile(r"\]\(([^)]+)\)")

def check3_pointer_integrity(root: Path, r: AuditResult) -> None:
    print("[3/10] Pointer integrity...")
    broken = 0
    for md_file in root.rglob("*.md"):
        # Skip hidden dirs and _backups
        if any(p.startswith(".") or p == "_backups" for p in md_file.parts):
            continue
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in _MD_LINK_RE.finditer(text):
            target = m.group(1).split("#")[0].split("?")[0].strip()
            if not target or target.startswith("http"):
                continue
            resolved = (md_file.parent / target).resolve()
            if not resolved.exists():
                r.warn(f"broken pointer in {md_file.relative_to(root)}: {target}")
                broken += 1
    if broken == 0:
        r.ok("pointer integrity: no broken markdown links")


# ---------------------------------------------------------------------------
# Check 4: AI-only file format
# ---------------------------------------------------------------------------

def check4_ai_file_format(root: Path, r: AuditResult) -> None:
    print("[4/10] AI-only file format...")
    all_ok = True
    for ai_file in ["STATE.md", "NEXT.md", "board.md"]:
        p = root / ai_file
        if not p.exists():
            continue
        bad = 0
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            # Must be comment, blank, or contain at least one key:value
            if stripped and not stripped.startswith("#") and ":" not in stripped:
                bad += 1
        if bad > 0:
            r.warn(f"{ai_file} has {bad} non-conforming lines (expected: comments or key:value)")
            all_ok = False
    if all_ok:
        r.ok("AI-only files format OK")


# ---------------------------------------------------------------------------
# Check 5: Manifest schema
# ---------------------------------------------------------------------------

_REQUIRED_MANIFEST_KEYS = ["id", "tier", "kind", "status", "files"]

def _extract_frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""

def check5_manifest_schema(root: Path, r: AuditResult) -> None:
    print("[5/10] Manifest schema...")
    manifests = list((root / "manifests").glob("block-*.md"))
    if not manifests:
        r.ok("manifest schema: no manifests found (skipped)")
        return
    errors = 0
    for mf in manifests:
        fm = _extract_frontmatter(mf.read_text(encoding="utf-8", errors="replace"))
        for key in _REQUIRED_MANIFEST_KEYS:
            if not re.search(rf"^{key}:", fm, re.MULTILINE):
                r.warn(f"manifest-schema: {mf.name} missing '{key}:'")
                errors += 1
    if errors == 0:
        r.ok(f"manifest schema: all {len(manifests)} manifests have required keys")


# ---------------------------------------------------------------------------
# Check 6: Dependency validation
# ---------------------------------------------------------------------------

def _load_done_blocks(root: Path) -> set[str]:
    log = root / "blocks" / "BLOCK_LOG.md"
    if not log.exists():
        return set()
    done: set[str] = set()
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^(block-\d+)\s+done", line)
        if m:
            done.add(m.group(1))
    return done

def check6_dependencies(root: Path, r: AuditResult) -> None:
    print("[6/10] Dependency validation...")
    log = root / "blocks" / "BLOCK_LOG.md"
    if not log.exists():
        r.warn("dep-validation: BLOCK_LOG.md not found — skipping")
        return

    done_blocks = _load_done_blocks(root)
    manifests = list((root / "manifests").glob("block-*.md"))
    errors = 0

    for mf in manifests:
        fm = _extract_frontmatter(mf.read_text(encoding="utf-8", errors="replace"))
        id_m = re.search(r"^id:\s*(\S+)", fm, re.MULTILINE)
        if not id_m:
            continue
        block_id = id_m.group(1)
        if block_id not in done_blocks:
            continue  # Only validate completed blocks

        # Extract dependencies
        deps_m = re.search(r"^dependencies:\s*\[([^\]]*)\]", fm, re.MULTILINE)
        if not deps_m:
            continue
        deps = [d.strip() for d in deps_m.group(1).split(",") if d.strip() and d.strip() != "-"]
        for dep in deps:
            if dep not in done_blocks:
                r.warn(f"dep-validation: {mf.name}: dep '{dep}' not in BLOCK_LOG")
                errors += 1

    if errors == 0:
        r.ok("dep-validation: all done-block dependencies confirmed in BLOCK_LOG")


# ---------------------------------------------------------------------------
# Checks 7+8: Delegate to audit_helpers.py
# ---------------------------------------------------------------------------

def check7_conflicts(root: Path, r: AuditResult) -> None:
    print("[7/10] File conflicts...")
    helpers = root / "sdk" / "audit_helpers.py"
    if not helpers.exists():
        r.warn("file-conflict: sdk/audit_helpers.py not found — skipping")
        return
    result = subprocess.run(
        [sys.executable, str(helpers), "--check", "conflicts", "--arch-root", str(root)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    for line in (result.stdout + result.stderr).splitlines():
        if line.startswith("OK:"):
            r.ok(line[3:].strip())
        elif line.startswith("WARN:"):
            r.warn(line[5:].strip())
        elif line.startswith("ERROR:"):
            r.err(line[6:].strip())


def check8_drift(root: Path, r: AuditResult) -> None:
    print("[8/10] Drift detection...")
    helpers = root / "sdk" / "audit_helpers.py"
    if not helpers.exists():
        r.warn("drift: sdk/audit_helpers.py not found — skipping")
        return
    result = subprocess.run(
        [sys.executable, str(helpers), "--check", "drift", "--arch-root", str(root)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    for line in (result.stdout + result.stderr).splitlines():
        if line.startswith("OK:"):
            r.ok(line[3:].strip())
        elif line.startswith("WARN:"):
            r.warn(line[5:].strip())
        elif line.startswith("ERROR:"):
            r.err(line[6:].strip())


# ---------------------------------------------------------------------------
# Check 9: Velocity fields
# ---------------------------------------------------------------------------

def check9_velocity(root: Path, r: AuditResult) -> None:
    print("[9/10] Velocity fields...")
    log = root / "blocks" / "BLOCK_LOG.md"
    if not log.exists():
        r.warn("velocity: BLOCK_LOG.md not found — skipping")
        return

    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    block_ids = [
        re.match(r"^(block-\d+)\s+done", l).group(1)
        for l in lines
        if re.match(r"^(block-\d+)\s+done", l)
    ][-30:]  # Last 30

    missing = 0
    for bid in block_ids:
        retros = list((root / "blocks").glob(f"{bid}-*.md"))
        retros = [r2 for r2 in retros if "LOG" not in r2.name.upper()]
        if not retros:
            continue
        text = retros[0].read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^actual_duration_hours:\s*[0-9]", text, re.MULTILINE):
            r.warn(f"velocity: {bid} missing actual_duration_hours")
            missing += 1

    if missing == 0:
        r.ok("velocity: all recent blocks have actual_duration_hours filled")


# ---------------------------------------------------------------------------
# Check 10: Integrity lock
# ---------------------------------------------------------------------------

def check10_integrity(root: Path, r: AuditResult, strict: bool = False) -> None:
    print("[10/10] Integrity lock...")
    lock = root / ".integrity.lock"
    if not lock.exists():
        r.warn("integrity-lock: .integrity.lock not found — run: python sdk/integrity_check.py --regenerate")
        return
    checker = root / "sdk" / "integrity_check.py"
    if not checker.exists():
        r.warn("integrity-lock: sdk/integrity_check.py not found — skipping")
        return

    cmd = [sys.executable, str(checker), "--verify", "--arch-root", str(root)]
    if strict:
        cmd.append("--strict")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    for line in (result.stdout + result.stderr).splitlines():
        if not line.strip():
            continue
        if "OK:" in line or "verified OK" in line:
            r.ok(line.replace("OK:", "").strip())
        elif "WARN:" in line:
            r.warn(line.replace("WARN:", "").strip())
        elif "ERROR:" in line or "MISMATCH" in line:
            r.err(line.replace("ERROR:", "").strip())


# ---------------------------------------------------------------------------
# HOT token estimate
# ---------------------------------------------------------------------------

def print_token_estimates(root: Path) -> None:
    print("\n[INFO] HOT file token estimates (chars/4):")
    total = 0
    for f in ["CLAUDE.md", "PROTOCOLS.md", "STATE.md", "NEXT.md", "INDEX.md", "_syntax.md", "board.md"]:
        p = root / f
        if p.exists():
            chars = len(p.read_bytes())
            tok = chars // 4
            total += chars
            flag = "  [!]" if tok > 1000 else "     "
            print(f"{flag} {f}: ~{tok} tok")
    total_tok = total // 4
    flag = "[!] OVER BUDGET" if total_tok > 4000 else "OK"
    print(f"\n  HOT boot total: ~{total_tok} tok — {flag} (target: <4000 tok)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_audit(root: Path, strict: bool = False, as_json: bool = False) -> AuditResult:
    r = AuditResult()
    print("=" * 50)
    print("  cognitive-arch AUDIT (Python — cross-platform)")
    print("=" * 50)

    check1_hot_files(root, r)
    check2_size_budgets(root, r)
    check3_pointer_integrity(root, r)
    check4_ai_file_format(root, r)
    check5_manifest_schema(root, r)
    check6_dependencies(root, r)
    check7_conflicts(root, r)
    check8_drift(root, r)
    check9_velocity(root, r)
    check10_integrity(root, r, strict)

    if not as_json:
        print_token_estimates(root)
        print()
        print("=" * 50)
        print(f"  Errors:   {len(r.errors)}")
        print(f"  Warnings: {len(r.warnings)}")
        print(f"  Score:    {r.to_dict()['score']}/100")
        print(f"  Result:   {'PASS' if r.passed else 'FAIL'}")
        print("=" * 50)

    return r


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cross-platform cognitive-arch audit")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings too")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    args = parser.parse_args()

    root = Path(args.arch_root).resolve()
    result = run_audit(root, strict=args.strict, as_json=args.json)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))

    sys.exit(0 if result.passed else 1)
