# sdk/codebase_scanner.py
# PURPOSE: Scan a codebase at L0–L4 levels; produce project-profile-<client>.md + HTML dossier.
#          Core CLI entry point for Phase 30 scanner feature.
#          Operates at distance: --target-repo points outside cognitive-arch.
#          Compliant: profile stores only metadata, never real client code.
# INPUTS:  --target-repo, --level, --client, --context, --ticket, --area, --arch-root
# OUTPUTS: governance/project-profile-<client>.md, governance/scanner-output-<client>-<ts>.html
# DEPS:    stdlib only; sdk/scanner_profile, sdk/scanner_deep, sdk/scanner_html, sdk/scanner_adaptive
# USAGE:   python sdk/codebase_scanner.py --target-repo /path/to/repo --level L0 --client acme
# SEE:     design/scanner.md

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 on Windows
def _fix_utf8() -> None:
    import io as _io
    if sys.platform == "win32":
        if hasattr(sys.stdout, "buffer") and not (
            isinstance(sys.stdout, _io.TextIOWrapper) and sys.stdout.encoding.lower() == "utf-8"
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_fix_utf8()


def _import_sdk(arch_root: Path) -> None:
    sdk_str = str(arch_root / "sdk")
    if sdk_str not in sys.path:
        sys.path.insert(0, sdk_str)


# ---------------------------------------------------------------------------
# File tree helpers
# ---------------------------------------------------------------------------

def _read_gitignore(repo: Path) -> set[str]:
    """Return set of ignore patterns from .gitignore."""
    patterns: set[str] = set()
    gi = repo / ".gitignore"
    if gi.exists():
        for line in gi.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.add(line.rstrip("/"))
    return patterns


def _is_ignored(rel: str, patterns: set[str]) -> bool:
    """Simple .gitignore heuristic: skip if any part matches a pattern."""
    parts = Path(rel).parts
    for pat in patterns:
        if pat in parts:
            return True
        if parts and re.fullmatch(pat.replace("*", ".*"), parts[0]):
            return True
    return False


def _count_files(repo: Path) -> tuple[int, int]:
    """Return (total_files, relevant_files) respecting .gitignore."""
    patterns = _read_gitignore(repo)
    always_skip = {".git", "__pycache__", "node_modules", "dist", "build", ".next"}
    total = relevant = 0
    for p in repo.rglob("*"):
        if not p.is_file():
            continue
        total += 1
        rel = str(p.relative_to(repo))
        parts = Path(rel).parts
        if any(s in parts for s in always_skip):
            continue
        if _is_ignored(rel, patterns):
            continue
        relevant += 1
    return total, relevant


def _collect_files(repo: Path, area: str | None = None) -> list[Path]:
    """Collect relevant source files from repo, optionally limited to area."""
    patterns = _read_gitignore(repo)
    always_skip = {".git", "__pycache__", "node_modules", "dist", "build", ".next",
                   ".venv", "venv", "coverage", ".coverage"}
    code_exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".rb",
                 ".cs", ".cpp", ".c", ".h", ".swift", ".kt", ".scala", ".vue",
                 ".json", ".yaml", ".yml", ".toml", ".md"}

    root = repo / area if area else repo
    if not root.exists():
        root = repo  # fallback

    files = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in code_exts:
            continue
        rel = str(p.relative_to(repo))
        parts = Path(rel).parts
        if any(s in parts for s in always_skip):
            continue
        if _is_ignored(rel, patterns):
            continue
        files.append(p)
    return sorted(files)


def _detect_languages(files: list[Path], repo: Path) -> dict[str, float]:
    """Return {ext: percentage} language distribution."""
    counts: dict[str, int] = {}
    lang_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".tsx": "TypeScript/React", ".jsx": "JavaScript/React",
        ".java": "Java", ".go": "Go", ".rs": "Rust", ".rb": "Ruby",
        ".cs": "C#", ".cpp": "C++", ".c": "C", ".swift": "Swift",
        ".kt": "Kotlin", ".scala": "Scala", ".vue": "Vue",
    }
    total = 0
    for f in files:
        ext = f.suffix
        lang = lang_map.get(ext, ext)
        counts[lang] = counts.get(lang, 0) + 1
        total += 1
    if total == 0:
        return {}
    return {lang: round(count / total * 100, 1) for lang, count in
            sorted(counts.items(), key=lambda x: -x[1])}


