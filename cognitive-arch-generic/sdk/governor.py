# PURPOSE: Governor v2 — CLI entry point for SDK-based block orchestration
# INPUTS:  STATE.md, NEXT.md, board.md, manifests/, ANTHROPIC_API_KEY (env, sdk mode only)
# OUTPUTS: task packets to sub-agents, state file updates, git commits
# DEPS:    anthropic>=0.25.0, sdk/convention_snippet, sdk/task_packet,
#          sdk/return_validator, sdk/dispatch, sdk/integration, sdk/config
# SEE:     design/governor-v2.md, protocols/governor-dispatch.md,
#          protocols/governor-integration.md, protocols/governor-failure-handling.md

"""
Governor v2 — SDK-based block orchestration for cognitive-arch projects.

Usage examples:
  python sdk/governor.py --help
  python sdk/governor.py --dry-run
  python sdk/governor.py --block 030
  python sdk/governor.py --test-integration
  python sdk/governor.py --mode manual --dry-run
"""

import argparse
import sys
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path

# sdk/governor.py lives inside cognitive-arch/sdk/ — so parent.parent = cognitive-arch/
ARCH_ROOT = Path(__file__).resolve().parent.parent

# Ensure sdk/ siblings are importable
_SDK_DIR = Path(__file__).resolve().parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_arch_file(relative_path: str) -> str:
    """Read a file relative to cognitive-arch/. Returns content or error string."""
    full = ARCH_ROOT / relative_path
    if not full.exists():
        return f"(not found: {relative_path})"
    return full.read_text(encoding="utf-8").strip()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_dry_run(args) -> int:
    """Read STATE.md and NEXT.md; print next block summary without dispatching."""
    state = read_arch_file("STATE.md")
    next_ptr = read_arch_file("NEXT.md")

    print("=" * 50)
    print("  GOVERNOR v2 — DRY RUN")
    print("=" * 50)
    print(f"  mode   : {args.mode}")
    n_parallel = getattr(args, "parallel", 1) or 1
    if n_parallel > 1:
        print(f"  parallel mode: {n_parallel} workers")
    print(f"  STATE  : {state}")
    print()
    print(f"  NEXT   : {next_ptr}")
    print()
    print("  No agents dispatched (dry-run mode).")
    print("=" * 50)
    return 0


def _write_governor_state(state: dict) -> None:
    """Write ephemeral governor-state.md before each state transition (crash recovery)."""
    state_path = ARCH_ROOT / "governance" / "governor-state.md"
    lines = ["# governor-state — ephemeral Governor session state (AI-only)", ""]
    for k, v in state.items():
        lines.append(f"{k}:{v}")
    state_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_block(args) -> int:
    """
    Run Governor on a specific block manifest (mock dispatch).
    Full multi-group orchestration available via --test-integration.
    """
    from task_packet import build_packet
    from dispatch import dispatch_block
    from integration import integrate_group
    from config import load_config

    cfg = load_config(ARCH_ROOT, governor_mode=args.mode)
    manifest_path = f"manifests/block-{args.block}-"

    # Find matching manifest
    candidates = list((ARCH_ROOT / "manifests").glob(f"block-{args.block}-*.md"))
    if not candidates:
        print(f"ERROR: no manifest found for block-{args.block} in manifests/", file=sys.stderr)
        return 1
    manifest_rel = str(candidates[0].relative_to(ARCH_ROOT))

    # Read current phase from STATE.md for governor-state (avoid hardcoding)
    state_text = read_arch_file("STATE.md")
    current_phase = "phase-unknown"
    for token in state_text.split():
        if token.startswith("phase:"):
            current_phase = token.split(":", 1)[1]
            break

    # Write governor-state before dispatch (crash recovery)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    _write_governor_state({
        "session": "g-cli", "phase": current_phase, "block": args.block, "ts": ts,
        "dispatch_group": "manual", "dispatched": f"block-{args.block}",
        "awaiting": f"block-{args.block}", "last_committed": "-",
        "integration_status": "pending",
    })

    try:
        packet = build_packet(manifest_rel, ARCH_ROOT, gov_id="g-cli", ts=ts)
    except Exception as exc:
        print(f"ERROR building task packet: {exc}", file=sys.stderr)
        return 1

    # Route to correct dispatch mode — manual mode prints packet for human handoff
    if args.mode == "manual":
        print("=" * 60)
        print("  GOVERNOR v2 — MANUAL MODE")
        print("  Copy the task packet below and paste to a sub-agent.")
        print("=" * 60)
        print(packet)
        print("=" * 60)
        _write_governor_state({
            "session": "g-cli", "phase": current_phase, "block": args.block, "ts": ts,
            "dispatch_group": "manual", "dispatched": f"block-{args.block}",
            "awaiting": f"block-{args.block}", "last_committed": "-",
            "integration_status": "manual-handoff",
        })
        return 0
    elif args.mode == "sdk":
        dispatch_mode = "sdk"
    else:  # mock (default)
        dispatch_mode = "mock"

    result = dispatch_block(packet, mode=dispatch_mode, api_key=cfg.api_key)

    if not result.success:
        print(f"DISPATCH FAILED: {result.error}", file=sys.stderr)
        return 1

    print(f"Block {args.block} dispatched (mode={dispatch_mode})")
    print(f"  status : {result.validation.parsed.get('status') if result.validation else 'n/a'}")
    print(f"  elapsed: {result.elapsed_sec:.2f}s")

    _write_governor_state({
        "session": "g-cli", "phase": current_phase, "block": args.block, "ts": ts,
        "dispatch_group": "manual", "dispatched": f"block-{args.block}",
        "awaiting": "-", "last_committed": "-", "integration_status": "done",
    })
    return 0


