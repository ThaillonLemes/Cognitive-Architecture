# sdk/block_start.py
# PURPOSE: Automate block-start validation and board update (steps 1-4 of block-start protocol).
#          Saves ~1500 tokens per block start.
# INPUTS:  block_id, manifests/, blocks/BLOCK_LOG.md, NEXT.md
# OUTPUTS: Validation report; updated board.md and STATE.md if checks pass
# DEPS:    stdlib only; sdk/state_manager, sdk/board_manager
# USAGE:   python sdk/block_start.py --block-id block-112 --arch-root .
# SEE:     commands/block-start.md, _syntax.md

from __future__ import annotations

import argparse
import io
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

def _fix_utf8():
    """Apply UTF-8 stdout fix on Windows — safe to call multiple times."""
    import io as _io
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'buffer') and not (
            isinstance(sys.stdout, _io.TextIOWrapper) and sys.stdout.encoding.lower() == 'utf-8'
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_fix_utf8()


def _import_sdk(arch_root: Path) -> None:
    sdk = str(arch_root / "sdk")
    if sdk not in sys.path:
        sys.path.insert(0, sdk)


# ---------------------------------------------------------------------------
# Manifest reader
# ---------------------------------------------------------------------------

def _find_manifest(arch_root: Path, block_id: str) -> Path | None:
    candidates = list((arch_root / "manifests").glob(f"{block_id}-*.md"))
    return candidates[0] if candidates else None


def _read_manifest(path: Path) -> dict[str, str]:
    """Extract key fields from manifest frontmatter and body.

    Block-164: reads size, importance, wip_stage in addition to v1 tier.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    data: dict[str, str] = {}
    # Frontmatter
    parts = text.split("---", 2)
    fm = parts[1] if len(parts) >= 3 else ""
    for key in ("id", "phase", "tier", "size", "importance", "status",
                "dependencies", "kind", "wip_stage"):
        m = re.search(rf"^{key}:\s*(.+)", fm, re.MULTILINE)
        if m:
            data[key] = m.group(1).strip().strip('"[]')
    return data


# ---------------------------------------------------------------------------
# BLOCK_LOG reader
# ---------------------------------------------------------------------------

def _load_block_log(arch_root: Path) -> set[str]:
    """Return set of block IDs that are done (in BLOCK_LOG.md)."""
    log = arch_root / "blocks" / "BLOCK_LOG.md"
    if not log.exists():
        return set()
    done: set[str] = set()
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^(block-\d+)\s+(done|integrated)", line)
        if m:
            done.add(m.group(1))
    return done


# ---------------------------------------------------------------------------
# Main start function
# ---------------------------------------------------------------------------

def start_block(
    arch_root: Path,
    block_id: str,
    agent: str = "implementer",
) -> dict[str, str | bool]:
    """
    Validate block start pre-conditions and update board + state.
    Returns {manifest, deps_ok, board, state} summary.
    """
    _import_sdk(arch_root)
    from state_manager import update_state, update_next
    from board_manager import update_agent

    results: dict[str, str | bool] = {}
    block_num = block_id.replace("block-", "")

    print(f"\n[block_start] Starting {block_id}")

    # --- Step 1: Manifest check ---
    manifest_path = _find_manifest(arch_root, block_id)
    if not manifest_path:
        print(f"  ERROR: No manifest found for {block_id} in manifests/")
        print(f"  Action required: generate manifest first (protocols/manifest-*.md)")
        results["manifest"] = "missing"
        return results

    manifest = _read_manifest(manifest_path)
    # v2 manifests use size+importance; v1 use tier
    size_label = manifest.get("size") or manifest.get("tier", "?")
    importance_label = manifest.get("importance", "")
    tier_display = f"size={size_label}" + (f" importance={importance_label}" if importance_label else "")
    print(f"  Manifest: {manifest_path.name} | phase={manifest.get('phase','?')} {tier_display}")
    results["manifest"] = "ok"

    # --- Step 2: Dependencies check ---
    deps_raw = manifest.get("dependencies", "")
    deps = [d.strip() for d in re.split(r"[,\s]+", deps_raw) if d.strip() and d.strip() != "-"]
    done_blocks = _load_block_log(arch_root)

    unmet = [d for d in deps if d not in done_blocks]
    if unmet:
        print(f"  HALT: Dependencies not done: {unmet}")
        print(f"  Cannot start {block_id} until deps are in BLOCK_LOG.md")
        results["deps_ok"] = False
        results["unmet_deps"] = ", ".join(unmet)
        return results

    if deps:
        print(f"  Deps OK: {deps}")
    else:
        print(f"  No dependencies")
    results["deps_ok"] = True

    # --- Step 3: Update STATE.md ---
    phase = manifest.get("phase", "unknown")
    state_updates: dict[str, str | bool] = {
        "status": "active",
        "phase": phase,
        "next": block_id,
        "wip_stage": manifest.get("wip_stage") or "implementing",
    }
    update_state(arch_root, state_updates)

    # block-173: stamp started_at in manifest via velocity_tracker
    try:
        vt_path = arch_root / "sdk" / "velocity_tracker.py"
        if vt_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("velocity_tracker", vt_path)
            vt = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(vt)
            ts = vt.stamp_started(arch_root, block_id)
            if ts:
                print(f"  velocity_tracker: started_at={ts}")
    except Exception:
        pass  # never block start on tracker failure
    print(f"  STATE.md: status=active phase={phase} next={block_id}")
    results["state"] = "ok"

    # --- Step 4: Update NEXT.md ---
    update_next(arch_root, {
        "next_action": block_id,
        "phase": phase,
        "manifest": str(manifest_path.relative_to(arch_root)).replace("\\", "/"),
        "status": "active",
    })
    print(f"  NEXT.md: next_action={block_id}")
    results["next"] = "ok"

    # --- Step 4b: Update board.md ---
    ok = update_agent(arch_root, agent, {
        "b": block_num,
        "status": "wip",
        "lock": "in-progress",
    })
    print(f"  board.md: agent:{agent} status:wip b:{block_num} — {'ok' if ok else 'agent not found'}")
    results["board"] = "ok" if ok else "agent_not_found"

    print(f"\n  [block_start] Pre-flight complete. Begin implementation.")
    print(f"  Manifest: {manifest_path.name}")
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate and initialize block start")
    parser.add_argument("--block-id", required=True, help="e.g. block-112")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--agent", default="implementer", help="Agent name in board.md")
    args = parser.parse_args()

    root = Path(args.arch_root).resolve()
    start_block(root, args.block_id, args.agent)