def _detect_entry_points(files: list[Path], repo: Path) -> list[str]:
    """Heuristic detection of project entry points."""
    candidates = [
        "main.py", "app.py", "index.py", "server.py", "run.py",
        "index.ts", "index.js", "main.ts", "main.js",
        "src/main.py", "src/app.py", "src/index.ts", "src/index.js",
        "src/app/page.tsx", "src/app/layout.tsx",
        "main.go", "main.rs", "Main.java",
    ]
    found = []
    for c in candidates:
        if (repo / c).exists():
            found.append(c)
    return found[:5]


def _detect_stack(repo: Path) -> dict[str, str]:
    """Detect stack from config files."""
    stack: dict[str, str] = {}

    # Package.json (Node/npm)
    pkg = repo / "package.json"
    if pkg.exists():
        try:
            import json
            data = json.loads(pkg.read_text(encoding="utf-8", errors="replace"))
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            frameworks = []
            if "next" in deps:
                frameworks.append(f"Next.js {deps['next']}")
            if "react" in deps:
                frameworks.append(f"React {deps.get('react', '')}")
            if "vue" in deps:
                frameworks.append("Vue")
            if "express" in deps:
                frameworks.append("Express")
            if "fastapi" in deps or "fastapi" in str(data):
                frameworks.append("FastAPI")
            if frameworks:
                stack["framework"] = " + ".join(frameworks)
            stack["runtime"] = "Node.js"
            if "typescript" in deps or "ts-node" in deps:
                stack["lang"] = "TypeScript"
            else:
                stack["lang"] = "JavaScript"
        except Exception:
            stack["runtime"] = "Node.js"

    # Python requirements / pyproject
    for rf in ["requirements.txt", "pyproject.toml", "setup.py"]:
        if (repo / rf).exists():
            stack["runtime"] = stack.get("runtime", "Python")
            stack["lang"] = "Python"
            text = (repo / rf).read_text(encoding="utf-8", errors="replace").lower()
            if "fastapi" in text:
                stack["framework"] = stack.get("framework", "FastAPI")
            elif "django" in text:
                stack["framework"] = stack.get("framework", "Django")
            elif "flask" in text:
                stack["framework"] = stack.get("framework", "Flask")
            break

    # Go
    if (repo / "go.mod").exists():
        stack["runtime"] = "Go"
        stack["lang"] = "Go"

    # Rust
    if (repo / "Cargo.toml").exists():
        stack["runtime"] = "Rust"
        stack["lang"] = "Rust"

    # Java / Maven / Gradle
    if (repo / "pom.xml").exists():
        stack["runtime"] = "JVM/Maven"
        stack["lang"] = "Java"
    elif (repo / "build.gradle").exists() or (repo / "build.gradle.kts").exists():
        stack["runtime"] = "JVM/Gradle"
        stack["lang"] = "Kotlin/Java"

    # Docker / k8s / cloud
    if (repo / "Dockerfile").exists() or list(repo.glob("docker-compose*.yml")):
        stack["infra"] = "Docker"
    if list(repo.glob("*.yml")) and any("kind: Deployment" in f.read_text(encoding="utf-8", errors="replace")
                                        for f in repo.glob("*.yml") if f.is_file()):
        stack["infra"] = stack.get("infra", "") + "+k8s"

    # CI
    if (repo / ".github" / "workflows").exists():
        stack["ci"] = "GitHub Actions"
    elif (repo / ".gitlab-ci.yml").exists():
        stack["ci"] = "GitLab CI"
    elif (repo / "Jenkinsfile").exists():
        stack["ci"] = "Jenkins"

    return stack


