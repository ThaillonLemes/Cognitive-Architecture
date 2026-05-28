# sdk/retro_signals.py
# PURPOSE: Extract RetroSignal records from block retrospective markdown files.
# INPUTS:  blocks/block-NNN-*.md (retrospective files), manifests/block-NNN-*.md (for tier/kind)
# OUTPUTS: list[RetroSignal]; parse failures logged to sdk/_retro_signal_failures.log
# DEPS:    stdlib only (re, pathlib, logging), sdk/retro_signal_schema
# SEE:     sdk/retro_signal_schema.py, sdk/pattern_analyzer.py

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from retro_signal_schema import RetroSignal

_FAIL_LOG = Path(__file__).parent / "_retro_signal_failures.log"
_AXIOM_PATTERN = re.compile(r"\b([PQCSM][1-9][0-9]?)\b")
_GATES_PATTERN = re.compile(r"gates_passed:\s*(\d+)/(\d+)", re.IGNORECASE)
_HOURS_PATTERN = re.compile(r"^actual_duration_hours:\s*([0-9.]+)", re.MULTILINE)
_DURATION_SOURCE_PATTERN = re.compile(r"^duration_source:\s*(\S+)", re.MULTILINE)
_COMPLETED_PATTERN = re.compile(r"^completed_at:\s*(\S+)", re.MULTILINE)
_ID_PATTERN = re.compile(r"^id:\s*(block-\d+)", re.MULTILINE)
_STATUS_PATTERN = re.compile(r"^status:\s*(\w+)", re.MULTILINE)


def _extract_frontmatter(text: str) -> str:
    """Return content between first and second '---' markers."""
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""


def _load_manifest_meta(block_id: str, arch_root: Path) -> dict[str, str]:
    """Return {tier, kind, phase, estimated_duration_days} from the block's manifest."""
    manifests_dir = arch_root / "manifests"
    candidates = list(manifests_dir.glob(f"{block_id}-*.md"))
    if not candidates:
        return {}
    text = candidates[0].read_text(encoding="utf-8", errors="ignore")
    fm = _extract_frontmatter(text)
    meta: dict[str, str] = {}
    for key in ("tier", "kind", "phase", "estimated_duration_days"):
        m = re.search(rf"^{key}:\s*(\S+)", fm, re.MULTILINE)
        if m:
            meta[key] = m.group(1)
    return meta


def extract_signal(retro_path: Path, arch_root: Path) -> Optional[RetroSignal]:
    """
    Parse a single retrospective file and return a RetroSignal.
    Returns None on unrecoverable parse error (also logs to _retro_signal_failures.log).
    """
    try:
        text = retro_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        _log_failure(str(retro_path), f"read error: {e}")
        return None

    fm = _extract_frontmatter(text)
    if not fm:
        _log_failure(str(retro_path), "no frontmatter found")
        return None

    # block_id
    id_m = _ID_PATTERN.search(fm)
    if not id_m:
        _log_failure(str(retro_path), "no 'id:' field in frontmatter")
        return None
    block_id = id_m.group(1)

    # Only extract 'done' blocks
    status_m = _STATUS_PATTERN.search(fm)
    if status_m and status_m.group(1) not in ("done", "forced"):
        return None  # skip non-done blocks silently

    # Manifest metadata
    meta = _load_manifest_meta(block_id, arch_root)
    tier = meta.get("tier", "unknown")
    kind = meta.get("kind", "unknown")
    phase = meta.get("phase", "unknown")
    try:
        est_days: Optional[float] = float(meta["estimated_duration_days"])
    except (KeyError, ValueError):
        est_days = None

    # Duration
    h_m = _HOURS_PATTERN.search(fm)
    try:
        actual_h: Optional[float] = float(h_m.group(1)) if h_m else None
    except ValueError:
        actual_h = None

    ds_m = _DURATION_SOURCE_PATTERN.search(fm)
    duration_source = ds_m.group(1) if ds_m else "unknown"

    # Gates
    gates_m = _GATES_PATTERN.search(fm)
    if gates_m:
        passed = int(gates_m.group(1))
        total = int(gates_m.group(2))
        failures = total - passed
    else:
        passed = total = failures = 0

    # completed_at
    ca_m = _COMPLETED_PATTERN.search(fm)
    closed_at = ca_m.group(1) if ca_m else None

    # Axioms violated — scan body for explicit mentions
    body = text.split("---", 2)[-1] if "---" in text else text
    axioms_found = _AXIOM_PATTERN.findall(body.upper())
    # Heuristic: axioms mentioned near "violated", "skipped", "override", "ignored"
    violation_ctx = re.findall(
        r"(?:violat|skip|override|ignor|broken|break).{0,80}([PQCSM][1-9][0-9]?)|"
        r"([PQCSM][1-9][0-9]?).{0,80}(?:violat|skip|override|ignor|broken|break)",
        body, re.IGNORECASE
    )
    axioms_violated = list({m for pair in violation_ctx for m in pair if m})

    # Scope expansion: look for "Added unexpectedly" or "Modified unexpectedly" in §8
    scope_expansion = bool(re.search(r"added unexpectedly|modified unexpectedly", body, re.IGNORECASE))
    # Also check if "As manifest." is NOT present in §8 (proxy for scope expansion)
    if not scope_expansion and "## 8. Files actually touched" in body:
        section8 = body.split("## 8. Files actually touched", 1)[1]
        scope_expansion = "as manifest" not in section8[:300].lower()

    # Forced pass
    forced_pass = bool(re.search(r"force.pass|forced_pass|force-pass", body, re.IGNORECASE))

    warnings: list[str] = []
    if actual_h is None:
        warnings.append("actual_duration_hours missing")
    if tier == "unknown":
        warnings.append("tier not found in manifest")

    return RetroSignal(
        block_id=block_id,
        phase=phase,
        tier=tier,
        kind=kind,
        duration_actual_h=actual_h,
        duration_estimated_days=est_days,
        duration_source=duration_source,
        axioms_violated=axioms_violated,
        scope_expansion=scope_expansion,
        gate_failures=failures,
        gates_total=total,
        gates_passed_count=passed,
        forced_pass=forced_pass,
        closed_at=closed_at,
        parse_warnings=warnings,
    )


def extract_all(arch_root: Path) -> list[RetroSignal]:
    """
    Extract signals from all block retrospectives in blocks/.
    Logs failures to sdk/_retro_signal_failures.log; never raises.
    """
    blocks_dir = arch_root / "blocks"
    signals: list[RetroSignal] = []

    for retro_file in sorted(blocks_dir.glob("block-*-*.md")):
        if "phase-" in retro_file.name:
            continue  # skip phase retrospectives
        sig = extract_signal(retro_file, arch_root)
        if sig is not None:
            signals.append(sig)

    return signals


def _log_failure(path: str, reason: str) -> None:
    with open(_FAIL_LOG, "a", encoding="utf-8") as f:
        f.write(f"{path}: {reason}\n")


if __name__ == "__main__":
    import sys
    arch_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent
    signals = extract_all(arch_root)
    print(f"Extracted {len(signals)} signals.")
    for s in signals[:5]:
        print(f"  {s.block_id}: tier={s.tier} kind={s.kind} h={s.duration_actual_h} violations={s.axioms_violated}")
