# sdk/scanner_profile.py
# PURPOSE: Read, write, and update project-profile-<client>.md by section.
#          ProjectProfile class shared by scanner, consistency_checker, HTML generator.
# INPUTS:  governance/project-profile-<client>.md
# OUTPUTS: Updated profile sections with timestamps
# DEPS:    stdlib only
# USAGE:   from scanner_profile import ProjectProfile; p = ProjectProfile(arch_root, "visagio")
# SEE:     design/scanner.md §2

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Section constants
# ---------------------------------------------------------------------------

SECTION_NAMES = {
    "L0": "L0 — Macro arquitetural",
    "L1": "L1 — Estrutura",
    "L2": "L2 — Padrões de arquitetura",
    "L3": "L3 — Estética & convenções",
    "L4": "L4 — Coexistência de padrões",
}


class ProjectProfile:
    """Encapsulates read/write of governance/project-profile-<client>.md.

    Stored as flat markdown with ## headers per level.
    Each section has a _scanned_at: line as first content.
    Only metadata (patterns, names, counts) — never actual client code.
    """

    def __init__(self, arch_root: Path, client: str) -> None:
        self._root = arch_root
        self.client = client
        self._path = arch_root / "governance" / f"project-profile-{client}.md"
        self._content = self._path.read_text(encoding="utf-8", errors="replace") if self._path.exists() else ""

    @property
    def path(self) -> Path:
        return self._path

    @property
    def exists(self) -> bool:
        return self._path.exists()

    # ------------------------------------------------------------------
    # Section helpers
    # ------------------------------------------------------------------

    def _section_header(self, level: str) -> str:
        return f"## {SECTION_NAMES.get(level, level)}"

    def get_section(self, level: str) -> str:
        """Return content of a level section, or '' if not present."""
        header = self._section_header(level)
        if header not in self._content:
            return ""
        parts = self._content.split(header, 1)
        after = parts[1]
        # Content ends at next ## header or EOF
        next_h = re.search(r"^## ", after, re.MULTILINE)
        return after[: next_h.start()].strip() if next_h else after.strip()

    def get_scanned_at(self, level: str) -> str:
        """Return the _scanned_at timestamp for a section, or ''."""
        section = self.get_section(level)
        m = re.search(r"_scanned_at:\s*(\S+)_", section)
        return m.group(1) if m else ""

    def set_section(self, level: str, content_lines: list[str]) -> None:
        """Set or replace a level section with new content. Adds scanned_at timestamp."""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        header = self._section_header(level)
        section_body = f"_{level}_scanned_at: {ts}_\n\n" + "\n".join(content_lines)
        new_section = f"{header}\n{section_body}\n"

        if header in self._content:
            # Replace existing section
            pattern = rf"({re.escape(header)}\n).*?(?=^## |\Z)"
            self._content = re.sub(pattern, new_section, self._content,
                                   count=1, flags=re.MULTILINE | re.DOTALL)
        else:
            self._content += f"\n{new_section}"

    def has_section(self, level: str) -> bool:
        return self._section_header(level) in self._content

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Write current content to disk."""
        self._path.parent.mkdir(exist_ok=True)
        header_line = f"# Project Profile — {self.client}\n"
        if not self._content.startswith("# Project Profile"):
            self._content = header_line + self._content
        self._path.write_text(self._content, encoding="utf-8")

    def reload(self) -> None:
        """Reload from disk."""
        self._content = self._path.read_text(encoding="utf-8", errors="replace") if self._path.exists() else ""

    # ------------------------------------------------------------------
    # Multi-client
    # ------------------------------------------------------------------

    @classmethod
    def list_clients(cls, arch_root: Path) -> list[str]:
        """Return all client names that have profiles in governance/."""
        gov = arch_root / "governance"
        if not gov.exists():
            return []
        clients = []
        for p in gov.glob("project-profile-*.md"):
            m = re.match(r"project-profile-(.+)\.md", p.name)
            if m:
                clients.append(m.group(1))
        return sorted(clients)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_has_level(self, level: str) -> tuple[bool, str]:
        """Return (ok, message) for required level presence."""
        if not self.has_section(level):
            return False, f"Profile for '{self.client}' missing {level} section. Run: python sdk/codebase_scanner.py --level {level} --client {self.client}"
        return True, f"{level} section present (scanned_at: {self.get_scanned_at(level)})"