def _extract_dependencies(repo: Path) -> list[str]:
    """Extract main dependencies from package.json, requirements.txt, etc."""
    deps: list[str] = []

    pkg = repo / "package.json"
    if pkg.exists():
        try:
            import json
            data = json.loads(pkg.read_text(encoding="utf-8", errors="replace"))
            all_deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            deps = [f"{k}@{v}" for k, v in list(all_deps.items())[:10]]
        except Exception:
            pass

    req = repo / "requirements.txt"
    if req.exists() and not deps:
        deps = [l.strip() for l in req.read_text(encoding="utf-8", errors="replace").splitlines()
                if l.strip() and not l.startswith("#")][:10]

    return deps


def _build_dir_tree(repo: Path, max_depth: int = 3) -> list[str]:
    """Build annotated directory tree."""
    type_labels = {
        "components": "UI components", "pages": "pages/routes", "api": "API handlers",
        "services": "services", "models": "data models", "controllers": "controllers",
        "utils": "utilities", "helpers": "helpers", "hooks": "hooks",
        "store": "state store", "context": "context providers",
        "tests": "tests", "test": "tests", "__tests__": "tests",
        "middleware": "middleware", "routes": "routes",
        "features": "features (FSD)", "shared": "shared (FSD)", "entities": "entities (FSD)",
        "lib": "library code", "core": "core logic", "domain": "domain layer",
        "infrastructure": "infra layer", "presentation": "presentation layer",
        "config": "configuration", "scripts": "build scripts",
        "public": "static assets", "assets": "assets", "static": "static files",
        "migrations": "DB migrations", "schemas": "schemas",
    }
    lines = []

    def _walk(p: Path, depth: int, prefix: str) -> None:
        if depth > max_depth:
            return
        try:
            entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
        except PermissionError:
            return
        skip = {".git", "__pycache__", "node_modules", "dist", "build", ".next",
                ".venv", "venv", ".pytest_cache"}
        dirs = [e for e in entries if e.is_dir() and e.name not in skip][:12]
        for d in dirs:
            label = type_labels.get(d.name.lower(), "")
            tag = f"  [{label}]" if label else ""
            lines.append(f"{prefix}{d.name}/{tag}")
            _walk(d, depth + 1, prefix + "  ")

    _walk(repo, 0, "")
    return lines[:50]  # cap for profile size


# ---------------------------------------------------------------------------
# L0 scan
# ---------------------------------------------------------------------------

def scan_l0(repo: Path, context: str = "") -> dict:
    """Scan macro architecture + domain logic (one time, deep)."""
    stack = _detect_stack(repo)
    files = _collect_files(repo)
    deps = _extract_dependencies(repo)
    tree = _build_dir_tree(repo)

    # System type heuristic
    sys_type = "unknown"
    if stack.get("infra") and "k8s" in stack.get("infra", ""):
        sys_type = "microservices"
    elif stack.get("framework") and "Next.js" in stack.get("framework", ""):
        sys_type = "web-fullstack"
    elif stack.get("framework") and any(f in stack.get("framework", "") for f in ["Express", "FastAPI", "Django", "Flask"]):
        sys_type = "web-api"
    elif stack.get("lang") in ("Go", "Rust"):
        sys_type = "service"
    elif stack.get("runtime", "").startswith("JVM"):
        sys_type = "jvm-app"
    elif stack.get("lang") == "Python":
        sys_type = "python-app"

    # Domain logic: read entry point files for entity/flow extraction
    domain_entities: list[str] = []
    domain_flows: list[str] = []

    # Scan model/entity files for domain concepts
    for f in files:
        if any(part in f.parts for part in ("models", "entities", "domain", "schemas")):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
                # Extract class/model names (max 5 per file, max 20 total)
                for m in re.finditer(r"^class\s+(\w+)", text, re.MULTILINE):
                    name = m.group(1)
                    if not any(skip in name for skip in ("Test", "Mock", "Base", "Mixin")):
                        if name not in domain_entities:
                            domain_entities.append(name)
                if len(domain_entities) >= 15:
                    break
            except Exception:
                pass

    # Extract from context if provided
    if context:
        domain_flows.append(context)

    return {
        "sys_type": sys_type,
        "stack": stack,
        "deps": deps[:10],
        "tree": tree,
        "domain_entities": domain_entities[:15],
        "domain_flows": domain_flows,
        "file_count": len(files),
    }


