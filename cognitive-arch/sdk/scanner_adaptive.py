# sdk/scanner_adaptive.py
# PURPOSE: Adaptive mode for large repos (pre-scan assessment, cost estimate, Piloto confirmation),
#          and profile management utilities (--refresh-level, stale detection).
# INPUTS:  target_repo, level, area; project-profile sections with scanned_at timestamps
# OUTPUTS: Prompts user before large scans; blocks until confirmed; never starts silently
# DEPS:    stdlib only; sdk/scanner_profile
# USAGE:   from scanner_adaptive import adaptive_preflight, ProfileManager
# SEE:     design/scanner.md §4

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

_COST_PER_FILE: dict[str, int] = {
    "L0": 600,   # deep domain read
    "L1": 150,   # shallow structure
    "L2": 900,   # architecture analysis
    "L3": 700,   # code aesthetics
    "L4": 400,   # pattern comparison
}
_CHARS_PER_TOKEN = 4
_USD_PER_TOKEN = 0.000003


def estimate_cost(file_count: int, level: str) -> tuple[int, float]:
    """Return (approx_tokens, usd_estimate) for a scan."""
    chars = file_count * _COST_PER_FILE.get(level, 500)
    tokens = chars // _CHARS_PER_TOKEN
    usd = round(tokens * _USD_PER_TOKEN, 4)
    return tokens, usd


# ---------------------------------------------------------------------------
# Adaptive preflight
# ---------------------------------------------------------------------------

LARGE_REPO_THRESHOLD = 200  # files


def adaptive_preflight(
    repo: Path,
    level: str,
    area: Optional[str] = None,
    threshold: int = LARGE_REPO_THRESHOLD,
    interactive: bool = True,
) -> bool:
    """Run pre-scan assessment for large repos. Returns True to proceed, False to cancel.

    For repos below threshold, always returns True (no prompt needed).
    """
    from codebase_scanner import _count_files
    total, relevant = _count_files(repo)

    if relevant < threshold:
        return True  # small repo — no prompt needed

    # Large repo: show cost estimates and ask
    print(f"\n[scanner] Inventário do projeto:")
    print(f"  Total de arquivos: {total}")
    print(f"  Após .gitignore: {relevant} arquivos relevantes")
    print()

    tok_full, usd_full = estimate_cost(relevant, level)
    tok_struct, usd_struct = estimate_cost(min(relevant, 100), "L1")
    tok_area, usd_area = estimate_cost(min(relevant // 4, 50), level)

    print(f"  Estimativas de custo para nível {level}:")
    print(f"  [A] Scan completo ({level}+lógica):  ~{tok_full:,} tokens · est. ${usd_full}")
    print(f"  [B] Scan estrutural (L0+L1 sem domínio): ~{tok_struct:,} tokens · est. ${usd_struct}")
    print(f"  [C] Scan por área (indique a pasta):  ~{tok_area:,} tokens · est. ${usd_area}")
    print(f"  [D] Cancelar")
    print()

    if not interactive:
        # Non-interactive: auto-proceed with full scan
        return True

    try:
        choice = input("  Sua escolha [A/B/C/D]: ").strip().upper()
    except (EOFError, KeyboardInterrupt):
        return False

    if choice == "D":
        return False
    return True  # A, B, C — proceed (caller adjusts scope via --area)


# ---------------------------------------------------------------------------
# Ticket inference
# ---------------------------------------------------------------------------

_AREA_KEYWORDS: dict[str, list[str]] = {
    "auth": ["auth", "login", "jwt", "token", "senha", "password", "session", "oauth", "refresh"],
    "user": ["user", "usuário", "usuario", "perfil", "profile", "conta", "account", "register"],
    "payment": ["payment", "pagamento", "stripe", "checkout", "invoice", "billing"],
    "api": ["api", "endpoint", "route", "controller", "handler", "rest", "graphql"],
    "database": ["db", "database", "migration", "schema", "model", "repository", "orm"],
    "frontend": ["component", "ui", "page", "view", "layout", "style", "css"],
    "email": ["email", "mail", "smtp", "notification", "notify"],
    "test": ["test", "teste", "spec", "mock", "fixture"],
}


def infer_area_from_ticket(ticket_text: str, repo: Path) -> Optional[str]:
    """Infer the most likely source area from ticket text. Returns path or None."""
    text_lower = ticket_text.lower()

    # Score each area
    scores: dict[str, int] = {}
    for area, keywords in _AREA_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score:
            scores[area] = score

    if not scores:
        return None

    best_area = max(scores, key=lambda k: scores[k])

    # Try to find matching directory
    candidates = []
    for p in repo.rglob("*"):
        if p.is_dir() and best_area.lower() in p.name.lower():
            rel = str(p.relative_to(repo))
            candidates.append(rel)

    if candidates:
        # Prefer shallower paths
        candidates.sort(key=lambda x: x.count("/"))
        return candidates[0]

    # Generic fallback
    dir_map = {
        "auth": "src/auth",
        "user": "src/user",
        "payment": "src/payment",
        "api": "src/api",
        "database": "src",
        "frontend": "src/components",
        "email": "src/email",
        "test": "tests",
    }
    return dir_map.get(best_area)


def confirm_area(area: Optional[str], ticket_text: str, interactive: bool = True) -> Optional[str]:
    """Show inferred area to Piloto and confirm."""
    if not area:
        print(f"[scanner] Não foi possível inferir área do ticket.")
        return None

    print(f"\n[scanner] Área inferida do ticket: {area}")
    print(f"  Ticket: {ticket_text[:80]}...")

    if not interactive:
        return area

    try:
        choice = input("  [y] Confirmar  [n] Cancelar  [c] Customizar área: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return area  # default to proceeding

    if choice == "n":
        return None
    if choice.startswith("c"):
        try:
            custom = input("  Área (path relativo): ").strip()
            return custom or area
        except (EOFError, KeyboardInterrupt):
            return area
    return area  # y or default


# ---------------------------------------------------------------------------
# Profile management
# ---------------------------------------------------------------------------

class ProfileManager:
    """Manage project-profile sections: refresh, staleness detection, multi-client."""

    def __init__(self, arch_root: Path) -> None:
        self._root = arch_root

    def is_stale(self, client: str, level: str, max_days: int = 30) -> bool:
        """Return True if a profile section is missing or older than max_days."""
        from scanner_profile import ProjectProfile
        from datetime import datetime, timezone
        p = ProjectProfile(self._root, client)
        if not p.has_section(level):
            return True
        ts_str = p.get_scanned_at(level)
        if not ts_str:
            return True
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - ts).days
            return age > max_days
        except ValueError:
            return True

    def list_stale(self, client: str) -> list[str]:
        """Return list of levels that are stale for client."""
        return [lvl for lvl in ("L0", "L1", "L2", "L3", "L4") if self.is_stale(client, lvl)]

    def refresh_level(self, client: str, level: str, target_repo: Path, **kwargs) -> dict:
        """Force re-scan of a specific level (--refresh-level)."""
        import importlib
        import sys as _sys
        sdk_str = str(self._root / "sdk")
        if sdk_str not in _sys.path:
            _sys.path.insert(0, sdk_str)
        from codebase_scanner import run_scan
        return run_scan(target_repo, level, self._root, client, **kwargs)
