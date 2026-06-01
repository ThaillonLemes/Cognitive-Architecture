# sdk/gates.py
# PURPOSE: Gate evaluation logic for block close, including CorporateGates (block-164).
# INPUTS:  arch_root, block_id, gate config from manifest
# OUTPUTS: GateResult (ok, message, requires_manual)
# DEPS:    stdlib only
# USAGE:   from gates import CorporateGates; CorporateGates(arch_root).check_all(block_id)
# SEE:     design/block-phase-redesign.md §1.8

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class GateResult:
    name: str
    ok: bool
    message: str
    requires_manual: bool = False


# ---------------------------------------------------------------------------
# Universal gates
# ---------------------------------------------------------------------------

def gate_files_updated(arch_root: Path, block_id: str) -> GateResult:
    """Verify STATE.md, NEXT.md, BLOCK_LOG.md reference the block."""
    missing = []
    for fname in ("STATE.md", "NEXT.md"):
        p = arch_root / fname
        if p.exists() and block_id not in p.read_text(encoding="utf-8", errors="replace"):
            missing.append(fname)
    log = arch_root / "blocks" / "BLOCK_LOG.md"
    if log.exists() and block_id not in log.read_text(encoding="utf-8", errors="replace"):
        missing.append("BLOCK_LOG.md")
    if missing:
        return GateResult("files-updated", False, f"Block ID not found in: {', '.join(missing)}")
    return GateResult("files-updated", True, "STATE.md, NEXT.md, BLOCK_LOG.md reference block")


def gate_scope_clean(arch_root: Path, block_id: str) -> GateResult:
    """Check fmod_real <= fmod_declared (loose heuristic — real validation is manual)."""
    manifests_dir = arch_root / "manifests"
    candidates = list(manifests_dir.glob(f"{block_id}-*.md"))
    if not candidates:
        return GateResult("scope-clean", True, "no manifest found — skipped")
    text = candidates[0].read_text(encoding="utf-8", errors="replace")
    # Count declared modify + create
    declared = len(re.findall(r"^\s+-\s+\S", text, re.MULTILINE))
    return GateResult("scope-clean", True, f"manifest parsed ({declared} declared file entries)")


# ---------------------------------------------------------------------------
# CorporateGates — mode=corporate specific (block-164)
# ---------------------------------------------------------------------------

class CorporateGates:
    """Evaluate the three corporate gates for a block.

    Gates:
      functionality-check — manual checklist: acceptance_criteria met?
      consistency-check   — script: consistency_checker.py score >= threshold
      teach-ready         — manual checklist: Piloto can explain the work?
    """

    TEACH_CHECKLIST = [
        "Consigo explicar em 3 frases o que foi feito?",
        "Consigo responder por que escolhi essa abordagem?",
        "Consigo explicar o impacto para não-técnicos (gestor, cliente)?",
    ]

    FUNCTIONALITY_CHECKLIST = [
        "O que o ticket pediu está funcionando conforme o acceptance_criteria?",
    ]

    def __init__(self, arch_root: Path) -> None:
        self._root = arch_root

    def check_functionality(self, block_id: str) -> GateResult:
        """Returns a manual gate result with checklist items."""
        return GateResult(
            "functionality-check",
            True,  # manual — caller verifies
            "MANUAL: " + " | ".join(self.FUNCTIONALITY_CHECKLIST),
            requires_manual=True,
        )

    def check_consistency(self, block_id: str, client_id: str = "") -> GateResult:
        """Run consistency_checker.py if available; warn if not."""
        checker = self._root / "sdk" / "consistency_checker.py"
        if not checker.exists():
            return GateResult(
                "consistency-check",
                True,
                "WARN: consistency_checker.py not yet implemented — gate passes",
            )
        if not client_id:
            # Try to read client_id from manifest
            manifests_dir = self._root / "manifests"
            candidates = list(manifests_dir.glob(f"{block_id}-*.md"))
            if candidates:
                text = candidates[0].read_text(encoding="utf-8", errors="replace")
                m = re.search(r"^client_id:\s*(\S+)", text, re.MULTILINE)
                if m:
                    client_id = m.group(1)

        profile = self._root / "governance" / f"project-profile-{client_id}.md"
        if not profile.exists():
            return GateResult(
                "consistency-check",
                True,
                f"WARN: no project-profile for '{client_id}' — gate passes",
            )
        try:
            result = subprocess.run(
                [sys.executable, str(checker),
                 "--profile", str(profile),
                 "--arch-root", str(self._root)],
                capture_output=True, text=True, encoding="utf-8", timeout=30,
            )
            ok = result.returncode == 0
            msg = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "ok"
            return GateResult("consistency-check", ok, msg)
        except Exception as exc:
            return GateResult("consistency-check", False, str(exc))

    def check_teach_ready(self, block_id: str) -> GateResult:
        """Returns a manual gate result with the teach-ready checklist."""
        return GateResult(
            "teach-ready",
            True,  # manual — Piloto confirms
            "MANUAL: " + " | ".join(self.TEACH_CHECKLIST),
            requires_manual=True,
        )

    def check_all(self, block_id: str, client_id: str = "") -> list[GateResult]:
        return [
            self.check_functionality(block_id),
            self.check_consistency(block_id, client_id),
            self.check_teach_ready(block_id),
        ]


# ---------------------------------------------------------------------------
# Gate runner (universal)
# ---------------------------------------------------------------------------

def evaluate_gate(gate_cfg: dict, arch_root: Path, block_id: str) -> GateResult:
    """Evaluate a single gate config dict from a manifest."""
    name = gate_cfg.get("name", "unknown")
    gate_type = gate_cfg.get("type", "")
    cmd = gate_cfg.get("cmd", "")
    expect = gate_cfg.get("expect", "")

    if name == "files-updated":
        return gate_files_updated(arch_root, block_id)

    if name == "scope-clean":
        return gate_scope_clean(arch_root, block_id)

    if gate_type == "manual":
        checklist = gate_cfg.get("checklist", [])
        return GateResult(name, True, "MANUAL: " + " | ".join(checklist), requires_manual=True)

    if gate_type == "script" or cmd:
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=str(arch_root),
                capture_output=True, text=True, encoding="utf-8", timeout=60,
            )
            ok = expect in result.stdout if expect else result.returncode == 0
            msg = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "ok"
            return GateResult(name, ok, msg)
        except Exception as exc:
            return GateResult(name, False, str(exc))

    return GateResult(name, True, "gate type unknown — skipped")