# ---------------------------------------------------------------------------
# L1 scan
# ---------------------------------------------------------------------------

def scan_l1(repo: Path) -> dict:
    """Scan structure and languages."""
    files = _collect_files(repo)
    langs = _detect_languages(files, repo)
    entries = _detect_entry_points(files, repo)
    deps = _extract_dependencies(repo)
    tree = _build_dir_tree(repo)

    return {
        "languages": langs,
        "entry_points": entries,
        "deps": deps,
        "tree": tree,
        "file_count": len(files),
    }


# ---------------------------------------------------------------------------
# Profile update
# ---------------------------------------------------------------------------

def _update_profile_l0(profile, result: dict) -> None:
    stack = result["stack"]
    stack_str = " · ".join(f"{k}: {v}" for k, v in stack.items() if v)
    lines = [
        f"tipo: {result['sys_type']}",
        f"stack: {stack_str}",
    ]
    if result["deps"]:
        lines.append(f"deps_principais: {', '.join(result['deps'][:5])}")
    if result["domain_entities"]:
        lines.append(f"entidades: {', '.join(result['domain_entities'])}")
    if result["domain_flows"]:
        lines.append(f"fluxos_contexto: {', '.join(result['domain_flows'])}")
    lines.append(f"arquivos_relevantes: {result['file_count']}")
    if result["tree"]:
        lines.append("\nárvore_dirs:")
        for t in result["tree"][:20]:
            lines.append(f"  {t}")
    profile.set_section("L0", lines)


def _update_profile_l1(profile, result: dict) -> None:
    langs_str = " · ".join(f"{l} ({p}%)" for l, p in list(result["languages"].items())[:5])
    lines = [
        f"linguagens: {langs_str or 'desconhecidas'}",
        f"arquivos: {result['file_count']}",
    ]
    if result["entry_points"]:
        lines.append(f"entry_points: {', '.join(result['entry_points'])}")
    if result["deps"]:
        lines.append(f"deps_principais: {', '.join(result['deps'][:5])}")
    profile.set_section("L1", lines)


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

def _estimate_tokens(file_count: int, level: str) -> tuple[int, float]:
    """Rough token estimation. Returns (tokens, usd_estimate)."""
    chars_per_file = {"L0": 500, "L1": 200, "L2": 800, "L3": 600, "L4": 400}
    chars = file_count * chars_per_file.get(level, 500)
    tokens = chars // 4
    usd = tokens * 0.000003  # rough sonnet pricing
    return tokens, round(usd, 4)


# ---------------------------------------------------------------------------
# Main scanner
# ---------------------------------------------------------------------------

