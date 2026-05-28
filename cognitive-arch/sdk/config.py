# PURPOSE: Governor v2 runtime configuration — parallelism limits, pause signal, model defaults
# INPUTS:  environment variables, governance/.pause file (interruption signal)
# OUTPUTS: GovConfig dataclass consumed by governor.py and dispatch.py
# DEPS:    stdlib only (os, pathlib, dataclasses)
# SEE:     design/governor-v2.md §11 open questions 5 and 6, sdk/dispatch.py, sdk/governor.py

"""
Governor v2 configuration.

Answers open questions 5 (max parallelism) and 6 (user interruption signal).

Open question 5 — max_parallel_agents:
  Default: 3. Configurable via GOV_MAX_PARALLEL env var.
  Governor will not dispatch more blocks in parallel than this limit.

Open question 6 — user interruption signal:
  Governor polls for governance/.pause before each group dispatch.
  If the file exists, Governor pauses and prints "PAUSED — delete governance/.pause to resume."
  User creates the file to request a pause; deletes it to resume.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_MAX_PARALLEL_AGENTS = 3
DEFAULT_MODEL               = "claude-opus-4-5"
DEFAULT_MAX_TOKENS          = 4096
DEFAULT_TIMEOUT_SEC         = 300       # 5 min per block
PAUSE_SIGNAL_FILENAME       = ".pause"  # relative to governance/
ANTHROPIC_API_KEY_ENV       = "ANTHROPIC_API_KEY"


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------

@dataclass
class GovConfig:
    max_parallel_agents: int = DEFAULT_MAX_PARALLEL_AGENTS
    model: str              = DEFAULT_MODEL
    max_tokens: int         = DEFAULT_MAX_TOKENS
    timeout_sec: float      = DEFAULT_TIMEOUT_SEC
    governor_mode: str      = "manual"   # manual | sdk | mock
    api_key: str            = ""
    arch_root: Path         = field(default_factory=lambda: Path("."))

    @property
    def pause_signal_path(self) -> Path:
        return self.arch_root / "governance" / PAUSE_SIGNAL_FILENAME

    def is_paused(self) -> bool:
        """Return True if the user has placed a pause signal file."""
        return self.pause_signal_path.exists()

    def check_pause(self) -> bool:
        """
        Check for pause signal. If paused, print message and return True.
        Caller should loop/wait until is_paused() returns False.
        """
        if self.is_paused():
            print(f"GOVERNOR PAUSED — delete '{self.pause_signal_path}' to resume.")
            return True
        return False


def load_config(arch_root: Path, governor_mode: str = "manual") -> GovConfig:
    """
    Build a GovConfig from environment variables and defaults.

    Args:
        arch_root:      Path to cognitive-arch/ directory.
        governor_mode:  "manual", "sdk", or "mock".
    """
    return GovConfig(
        max_parallel_agents=int(os.environ.get("GOV_MAX_PARALLEL", DEFAULT_MAX_PARALLEL_AGENTS)),
        model=os.environ.get("GOV_MODEL", DEFAULT_MODEL),
        max_tokens=int(os.environ.get("GOV_MAX_TOKENS", DEFAULT_MAX_TOKENS)),
        timeout_sec=float(os.environ.get("GOV_TIMEOUT_SEC", DEFAULT_TIMEOUT_SEC)),
        governor_mode=governor_mode,
        api_key=os.environ.get(ANTHROPIC_API_KEY_ENV, ""),
        arch_root=arch_root,
    )


# ---------------------------------------------------------------------------
# CLI (informational)
# ---------------------------------------------------------------------------

def main() -> None:
    import sys
    arch_root = Path(__file__).resolve().parent.parent
    cfg = load_config(arch_root)
    print("Governor v2 — current config:")
    print(f"  max_parallel_agents : {cfg.max_parallel_agents}  (GOV_MAX_PARALLEL env)")
    print(f"  model               : {cfg.model}  (GOV_MODEL env)")
    print(f"  max_tokens          : {cfg.max_tokens}  (GOV_MAX_TOKENS env)")
    print(f"  timeout_sec         : {cfg.timeout_sec}  (GOV_TIMEOUT_SEC env)")
    print(f"  governor_mode       : {cfg.governor_mode}")
    print(f"  api_key             : {'set' if cfg.api_key else 'NOT SET (set ANTHROPIC_API_KEY)'}")
    print(f"  pause_signal        : {cfg.pause_signal_path}  (exists={cfg.is_paused()})")


if __name__ == "__main__":
    main()