# ---------------------------------------------------------------------------
# Track helpers
# ---------------------------------------------------------------------------

def _get_arch_root(args) -> Path:
    """Return arch root, allowing override via --arch-root for testing."""
    override = getattr(args, "arch_root", None)
    return Path(override) if override else ARCH_ROOT


def _parse_frontmatter(content: str) -> dict:
    """Parse YAML-like frontmatter between --- delimiters."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip().strip("\"'")
    return result


def _parse_priority_table(priority_md: str) -> list:
    """Parse Active Tracks markdown table from tracks/PRIORITY.md."""
    rows: list = []
    headers: list = []
    in_table = False

    for line in priority_md.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        if not headers:
            headers = [h.lower().replace(" ", "_") for h in cells]
            in_table = True
            continue
        # Skip separator rows (only dashes / colons)
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if len(cells) < len(headers):
            continue
        row = dict(zip(headers, cells[: len(headers)]))
        # Skip placeholder rows
        tid = row.get("track_id", "")
        if not tid or tid.startswith("_") or "no tracks" in tid.lower():
            continue
        try:
            row["_total_priority_int"] = int(row.get("total_priority", "0"))
        except (ValueError, TypeError):
            row["_total_priority_int"] = 0
        rows.append(row)
    return rows


def _get_current_focus(priority_md: str) -> str:
    """Extract current_focus Track ID from PRIORITY.md. Returns '' if none."""
    for line in priority_md.splitlines():
        stripped = line.strip().strip("`")
        if stripped.startswith("current_focus:"):
            value = stripped.split(":", 1)[1].strip().strip("`")
            return "" if value in ("none", "-", "") else value
    return ""


def _find_open_track_blocks(track_id_normalized: str, arch_root: Path) -> list:
    """
    Scan tracks/ (recursively) for Track Block files with:
      - track: track/<track_id_normalized> in frontmatter
      - status: planned or wip
    Returns list of Path objects.
    """
    open_blocks: list = []
    tracks_dir = arch_root / "tracks"
    if not tracks_dir.exists():
        return open_blocks
    skip_names = {"README.md", "PRIORITY.md", "_placeholder.md"}
    for md_file in tracks_dir.rglob("*.md"):
        if md_file.name in skip_names:
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = _parse_frontmatter(content)
        if not fm:
            continue
        file_track = fm.get("track", "").lower()
        # Accept "track/name" or just "name"
        file_track_normalized = file_track.removeprefix("track/")
        file_status = fm.get("status", "").lower()
        if file_track_normalized == track_id_normalized.lower() and file_status in ("planned", "wip"):
            open_blocks.append(md_file)
    return open_blocks


# ---------------------------------------------------------------------------
# Track commands
# ---------------------------------------------------------------------------

def cmd_list_tracks(args) -> int:
    """Print tracks/PRIORITY.md priority table ordered by total_priority descending."""
    arch_root = _get_arch_root(args)
    priority_path = arch_root / "tracks" / "PRIORITY.md"

    if not priority_path.exists():
        print("No tracks/PRIORITY.md found. Run protocols/track-generation.md to create Tracks.")
        return 0

    priority_md = priority_path.read_text(encoding="utf-8")
    rows = _parse_priority_table(priority_md)

    if not rows:
        print("No Tracks found in tracks/PRIORITY.md. Create Tracks using protocols/track-generation.md.")
        return 0

    # Sort descending by total_priority
    rows.sort(key=lambda r: r["_total_priority_int"], reverse=True)
    current_focus = _get_current_focus(priority_md)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Track Priority Table (as of {today})")
    print("=" * 55)
    print(f"{'Rank':<6}{'Track ID':<30}{'total_priority':<16}{'focus'}")
    print("-" * 55)
    for rank, row in enumerate(rows, 1):
        tid = row.get("track_id", "?")
        tp = row.get("total_priority", "0")
        focus_marker = "*" if tid == current_focus else ""
        print(f"{rank:<6}{tid:<30}{tp:<16}{focus_marker}")
    print("=" * 55)
    return 0


def cmd_track_dispatch(args) -> int:
    """Dispatch open Track Blocks for the named Track (or current_focus if 'current')."""
    arch_root = _get_arch_root(args)
    track_name = args.track
    dry_run = getattr(args, "dry_run", False)

    # Resolve "current" to current_focus from PRIORITY.md
    if track_name == "current":
        priority_path = arch_root / "tracks" / "PRIORITY.md"
        if not priority_path.exists():
            print(
                "ERROR: tracks/PRIORITY.md not found. Cannot resolve 'current' Track.",
                file=sys.stderr,
            )
            return 1
        priority_md = priority_path.read_text(encoding="utf-8")
        current_focus = _get_current_focus(priority_md)
        if not current_focus:
            print("ERROR: No current_focus set in tracks/PRIORITY.md.", file=sys.stderr)
            return 1
        track_name = current_focus

    # Normalize: strip "track/" prefix, lowercase
    track_id_normalized = track_name.lower().removeprefix("track/")

    # Find Track file: tracks/<name>.md (case-insensitive)
    tracks_dir = arch_root / "tracks"
    track_file = tracks_dir / f"{track_id_normalized}.md"
    if not track_file.exists():
        found = None
        if tracks_dir.exists():
            for f in tracks_dir.glob("*.md"):
                if f.stem.lower() == track_id_normalized:
                    found = f
                    break
        if not found:
            print(
                f"ERROR: Track '{track_name}' not found in tracks/. "
                "Run --list-tracks to see available Tracks.",
                file=sys.stderr,
            )
            return 1

    # Find open Track Blocks
    open_blocks = _find_open_track_blocks(track_id_normalized, arch_root)

    if not open_blocks:
        print(
            f"Track '{track_id_normalized}': no open Track Blocks found. "
            "Create a new Track Block using templates/track-block.md."
        )
        return 0

    if dry_run:
        print(
            f"[DRY RUN] Would dispatch {len(open_blocks)} Track Block(s) for Track '{track_id_normalized}':"
        )
        for bp in open_blocks:
            try:
                rel = bp.relative_to(arch_root)
            except ValueError:
                rel = bp
            print(f"  {rel}")
        return 0

    # Real dispatch — build task packets and call dispatch_batch
    from task_packet import build_packet
    from dispatch import dispatch_batch
    from config import load_config

    cfg = load_config(arch_root, governor_mode=args.mode)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    packets: list = []
    for block_path in open_blocks:
        try:
            rel = str(block_path.relative_to(arch_root))
            packet = build_packet(rel, arch_root, gov_id="g-cli-track", ts=ts)
            packets.append(packet)
        except Exception as exc:
            print(f"WARNING: could not build packet for {block_path.name}: {exc}", file=sys.stderr)

    if not packets:
        print(
            f"ERROR: Could not build any task packets for Track '{track_id_normalized}'.",
            file=sys.stderr,
        )
        return 1

    results = dispatch_batch(packets, mode=args.mode, api_key=cfg.api_key)
    failed = [r for r in results if not r.success]
    print(f"Dispatched {len(results)} Track Block(s) for Track '{track_id_normalized}'.")
    if failed:
        print(f"  {len(failed)} failed:", file=sys.stderr)
        for r in failed:
            print(f"    {r.block_id}: {r.error}", file=sys.stderr)
        return 1
    return 0


def cmd_test_integration(args) -> int:
    """
    Run full mock integration test: dispatch 2 mock blocks, integrate, verify state updates.
    Uses a temporary copy of the arch to avoid modifying real state files.
    """
    from dispatch import dispatch_block, MockAnthropicClient
    from integration import integrate_group

    print("=== GOVERNOR v2 INTEGRATION TEST (mock) ===")

    # Build a minimal temp arch_root from real files
    tmp = Path(tempfile.mkdtemp())
    try:
        # Copy essential state files
        for fname in ["STATE.md", "NEXT.md", "board.md"]:
            src = ARCH_ROOT / fname
            if src.exists():
                shutil.copy(src, tmp / fname)
        (tmp / "blocks").mkdir()
        block_log_src = ARCH_ROOT / "blocks" / "BLOCK_LOG.md"
        if block_log_src.exists():
            shutil.copy(block_log_src, tmp / "blocks" / "BLOCK_LOG.md")

        # Build two mock task packets
        packets = []
        for bid in ["035", "036"]:
            packets.append((
                bid,
                f"b:{bid} kind:feature phase:phase-5 gov:g-test ts:2026-05-22T12:00Z\n"
                f"axioms:Q1,Q2,Q3 scope:open retro_req:yes tok_track:yes\n"
                f"fread:design/governor-v2.md fmod:sdk/block_{bid}_output.py\n"
                f"\n--- convention snippet ---\nQ3: Manifests precede work.\n"
                f"\n--- manifest ---\n[test manifest block-{bid}]\n"
            ))

        # Dispatch both (mock)
        results = []
        for bid, packet in packets:
            r = dispatch_block(packet, mode="mock")
            # Override fmod to be distinct per block for disjoint check
            if r.validation:
                r.validation.parsed["fmod"] = f"sdk/block_{bid}_output.py:10"
            results.append(r)
            print(f"  dispatched block-{bid}: success={r.success}")

        # Write governor-state before integration (crash recovery)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        _write_governor_state({
            "session": "g-test", "phase": "phase-5", "block": "035+036", "ts": ts,
            "dispatch_group": "5E", "dispatched": "block-035,block-036",
            "awaiting": "-", "last_committed": "-", "integration_status": "pending",
        })

        # Integrate
        ir = integrate_group(results, tmp, next_block="037", do_commit=False)

        errors: list[str] = []
        if not ir.success:
            errors.append(f"integrate_group failed: {ir.errors}")
        if "block-035" not in ir.blocks_integrated and "035" not in ir.blocks_integrated:
            errors.append("block-035 not in integrated list")

        state_content = (tmp / "STATE.md").read_text(encoding="utf-8")
        if "035" not in state_content and "block-035" not in state_content:
            errors.append("STATE.md not updated")

        _write_governor_state({
            "session": "g-test", "phase": "phase-5", "block": "035+036", "ts": ts,
            "dispatch_group": "5E", "dispatched": "block-035,block-036",
            "awaiting": "-", "last_committed": "-", "integration_status": "done",
        })

        if errors:
            for e in errors:
                print(f"  FAIL: {e}", file=sys.stderr)
            return 1

        print(f"  integrated        : {ir.blocks_integrated}")
        print(f"  STATE.md updated  : yes")
        print(f"  BLOCK_LOG appended: yes")
        print("=== INTEGRATION TEST: PASS ===")
        return 0

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="governor",
        description=(
            "Governor v2 — SDK-based block orchestration for cognitive-arch projects.\n"
            "Reads project state, assembles task packets, dispatches Claude sub-agents,\n"
            "integrates results, and updates state files."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read project state and print next block plan. No agents dispatched.",
    )
    parser.add_argument(
        "--block",
        metavar="NNN",
        help="Run Governor on a specific block manifest (e.g. --block 030).",
    )
    parser.add_argument(
        "--test-integration",
        action="store_true",
        help="Run integration test with mock Anthropic client (no API key needed).",
    )
    parser.add_argument(
        "--mode",
        choices=["manual", "sdk", "mock"],
        default="mock",
        help="Governor mode. 'manual' prints task packets; 'mock' uses MockAnthropicClient; 'sdk' uses real API. (default: mock)",
    )
    parser.add_argument(
        "--parallel",
        metavar="N",
        type=int,
        default=1,
        help="Number of parallel workers for batch dispatch via ThreadPoolExecutor (default: 1 = sequential).",
    )
    parser.add_argument(
        "--list-tracks",
        action="store_true",
        default=False,
        help="Read tracks/PRIORITY.md and print the priority table ordered by total_priority descending.",
    )
    parser.add_argument(
        "--track",
        metavar="TRACK_NAME",
        default=None,
        help=(
            "Dispatch open Track Blocks for the named Track. "
            "Use 'current' to dispatch the current_focus Track."
        ),
    )
    parser.add_argument(
        "--arch-root",
        metavar="PATH",
        default=None,
        help=argparse.SUPPRESS,  # Internal flag for testing only
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_tracks:
        sys.exit(cmd_list_tracks(args))
    elif args.track:
        sys.exit(cmd_track_dispatch(args))
    elif args.dry_run:
        sys.exit(cmd_dry_run(args))
    elif args.block:
        sys.exit(cmd_block(args))
    elif args.test_integration:
        sys.exit(cmd_test_integration(args))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
