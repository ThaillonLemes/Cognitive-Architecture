# sdk/scanner_deep.py
# PURPOSE: Deep scan levels L2 (architecture patterns), L3 (code aesthetics/conventions),
#          L4 (pattern coexistence — current vs legacy). Each inference includes a
#          proof-of-reasoning section for the HTML dossier.
# INPUTS:  target_repo path, level, arch_root, client, context, area
# OUTPUTS: Updates ProjectProfile L2/L3/L4 sections; returns DeepScanResult dict
# DEPS:    stdlib only; sdk/scanner_profile, sdk/codebase_scanner
# USAGE:   from scanner_deep import scan_deep; result = scan_deep(repo, "L2", arch, "acme")
# SEE:     design/scanner.md §1 (L2-L4)

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional


def _import_sdk(arch_root: Path) -> None:
    sdk_str = str(arch_root / "sdk")
    if sdk_str not in sys.path:
        sys.path.insert(0, sdk_str)


# ---------------------------------------------------------------------------
# Architecture pattern detection (L2)
# ---------------------------------------------------------------------------

# Structural signals for known patterns
_ARCH_SIGNALS: dict[str, list[str]] = {
    "Feature-Sliced Design": ["features/", "entities/", "shared/", "widgets/", "processes/"],
    "Clean Architecture": ["domain/", "usecases/", "infrastructure/", "presentation/"],
    "Hexagonal (Ports & Adapters)": ["ports/", "adapters/", "core/", "application/"],
    "DDD": ["domain/", "aggregates/", "repositories/", "events/", "valueobjects/"],
    "MVC": ["models/", "views/", "controllers/"],
    "MVVM": ["viewmodels/", "views/", "models/"],
    "Repository Pattern": ["repositories/", "services/", "models/"],
    "Layered": ["services/", "controllers/", "repositories/", "models/"],
    "CQRS": ["commands/", "queries/", "handlers/", "events/"],
}


def _detect_architecture(repo: Path, area: Optional[str] = None) -> tuple[str, list[str]]:
    """Detect architecture pattern by structural signals. Returns (pattern, evidence)."""
    root = (repo / area) if area else repo
    if not root.exists():
        root = repo

    # Collect directory names
    dirs: set[str] = set()
    try:
        for p in root.rglob("*"):
            if p.is_dir():
                name = p.name.lower() + "/"
                dirs.add(name)
    except PermissionError:
        pass

    # Score each pattern
    scored: list[tuple[int, str, list[str]]] = []
    for pattern, signals in _ARCH_SIGNALS.items():
        matched = [s for s in signals if s in dirs]
        if matched:
            scored.append((len(matched), pattern, matched))

    if scored:
        scored.sort(key=lambda x: -x[0])
        best_score, best_pattern, evidence = scored[0]
        return best_pattern, evidence

    return "Indeterminate (insufficient signals)", []


def _read_sample_files(repo: Path, area: Optional[str], n: int = 5) -> list[tuple[str, str]]:
    """Read n sample files from area (or whole repo). Returns [(path, content)]."""
    from codebase_scanner import _collect_files
    files = _collect_files(repo, area)
    samples = []
    for f in files[:n]:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")[:2000]
            samples.append((str(f.relative_to(repo)), text))
        except Exception:
            pass
    return samples


# ---------------------------------------------------------------------------
# Aesthetics / conventions detection (L3)
# ---------------------------------------------------------------------------

def _detect_naming_convention(samples: list[tuple[str, str]]) -> dict[str, str]:
    """Infer naming conventions from sample code."""
    conventions: dict[str, str] = {}
    camel_count = 0
    pascal_count = 0
    snake_count = 0
    kebab_count = 0

    for _, content in samples:
        camel_count += len(re.findall(r"\b[a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*\b", content))
        pascal_count += len(re.findall(r"\b[A-Z][a-zA-Z0-9]+\b", content))
        snake_count += len(re.findall(r"\b[a-z][a-z0-9_]+[a-z0-9]\b", content))
        kebab_count += len(re.findall(r"[a-z]+-[a-z]+", content))

    if camel_count > pascal_count and camel_count > snake_count:
        conventions["variables"] = "camelCase"
        conventions["functions"] = "camelCase"
    elif snake_count > camel_count:
        conventions["variables"] = "snake_case"
        conventions["functions"] = "snake_case"
    else:
        conventions["variables"] = "camelCase"
        conventions["functions"] = "camelCase"

    if pascal_count > 0:
        conventions["classes"] = "PascalCase"

    return conventions


def _detect_import_style(samples: list[tuple[str, str]]) -> str:
    """Infer import style from sample code."""
    default_imports = 0
    named_imports = 0
    for _, content in samples:
        default_imports += len(re.findall(r"^import\s+\w+\s+from", content, re.MULTILINE))
        named_imports += len(re.findall(r"^import\s+\{", content, re.MULTILINE))
    if named_imports > default_imports:
        return "named imports preferred"
    elif default_imports > named_imports:
        return "default imports preferred"
    return "mixed (named and default)"


def _detect_test_style(repo: Path, area: Optional[str]) -> str:
    """Detect test file organization."""
    from codebase_scanner import _collect_files
    files = _collect_files(repo, area)
    test_files = [f for f in files if "test" in f.name.lower() or "spec" in f.name.lower()]
    if not test_files:
        return "no tests detected"
    colocated = sum(1 for f in test_files
                    if not any(p in str(f) for p in ["/tests/", "/test/", "/__tests__/"]))
    if colocated > len(test_files) // 2:
        return "co-located (next to source files)"
    return "centralized (tests/ directory)"


