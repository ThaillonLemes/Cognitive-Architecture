# sdk/invariant_check.py
# PURPOSE: Declarative anti-drift engine — runs INV1-INV6 over an arch root, returns
#          Violations; block-145 adds DRY-RUN-BY-DEFAULT auto-repair (--repair/--apply).
# INPUTS:  arch root (.integrity.lock, blocks/BLOCK_LOG.md, blocks/*.md, manifests/*.md,
#          governance/proposals/*, STATE.md, NEXT.md, session_start.TOOL_RUNNERS, tools-registry.yaml)
# OUTPUTS: list[Violation]; list[RepairAction]; CLI prints either and exits 0
# DEPS:    stdlib only; reuses sdk/integrity_check (load_lock, find_immutable_files, regenerate),
#          sdk/project_state (completed_block_ids), sdk/session_start (TOOL_RUNNERS)
# SEE:     sdk/invariant_schema.py, commands/integrity-bump.md (INV1 human gate),
#          phases/phase-25.md, sdk/pattern_analyzer.py (never-crash style)

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

# Allow running both as a module and as a script (python sdk/invariant_check.py).
_SDK_DIR = Path(__file__).resolve().parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import integrity_check  # noqa: E402  (reused for INV1)
import project_state  # noqa: E402   (canonical BLOCK_LOG reader, INV2/INV5)
from invariant_schema import Invariant, RepairAction, Violation  # noqa: E402


# ---------------------------------------------------------------------------
# Force UTF-8 output on Windows (mirrors session_start._fix_utf8)
# ---------------------------------------------------------------------------