def run_scan(
    target_repo: Path,
    level: str,
    arch_root: Path,
    client: str,
    context: str = "",
    area: str | None = None,
    refresh: bool = False,
    no_html: bool = False,
) -> dict:
    """Run a scan at the given level. Returns result dict."""
    _import_sdk(arch_root)
    from scanner_profile import ProjectProfile

    profile = ProjectProfile(arch_root, client)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    total_tokens = 0

    print(f"[scanner] Target: {target_repo}")
    print(f"[scanner] Level: {level} | Client: {client} | Area: {area or 'full'}")

    results: dict = {"level": level, "client": client}

    if level in ("L0", "L1", "L0+L1"):
        # L0 and L1 always run together
        file_count = len(_collect_files(target_repo, area))
        tok, usd = _estimate_tokens(file_count, "L0")
        total_tokens += tok
        print(f"[scanner] L0+L1: reading {file_count} files (~{tok} tokens, ~${usd})")

        l0 = scan_l0(target_repo, context)
        l1 = scan_l1(target_repo)

        _update_profile_l0(profile, l0)
        _update_profile_l1(profile, l1)

        results["l0"] = l0
        results["l1"] = l1

    elif level in ("L2", "L3", "L4", "L2+L3", "L2+L3+L4"):
        # Deep scan — delegated to scanner_deep (block-167)
        try:
            from scanner_deep import scan_deep
            deep_result = scan_deep(target_repo, level, arch_root, client, context, area)
            results.update(deep_result)
            tok, _ = _estimate_tokens(deep_result.get("file_count", 50), level)
            total_tokens += tok
        except ImportError:
            print("[scanner] WARN: scanner_deep.py not yet available — L2/L3/L4 scan skipped")
            results["error"] = "scanner_deep not available"

    profile.save()
    print(f"[scanner] Profile updated: {profile.path}")
    results["profile_path"] = str(profile.path)
    results["tokens_used"] = total_tokens
    results["usd_estimate"] = round(total_tokens * 0.000003, 4)

    # HTML generation (block-168)
    if not no_html:
        try:
            from scanner_html import generate_html
            # Read ux-config
            ux_cfg = arch_root / "governance" / "ux-config.yaml"
            html_enabled = True
            if ux_cfg.exists():
                text = ux_cfg.read_text(encoding="utf-8", errors="replace")
                m = re.search(r"^scanner_html_output:\s*(true|false)", text, re.MULTILINE)
                if m:
                    html_enabled = m.group(1) == "true"
            if html_enabled:
                html_path = generate_html(profile, results, arch_root, ts)
                results["html_path"] = str(html_path)
                print(f"[scanner] HTML dossier: {html_path}")
        except ImportError:
            pass  # HTML generator not yet available

    print(f"[scanner] Cost: ~{total_tokens} tokens | ~${results['usd_estimate']} USD")

    # Update PilotState.last_scan_at
    try:
        from state_manager import read_state, update_state
        update_state(arch_root, {"last_scan_at": datetime.now(timezone.utc).strftime("%Y-%m-%d")})
    except Exception:
        pass

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="codebase_scanner",
        description="Scan a codebase at L0-L4; produce project-profile + HTML dossier.",
    )
    p.add_argument("--target-repo", required=True, help="Path to repo to scan")
    p.add_argument("--level", default="L0",
                   choices=["L0", "L1", "L0+L1", "L2", "L3", "L4", "L2+L3", "L2+L3+L4"],
                   help="Scan level")
    p.add_argument("--context", default="", help="Optional free-text context / objective")
    p.add_argument("--ticket", default="", help="Ticket text — infers area then confirms")
    p.add_argument("--area", default="", help="Sub-path to scan (partial scan)")
    p.add_argument("--refresh-level", metavar="LEVEL", help="Force re-scan of a specific level")
    p.add_argument("--client", default="", help="Client/project name (required for multi-client)")
    p.add_argument("--no-html", action="store_true", help="Suppress HTML generation")
    p.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()
    target_repo = Path(args.target_repo).resolve()

    if not target_repo.exists():
        print(f"[scanner] ERROR: --target-repo not found: {target_repo}")
        return 1

    client = args.client or target_repo.name

    level = args.refresh_level or args.level

    # Ticket inference — delegated to scanner_adaptive (block-169)
    if args.ticket:
        _import_sdk(arch_root)
        try:
            from scanner_adaptive import infer_area_from_ticket
            area = infer_area_from_ticket(args.ticket, target_repo)
        except ImportError:
            area = args.area or None
    else:
        area = args.area or None

    # Adaptive mode for large repos (block-169)
    _import_sdk(arch_root)
    try:
        from scanner_adaptive import adaptive_preflight
        proceed = adaptive_preflight(target_repo, level, area)
        if not proceed:
            print("[scanner] Scan cancelled by user.")
            return 0
    except ImportError:
        pass  # adaptive not yet available

    run_scan(target_repo, level, arch_root, client, args.context, area,
             no_html=args.no_html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