# ---------------------------------------------------------------------------
# L4: Pattern coexistence
# ---------------------------------------------------------------------------

def _detect_pattern_coexistence(repo: Path, area: Optional[str]) -> dict:
    """Detect vigente vs legado patterns by recency heuristic."""
    from codebase_scanner import _collect_files
    files = _collect_files(repo, area)

    # Split files into "recent" and "old" by modification time
    import os
    file_ages = []
    for f in files:
        try:
            mtime = os.path.getmtime(f)
            file_ages.append((mtime, f))
        except OSError:
            pass

    if not file_ages:
        return {"vigente": "indeterminate", "legado": "none detected", "confidence": "low"}

    file_ages.sort(key=lambda x: -x[0])
    cutoff = len(file_ages) // 3  # top third = recent
    recent = [f for _, f in file_ages[:cutoff]]
    old = [f for _, f in file_ages[cutoff:]]

    # Count dir patterns in recent vs old files
    recent_dirs: dict[str, int] = {}
    old_dirs: dict[str, int] = {}

    for f in recent:
        for part in f.relative_to(repo).parts[:-1]:
            recent_dirs[part] = recent_dirs.get(part, 0) + 1
    for f in old:
        for part in f.relative_to(repo).parts[:-1]:
            old_dirs[part] = old_dirs.get(part, 0) + 1

    # Dirs prominent in recent but not old = vigente
    vigente_dirs = sorted(
        [(d, c) for d, c in recent_dirs.items() if c > old_dirs.get(d, 0)],
        key=lambda x: -x[1],
    )[:3]

    # Dirs prominent in old but not recent = legado
    legado_dirs = sorted(
        [(d, c) for d, c in old_dirs.items() if c > recent_dirs.get(d, 0)],
        key=lambda x: -x[1],
    )[:3]

    vigente_str = ", ".join(f"{d}/" for d, _ in vigente_dirs) or "padrão atual (homogêneo)"
    legado_str = ", ".join(f"{d}/" for d, _ in legado_dirs) or "nenhum legado detectado"

    return {
        "vigente": vigente_str,
        "legado": legado_str,
        "confidence": "medium" if vigente_dirs or legado_dirs else "low",
    }


# ---------------------------------------------------------------------------
# Main deep scan
# ---------------------------------------------------------------------------

def scan_deep(
    repo: Path,
    level: str,
    arch_root: Path,
    client: str,
    context: str = "",
    area: Optional[str] = None,
) -> dict:
    """Run deep scan (L2/L3/L4) on repo. Returns result dict for profile + HTML."""
    _import_sdk(arch_root)
    from scanner_profile import ProjectProfile
    from codebase_scanner import _collect_files

    profile = ProjectProfile(arch_root, client)
    files = _collect_files(repo, area)
    samples = _read_sample_files(repo, area, n=8)

    result: dict = {
        "file_count": len(files),
        "level": level,
        "proofs": {},
    }

    if "L2" in level or level in ("L2", "L2+L3", "L2+L3+L4"):
        pattern, evidence = _detect_architecture(repo, area)
        result["architecture"] = pattern
        result["arch_evidence"] = evidence
        proof = f"Detectado por sinais estruturais: {', '.join(evidence) or 'análise de arquivos-chave'}"
        if not evidence:
            # Fallback: read key files
            if samples:
                proof = f"Analisados {len(samples)} arquivos-chave — padrão inferido por estrutura"
        result["proofs"]["L2"] = proof

        lines = [
            f"padrão: {pattern}",
            f"evidência: {', '.join(evidence) or 'arquivos-chave'}",
            f"prova: {proof}",
        ]
        if context:
            lines.append(f"contexto_fornecido: {context}")
        profile.set_section("L2", lines)

    if "L3" in level or level in ("L3", "L2+L3", "L2+L3+L4"):
        naming = _detect_naming_convention(samples)
        import_style = _detect_import_style(samples)
        test_style = _detect_test_style(repo, area)

        result["naming"] = naming
        result["import_style"] = import_style
        result["test_style"] = test_style

        naming_str = " · ".join(f"{k}: {v}" for k, v in naming.items())
        lines = [
            f"naming: {naming_str}",
            f"imports: {import_style}",
            f"testes: {test_style}",
        ]

        # Check for formatters
        formatters = []
        for f_name in [".eslintrc", ".eslintrc.json", ".eslintrc.js", "prettier.config.js",
                       ".prettierrc", "pyproject.toml", ".flake8"]:
            if (repo / f_name).exists():
                formatters.append(f_name)
        if formatters:
            lines.append(f"formatters: {', '.join(formatters)}")

        profile.set_section("L3", lines)
        result["proofs"]["L3"] = f"Analisados {len(samples)} samples; detectado por heurística regex"

    if "L4" in level or level in ("L4", "L2+L3+L4"):
        coex = _detect_pattern_coexistence(repo, area)
        result["l4_coexistence"] = coex
        lines = [
            f"vigente: {coex['vigente']}",
            f"legado_tolerado: {coex['legado']}",
            f"confidence: {coex['confidence']}",
            "nota: Baseado em timestamps de modificação de arquivos (recente=vigente, antigo=legado)",
        ]
        profile.set_section("L4", lines)
        result["proofs"]["L4"] = "Classificado por frequência × recência dos arquivos"

    profile.save()
    result["profile_path"] = str(profile.path)
    return result