def _fix_utf8() -> None:
    import io as _io
    if sys.platform == "win32":
        if hasattr(sys.stdout, "buffer") and not (
            isinstance(sys.stdout, _io.TextIOWrapper)
            and sys.stdout.encoding.lower() == "utf-8"
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Small shared parse helpers (stdlib-only, never raise)
# ---------------------------------------------------------------------------

def _read(arch_root: Path, rel: str) -> str:
    try:
        return (arch_root / rel).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _frontmatter(text: str) -> str:
    """Content between the first and second '---' markers ('' if none)."""
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""


def _retro_files(arch_root: Path) -> list[Path]:
    """block-NNN-*.md retro files in blocks/ (excludes phase-* and BLOCK_LOG)."""
    blocks_dir = arch_root / "blocks"
    if not blocks_dir.exists():
        return []
    out = []
    for p in sorted(blocks_dir.glob("block-*-*.md")):
        if "phase-" in p.name or "LOG" in p.name.upper():
            continue
        out.append(p)
    return out


def _block_num(block_id: str) -> str:
    """'block-085' -> '085' (the zero-padded number used in retro filenames)."""
    m = re.match(r"block-(\d+)", block_id)
    return m.group(1) if m else block_id


def _retro_exists(arch_root: Path, block_id: str) -> bool:
    num = _block_num(block_id)
    blocks_dir = arch_root / "blocks"
    if not blocks_dir.exists():
        return False
    return any(True for _ in blocks_dir.glob(f"block-{num}-*.md"))


def _manifest_tier(arch_root: Path, block_id: str) -> str | None:
    """tier: from the block's manifest frontmatter, or None."""
    mdir = arch_root / "manifests"
    if not mdir.exists():
        return None
    for cand in sorted(mdir.glob(f"block-{_block_num(block_id)}-*.md")):
        fm = _frontmatter(cand.read_text(encoding="utf-8", errors="ignore"))
        m = re.search(r"^tier:\s*(\S+)", fm, re.MULTILINE)
        if m:
            return m.group(1)
    return None


# ---------------------------------------------------------------------------
# INV1 — every protection:immutable file is present in .integrity.lock
# ---------------------------------------------------------------------------

def check_inv1(arch_root: Path) -> list[str]:
    immutable = integrity_check.find_immutable_files(arch_root)
    lock = integrity_check.load_lock(arch_root)
    missing = [rel for rel in immutable if rel not in lock]
    return [f"immutable file not in .integrity.lock: {rel}" for rel in missing]


# ---------------------------------------------------------------------------
# INV2 — every 'done' block in BLOCK_LOG has a retro file in blocks/
# ---------------------------------------------------------------------------

def check_inv2(arch_root: Path) -> list[str]:
    out = []
    for block_id in project_state.completed_block_ids(arch_root):
        if not _retro_exists(arch_root, block_id):
            out.append(f"{block_id} is 'done' in BLOCK_LOG but has no blocks/{block_id}-*.md retro")
    return out


# ---------------------------------------------------------------------------
# INV3 — every retro with actual_duration_hours has a resolvable tier
# ---------------------------------------------------------------------------

def check_inv3(arch_root: Path) -> list[str]:
    out = []
    for retro in _retro_files(arch_root):
        fm = _frontmatter(retro.read_text(encoding="utf-8", errors="ignore"))
        if not re.search(r"^actual_duration_hours:\s*[0-9.]+", fm, re.MULTILINE):
            continue  # no duration -> INV3 not applicable
        id_m = re.search(r"^id:\s*(block-\d+)", fm, re.MULTILINE)
        block_id = id_m.group(1) if id_m else retro.stem
        # tier resolvable from retro frontmatter OR the matching manifest
        tier = None
        tm = re.search(r"^tier:\s*(\S+)", fm, re.MULTILINE)
        if tm:
            tier = tm.group(1)
        if tier is None:
            tier = _manifest_tier(arch_root, block_id)
        if tier is None:
            out.append(
                f"{block_id} has actual_duration_hours but no resolvable tier "
                f"(missing in retro frontmatter and manifest)"
            )
    return out


# ---------------------------------------------------------------------------
# INV4 — every key in session_start.TOOL_RUNNERS exists as an id: in the registry
# ---------------------------------------------------------------------------

def _registry_ids(arch_root: Path) -> set[str]:
    """All `- id:` values under `tools:` in governance/tools-registry.yaml."""
    text = _read(arch_root, "governance/tools-registry.yaml")
    ids: set[str] = set()
    for m in re.finditer(r"^\s*-\s*id:\s*['\"]?([A-Za-z0-9_-]+)", text, re.MULTILINE):
        ids.add(m.group(1))
    return ids


# Event-tools that may legitimately appear in TOOL_RUNNERS without a registry id.
# (None today — placeholder so a future runner can be whitelisted without code edits.)
_KNOWN_EVENT_TOOLS: set[str] = set()


def check_inv4(arch_root: Path) -> list[str]:
    # Import the REAL dict at check time so INV4 tracks it, never a stale copy.
    import session_start  # local import keeps engine import cheap / resilient
    runners = getattr(session_start, "TOOL_RUNNERS", {})
    registry = _registry_ids(arch_root)
    out = []
    for tool_id in runners:
        if tool_id in registry or tool_id in _KNOWN_EVENT_TOOLS:
            continue
        out.append(f"TOOL_RUNNERS key '{tool_id}' is not an id in governance/tools-registry.yaml")
    return out


# ---------------------------------------------------------------------------
# INV5 — STATE.last_block == highest done block; NEXT not pointing at a done block
# ---------------------------------------------------------------------------

def _highest_block_id(done_ids: list[str]) -> str | None:
    """Highest block-NNN by numeric value (BLOCK_LOG is not strictly ordered)."""
    nums = [(int(_block_num(b)), b) for b in done_ids if _block_num(b).isdigit()]
    return max(nums)[1] if nums else None


def check_inv5(arch_root: Path) -> list[str]:
    out = []
    done = project_state.completed_block_ids(arch_root)
    highest = _highest_block_id(done)

    state_text = _read(arch_root, "STATE.md")
    sm = re.search(r"\blast_block:(block-\d+)", state_text)
    state_last = sm.group(1) if sm else None

    if highest is not None:
        if state_last is None:
            out.append("STATE.md has no last_block field")
        elif state_last != highest:
            out.append(
                f"STATE.md last_block={state_last} != highest done block in BLOCK_LOG ({highest})"
            )

    # NEXT.md next_action must not point at an already-done block.
    next_text = _read(arch_root, "NEXT.md")
    nm = re.search(r"next_action:\s*(block-\d+)", next_text)
    if nm:
        next_block = nm.group(1)
        if next_block in set(done):
            out.append(
                f"NEXT.md next_action={next_block} points at a block already 'done' in BLOCK_LOG"
            )
    return out


# ---------------------------------------------------------------------------
# INV6 — every proposals/*.md file <-> a row in proposals/index.md (both ways)
# ---------------------------------------------------------------------------

def check_inv6(arch_root: Path) -> list[str]:
    pdir = arch_root / "governance" / "proposals"
    if not pdir.exists():
        return []  # no proposals layer yet -> nothing to reconcile

    files = {p.name for p in pdir.glob("*.md") if p.name != "index.md"}

    index_path = pdir / "index.md"
    index_text = index_path.read_text(encoding="utf-8", errors="ignore") if index_path.exists() else ""
    # Filenames referenced from index rows: match `...(...<name>.md)` links and bare `<name>.md`.
    indexed: set[str] = set()
    for m in re.finditer(r"([0-9A-Za-z._-]+\.md)", index_text):
        name = m.group(1).split("/")[-1]
        if name != "index.md":
            indexed.add(name)

    out = []
    for fname in sorted(files - indexed):
        out.append(f"proposal file governance/proposals/{fname} has no row in index.md")
    for fname in sorted(indexed - files):
        out.append(f"index.md references missing proposal file governance/proposals/{fname}")
    return out


# ===========================================================================
# REPAIRS (block-145) — DRY-RUN BY DEFAULT. A repair writes ONLY when apply=True,
# and ONLY after _backup() copies the target. INV1 is the one exception that
# never writes its live file even with --apply (the lock is human-gated).
# ===========================================================================

BACKUP_DIR = "_backups"


def _stamp(data: bytes) -> str:
    """Deterministic 8-hex stamp from content (Date.now()/random are unavailable).

    Two different pre-write contents get distinct backups; re-running a repair on
    the SAME content overwrites the same backup rather than accreting duplicates.
    """
    return hashlib.sha256(data).hexdigest()[:8]


def _backup(path: Path, arch_root: Path) -> str:
    """Copy `path` to _backups/<filename>.<stamp>.bak BEFORE any mutating write.

    Returns the backup's arch-root-relative POSIX path. NEVER call a live write
    without calling this first. The stamp is derived from the file's CURRENT
    bytes, so a backup always captures the pre-repair state.
    """
    data = path.read_bytes()
    backups = arch_root / BACKUP_DIR
    backups.mkdir(parents=True, exist_ok=True)
    dest = backups / f"{path.name}.{_stamp(data)}.bak"
    dest.write_bytes(data)
    return dest.relative_to(arch_root).as_posix()


# ---------------------------------------------------------------------------
# INV1 repair — STAGE ONLY. The lock is protection:immutable per
# commands/integrity-bump.md, so repair NEVER rewrites .integrity.lock (that
# would bypass the human gate). It stages the regenerated lock to
# _backups/.integrity.lock.proposed and emits the exact integrity-bump command.
# ---------------------------------------------------------------------------

_INTEGRITY_BUMP_CMD = "python sdk/integrity_check.py --regenerate --arch-root ."


def repair_inv1(arch_root: Path, *, apply: bool = False) -> list[RepairAction]:
    immutable = integrity_check.find_immutable_files(arch_root)
    lock = integrity_check.load_lock(arch_root)
    missing = [rel for rel in immutable if rel not in lock]
    if not missing:
        return [RepairAction(
            invariant_id="INV1", kind="noop",
            description="INV1 clean — .integrity.lock covers every immutable file.",
        )]

    details = [f"missing from lock: {rel}" for rel in missing]
    details.append(f"human gate: run `{_INTEGRITY_BUMP_CMD}` after review (see commands/integrity-bump.md)")

    backup_rel = None
    if apply:
        # Stage the REGENERATED lock content beside the real one — but never as the
        # live .integrity.lock. We compute the same bytes integrity_check.regenerate
        # would write, then drop them at _backups/.integrity.lock.proposed.
        try:
            proposed = _proposed_lock_text(arch_root, immutable)
            backups = arch_root / BACKUP_DIR
            backups.mkdir(parents=True, exist_ok=True)
            staged = backups / ".integrity.lock.proposed"
            staged.write_text(proposed, encoding="utf-8")
            backup_rel = staged.relative_to(arch_root).as_posix()
            details.append(f"staged proposed lock at {backup_rel} (NOT applied — human gate owns the live write)")
        except Exception as exc:  # staging is best-effort; never break the engine
            details.append(f"could not stage proposed lock: {exc}")

    return [RepairAction(
        invariant_id="INV1",
        kind="stage",
        description=(
            f"{len(missing)} immutable file(s) missing from .integrity.lock — "
            f"STAGED for the integrity-bump human gate (lock is immutable, never auto-written)."
        ),
        requires_human=True,
        applied=False,                       # the live lock is NEVER written here
        details=details,
        backup_path=backup_rel,
    )]


def _proposed_lock_text(arch_root: Path, immutable: list[str]) -> str:
    """The exact text integrity_check.regenerate would write — computed WITHOUT writing.

    Mirrors integrity_check.regenerate's format so a human can diff the staged
    .proposed against the live lock before bumping.
    """
    lines = [
        "# .integrity.lock — SHA256 hashes of immutable-tagged files",
        "# Regenerated by: sdk/integrity_check.py --regenerate",
        "# See: commands/integrity-bump.md for the approved human-approval workflow",
        "",
    ]
    for rel in immutable:
        h = integrity_check.sha256_of_file(arch_root / rel)
        lines.append(f"{rel}  sha256:{h}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# INV4 repair — REPORT/STAGE only. A registry row needs name/command/interval a
# human supplies, and tools-registry.yaml is guarded, so repair emits the
# suggested stub and never writes.
# ---------------------------------------------------------------------------

def repair_inv4(arch_root: Path, *, apply: bool = False) -> list[RepairAction]:
    import session_start
    runners = getattr(session_start, "TOOL_RUNNERS", {})
    registry = _registry_ids(arch_root)
    missing = [tid for tid in runners if tid not in registry and tid not in _KNOWN_EVENT_TOOLS]
    if not missing:
        return [RepairAction(
            invariant_id="INV4", kind="noop",
            description="INV4 clean — every TOOL_RUNNERS key is registered.",
        )]

    details: list[str] = [
        "add to governance/tools-registry.yaml (human fills name/command/interval):",
    ]
    for tid in missing:
        details.append(f"  - id: {tid}")
        details.append(f"    name: \"<human: {tid} display name>\"")
        details.append(f"    command: \"<human: command to run {tid}>\"")
        details.append("    interval_hours: <human: cadence>")

    return [RepairAction(
        invariant_id="INV4",
        kind="stage",
        description=(
            f"{len(missing)} TOOL_RUNNERS key(s) missing from tools-registry.yaml — "
            f"stub emitted; registry is guarded, NOT auto-written."
        ),
        requires_human=True,
        applied=False,
        details=details,
    )]


# ---------------------------------------------------------------------------
# INV6 repair — SAFE AUTO-FIX. Reconcile proposals/index.md <-> files:
#   * append a row for any proposal file missing from the index (auto, may apply);
#   * FLAG (never delete) index rows whose file is missing — that's a human call.
# Backs up index.md before writing under --apply.
# ---------------------------------------------------------------------------

def _proposal_meta(path: Path) -> tuple[str, str, str]:
    """(date, pattern_id, status) parsed from a proposal's frontmatter (best-effort)."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    fm = _frontmatter(text)
    def _field(name: str, default: str) -> str:
        m = re.search(rf"^{name}:\s*(.+)$", fm, re.MULTILINE)
        return m.group(1).strip() if m else default
    date_str = _field("created_at", path.name[:10] if len(path.name) >= 10 else "~")
    pattern_id = _field("pattern_id", "~")
    status = _field("status", "pending")
    return date_str, pattern_id, status


def repair_inv6(arch_root: Path, *, apply: bool = False) -> list[RepairAction]:
    pdir = arch_root / "governance" / "proposals"
    if not pdir.exists():
        return [RepairAction(
            invariant_id="INV6", kind="noop",
            description="No governance/proposals/ layer — nothing to reconcile.",
        )]

    files = {p.name for p in pdir.glob("*.md") if p.name != "index.md"}
    index_path = pdir / "index.md"
    index_text = index_path.read_text(encoding="utf-8", errors="ignore") if index_path.exists() else ""
    indexed: set[str] = set()
    for m in re.finditer(r"([0-9A-Za-z._-]+\.md)", index_text):
        name = m.group(1).split("/")[-1]
        if name != "index.md":
            indexed.add(name)

    orphans = sorted(files - indexed)        # files with no index row -> append (safe)
    ghosts = sorted(indexed - files)         # index rows with no file  -> flag only

    if not orphans and not ghosts:
        return [RepairAction(
            invariant_id="INV6", kind="noop",
            description="INV6 clean — proposals index and files reconcile both ways.",
        )]

    actions: list[RepairAction] = []

    # --- Direction 1: orphan files -> append a row (the auto-fixable half) ---
    if orphans:
        new_rows: list[str] = []
        for fname in orphans:
            date_str, pattern_id, status = _proposal_meta(pdir / fname)
            stem = fname[:-3] if fname.endswith(".md") else fname
            rel = f"governance/proposals/{fname}"
            new_rows.append(f"| {date_str} | [{stem}]({rel}) | {pattern_id} | ~ | {status} |")

        details = [f"append row for orphan: {f}" for f in orphans]
        backup_rel = None
        applied = False
        if apply:
            try:
                base = index_text if index_text else _default_index_header()
                if index_path.exists():
                    backup_rel = _backup(index_path, arch_root)   # ALWAYS back up first
                if base and not base.endswith("\n"):
                    base += "\n"
                new_text = base + "\n".join(new_rows) + "\n"
                index_path.write_text(new_text, encoding="utf-8")
                applied = True
                if backup_rel:
                    details.append(f"backed up prior index to {backup_rel}")
            except Exception as exc:
                actions.append(RepairAction(
                    invariant_id="INV6", kind="failed",
                    description=f"INV6 index append failed: {exc}",
                    details=details,
                ))
                orphans = []  # fall through without a misleading 'apply' action
        if orphans:
            actions.append(RepairAction(
                invariant_id="INV6",
                kind="apply",
                description=(
                    f"{'Appended' if applied else 'Would append'} {len(orphans)} "
                    f"missing index row(s) for orphan proposal file(s)."
                ),
                requires_human=False,
                applied=applied,
                details=details,
                backup_path=backup_rel,
            ))

    # --- Direction 2: ghost rows -> FLAG only (never delete) ---
    if ghosts:
        actions.append(RepairAction(
            invariant_id="INV6",
            kind="manual",
            description=(
                f"{len(ghosts)} index row(s) reference a missing proposal file — "
                f"FLAGGED for a human (reconcile never deletes)."
            ),
            requires_human=True,
            applied=False,
            details=[f"index row references missing file: governance/proposals/{g}" for g in ghosts],
        ))

    return actions


def _default_index_header() -> str:
    """Header used when proposals/index.md is absent — matches protocol_updater's."""
    return (
        "# Proposals Index — Governance\n\n"
        "| Date | ID | Pattern | Target File | Status |\n"
        "|------|----|---------|-------------|--------|\n"
    )


# ---------------------------------------------------------------------------
# INV2 / INV3 / INV5 repair — NO auto-fix. Describe the manual remedy.
# ---------------------------------------------------------------------------

def _manual_repair(arch_root: Path, *, apply: bool, inv_id: str, kind: str, check, remedy: str) -> list[RepairAction]:
    msgs = check(arch_root)
    if not msgs:
        return [RepairAction(invariant_id=inv_id, kind="noop",
                             description=f"{inv_id} clean — no manual action needed.")]
    return [RepairAction(
        invariant_id=inv_id,
        kind=kind,
        description=f"{inv_id}: {remedy}",
        requires_human=True,
        applied=False,
        details=list(msgs),
    )]


def repair_inv2(arch_root: Path, *, apply: bool = False) -> list[RepairAction]:
    return _manual_repair(
        arch_root, apply=apply, inv_id="INV2", kind="manual", check=check_inv2,
        remedy="no auto-repair — backfill the missing retro by hand (block-147 / block-close).",
    )


def repair_inv3(arch_root: Path, *, apply: bool = False) -> list[RepairAction]:
    return _manual_repair(
        arch_root, apply=apply, inv_id="INV3", kind="manual", check=check_inv3,
        remedy="no auto-repair — add `tier:` to the retro or its manifest by hand.",
    )


def repair_inv5(arch_root: Path, *, apply: bool = False) -> list[RepairAction]:
    return _manual_repair(
        arch_root, apply=apply, inv_id="INV5", kind="halt", check=check_inv5,
        remedy="no auto-repair — STATE/NEXT pointers are human-owned; fix by hand (HALT).",
    )


# ---------------------------------------------------------------------------
# Registry — invariants are DATA. Add one == add an entry here + a check fn.
# Severities follow the block-144 task spec (INV1/INV4 critical; rest warn).
# `repair` (block-145) is DRY-RUN by default; INV1/INV4 stage, INV6 auto-fixes,
# INV2/INV3/INV5 report a manual/halt action.
# ---------------------------------------------------------------------------

REGISTRY: list[Invariant] = [
    Invariant(
        id="INV1",
        description="Every protection:immutable file is present in .integrity.lock.",
        severity="critical",
        check=check_inv1,
        repair=repair_inv1,        # STAGE only — never writes the immutable lock
    ),
    Invariant(
        id="INV2",
        description="Every 'done' block in BLOCK_LOG has a blocks/block-NNN-*.md retro file.",
        severity="warn",
        check=check_inv2,
        repair=repair_inv2,        # manual — backfill by hand
    ),
    Invariant(
        id="INV3",
        description="Every retro with actual_duration_hours resolves a tier (retro or manifest).",
        severity="warn",
        check=check_inv3,
        repair=repair_inv3,        # manual — add tier by hand
    ),
    Invariant(
        id="INV4",
        description="Every session_start.TOOL_RUNNERS key is an id in tools-registry.yaml.",
        severity="critical",
        check=check_inv4,
        repair=repair_inv4,        # stage — emit registry stub, never auto-write
    ),
    Invariant(
        id="INV5",
        description="STATE.last_block == highest done block; NEXT.next_action is not already done.",
        severity="warn",
        check=check_inv5,
        repair=repair_inv5,        # halt — human-owned pointers
    ),
    Invariant(
        id="INV6",
        description="Every proposals/*.md file has an index.md row and vice-versa.",
        severity="warn",
        check=check_inv6,
        repair=repair_inv6,        # SAFE auto-fix — append orphan rows; flag ghosts
    ),
]


# ---------------------------------------------------------------------------
# Engine — never raises (mirrors pattern_analyzer.analyze)
# ---------------------------------------------------------------------------

def run_all(arch_root: Path, registry: list[Invariant] | None = None) -> list[Violation]:
    """Run every invariant's check over `arch_root`, returning all Violations.

    A check that raises is degraded to a single `warn` Violation ("<id>: check
    errored: ...") — it NEVER propagates, so one broken invariant can't crash a
    session or a block close. Mirrors pattern_analyzer's per-rule try/except.
    """
    arch_root = Path(arch_root)
    reg = REGISTRY if registry is None else registry
    violations: list[Violation] = []
    for inv in reg:
        try:
            messages = inv.check(arch_root)
        except Exception as exc:  # a buggy check must never crash the engine
            violations.append(Violation(
                invariant_id=inv.id,
                severity="warn",
                message=f"{inv.id}: check errored: {exc}",
                evidence=[],
            ))
            continue
        for msg in messages:
            violations.append(Violation(
                invariant_id=inv.id,
                severity=inv.severity,
                message=msg,
                evidence=[msg],
            ))
    return violations


def gate_result(arch_root: Path,
                registry: list[Invariant] | None = None) -> tuple[bool, list[Violation]]:
    """Block-close gate: (ok, critical_violations) where ok == (no criticals).

    This is what the block-close flow calls at its validate-gates step to decide
    whether to HALT: `ok is False` ⇒ a critical invariant is broken and the close
    must stop (consistent with the existing gate-fail flow). The session_start
    surfacing path deliberately does NOT consult this — it only reports counts —
    so the HALT authority lives in exactly one place.

    Pure + never raises: it reuses `run_all` (which degrades any check that errors
    to a `warn`, never a critical), so a buggy invariant can't fabricate a HALT.
    """
    violations = run_all(arch_root, registry=registry)
    criticals = [v for v in violations if v.severity == "critical"]
    return (not criticals), criticals


def repair_all(arch_root: Path, *, apply: bool = False,
               registry: list[Invariant] | None = None) -> list[RepairAction]:
    """Drive every invariant's `repair`, returning the actions it took or would take.

    DRY-RUN BY DEFAULT: with apply=False nothing on disk changes — repairs return
    descriptive RepairActions only. With apply=True, repairs may write, but ONLY
    after _backup(), and ONLY the auto-fixable INV6 actually mutates a live file;
    INV1/INV4 stay STAGE (they emit instructions, never write the guarded file).

    Never raises: a repair that errors degrades to one kind="failed" RepairAction
    (mirrors run_all's per-check try/except), so one broken repair can't abort a
    --repair sweep. Invariants without a `repair` are skipped silently (none today).
    """
    arch_root = Path(arch_root)
    reg = REGISTRY if registry is None else registry
    actions: list[RepairAction] = []
    for inv in reg:
        if inv.repair is None:
            continue
        try:
            actions.extend(inv.repair(arch_root, apply=apply))
        except Exception as exc:  # a buggy repair must never crash the sweep
            actions.append(RepairAction(
                invariant_id=inv.id,
                kind="failed",
                description=f"{inv.id}: repair errored: {exc}",
                requires_human=True,
            ))
    return actions


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_report(arch_root: Path, violations: list[Violation]) -> None:
    by_inv = {inv.id: inv for inv in REGISTRY}
    fired = {v.invariant_id for v in violations}

    print("=" * 60)
    print("  cognitive-arch :: INVARIANT CHECK")
    print(f"  arch-root: {arch_root}")
    print("=" * 60)

    # One status line per invariant (OK / VIOLATION + count).
    for inv in REGISTRY:
        count = sum(1 for v in violations if v.invariant_id == inv.id)
        status = f"VIOLATION ({count})" if inv.id in fired else "OK"
        print(f"  {inv.id} [{inv.severity}] {status} — {inv.description}")
    print("-" * 60)

    criticals = [v for v in violations if v.severity == "critical"]
    warns = [v for v in violations if v.severity == "warn"]

    if criticals:
        print(f"  CRITICAL ({len(criticals)}):")
        for v in criticals:
            print(f"    [{v.invariant_id}] {v.message}")
    if warns:
        print(f"  WARN ({len(warns)}):")
        for v in warns:
            print(f"    [{v.invariant_id}] {v.message}")
    if not violations:
        print("  No violations — all invariants clean.")

    print("-" * 60)
    print(f"  Totals: {len(criticals)} critical, {len(warns)} warn")
    print("=" * 60)


_KIND_LABEL = {
    "apply": "AUTO-FIX",
    "stage": "STAGE (human gate)",
    "manual": "MANUAL",
    "halt": "HALT",
    "noop": "ok",
    "failed": "FAILED",
}


def _print_repair_report(arch_root: Path, actions: list[RepairAction], *, apply: bool) -> None:
    mode = "APPLY" if apply else "DRY-RUN"
    prefix = "" if apply else "DRY-RUN "
    print("=" * 60)
    print("  cognitive-arch :: INVARIANT REPAIR")
    print(f"  arch-root: {arch_root}")
    print(f"  mode: {mode}" + ("" if apply else "  (default — writes NOTHING)"))
    print("=" * 60)

    # Skip noops in the body — they're just confirmation the invariant is clean.
    active = [a for a in actions if a.kind != "noop"]
    if not active:
        print("  No repairs needed — all repairable invariants are clean.")
    for a in active:
        label = _KIND_LABEL.get(a.kind, a.kind.upper())
        verb = "applied" if a.applied else ("staged" if a.kind == "stage" else "planned")
        print(f"  {prefix}[{a.invariant_id}] {label} — {a.description}")
        if a.applied:
            print(f"      (written; backup: {a.backup_path})")
        elif a.kind == "apply":
            print(f"      ({verb} — re-run with --apply to write)")
        for line in a.details:
            print(f"        {line}")

    applied_n = sum(1 for a in actions if a.applied)
    stage_n = sum(1 for a in actions if a.kind == "stage")
    manual_n = sum(1 for a in actions if a.kind in ("manual", "halt"))
    failed_n = sum(1 for a in actions if a.kind == "failed")
    print("-" * 60)
    print(f"  Totals: {applied_n} applied, {stage_n} staged, {manual_n} manual/halt, {failed_n} failed")
    if not apply:
        print("  DRY-RUN: nothing was written. Re-run with --apply to perform AUTO-FIX repairs.")
    print("=" * 60)


def main(argv: list[str] | None = None) -> int:
    _fix_utf8()
    parser = argparse.ArgumentParser(description="cognitive-arch invariant checker")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--repair", action="store_true",
                        help="Plan auto-repairs (DRY-RUN by default — writes nothing)")
    parser.add_argument("--apply", action="store_true",
                        help="With --repair, actually perform safe AUTO-FIX repairs (still backs up first)")
    args = parser.parse_args(argv)

    arch_root = Path(args.arch_root).resolve()

    if args.repair:
        # --apply only has meaning alongside --repair.
        actions = repair_all(arch_root, apply=args.apply)
        _print_repair_report(arch_root, actions, apply=args.apply)
        return 0
    if args.apply:
        print("--apply has no effect without --repair; running check only.")

    violations = run_all(arch_root)
    _print_report(arch_root, violations)
    # block-144 never HALTs — --strict / gate wiring is block-146.
    return 0


if __name__ == "__main__":
    sys.exit(main())
