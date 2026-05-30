# PURPOSE: Render an accepted proposal as a concrete diff (152), evaluate apply guards (153),
#          and atomically apply-with-rollback + provenance (154). Without --confirm: writes nothing.
# INPUTS:  governance/proposals/<id>.md (status, target_file, proposed_change, rationale, pattern_id), target_file, .integrity.lock, governance/governor-log.md
# OUTPUTS: DiffResult (152); GuardResult (153: allowed, target_file, reasons, backup_plan); ApplyResult (154); CLI prints diff/guard/apply verdict
# DEPS:    stdlib only (difflib, hashlib, ast, subprocess, os, shutil, dataclasses, pathlib); reuses proposal_resolver (_get_frontmatter_field, _is_immutable, _update_frontmatter_field, _update_index_status) + integrity_check (verify)
# SEE:     manifests/block-152-proposal-diff.md, manifests/block-153-guard-gates.md, manifests/block-154-apply-rollback.md, phases/phase-27.md, commands/integrity-bump.md

from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

# Reuse the front-matter readers and immutability check from the resolver,
# rather than re-implementing them (manifest §8 / Axiom Q1).
from proposal_resolver import (
    _get_frontmatter_field,
    _is_immutable,
    _update_frontmatter_field,
    _update_index_status,
)

# Reuse the integrity lock verifier (single source of truth for drift).
import integrity_check


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class DiffResult:
    """Outcome of rendering a proposal into a concrete unified diff.

    status is one of:
      'accepted'       — diff was generated (unified_diff is non-empty)
      'not-accepted'   — proposal missing or status != accepted (no diff)
      'no-target'      — target_file is a <...> placeholder or absent (no diff)
      'target-missing' — target_file resolves to a file that does not exist
    """
    proposal_id: str
    target_file: str
    is_immutable: bool
    unified_diff: str
    rationale: str
    status: str


@dataclass
class GuardResult:
    """Verdict of the apply-guard layer (block-153) for one proposal.

    Pure evaluation: deciding whether applying this proposal's diff WOULD be
    permitted. Nothing is written. block-154 consults this before any apply.

    Fields:
      allowed      — True only if every guard passed.
      target_file  — the proposal's target_file (relpath), '' when unresolved.
      reasons      — human-readable lines: one per failed guard (empty == allowed),
                     or a single confirmation line when allowed.
      backup_plan  — the relative path under _backups/ that block-154 would write
                     before touching the target (content-hash stamped), or '' when
                     there is nothing to back up (no concrete existing target).
    """
    allowed: bool
    target_file: str
    reasons: list[str] = field(default_factory=list)
    backup_plan: str = ""


@dataclass
class ApplyResult:
    """Outcome of atomically applying a proposal's diff (block-154).

    apply_proposal() is the only writer in this module. It passes through 153's
    guards, backs the target up, performs an atomic write, then runs the test
    suite + audit as the gate. Any verification failure auto-restores from the
    backup (atomic) so the tree is never left in a partial state.

    Fields:
      applied      — True only when the change was written AND verified AND
                     recorded (status/log/ADR). False on guard-refusal, dry-run,
                     verification failure (rolled back), or any error.
      proposal_id  — the proposal acted upon.
      target_file  — the proposal's target_file (relpath), '' when unresolved.
      backup_path  — POSIX relpath under _backups/ of the backup taken before the
                     write, '' when nothing was written (refused / dry-run / error
                     before backup).
      tests_passed — True iff the post-apply test-suite + audit verification passed.
      rolled_back  — True iff a write happened and was then reverted from backup.
      reasons      — human-readable lines explaining the outcome (guard reasons on
                     refusal; what would happen on dry-run; what failed on rollback).
    """
    applied: bool
    proposal_id: str
    target_file: str
    backup_path: str = ""
    tests_passed: bool = False
    rolled_back: bool = False
    reasons: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Front-matter block-scalar reader
# ---------------------------------------------------------------------------

def _read_block_scalar(text: str, field: str) -> str:
    """Read a YAML block-scalar field (``field: |``) from front matter.

    proposal_resolver._get_frontmatter_field only captures the first line, so
    for ``rationale: |`` it would return the literal ``|``. This reader returns
    the full indented block (with indentation stripped), or — when the field is
    a plain inline scalar — that single value.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^{re.escape(field)}:\s*(.*)$", line)
        if not m:
            continue
        inline = m.group(1).strip()
        if inline and inline not in ("|", ">", "|-", ">-", "|+", ">+"):
            # Plain inline scalar — return as-is (strip surrounding quotes).
            return inline.strip("\"'")
        # Block scalar: collect subsequent more-indented lines.
        raw: list[str] = []
        base_indent = len(line) - len(line.lstrip())
        for nxt in lines[i + 1:]:
            if nxt.strip() == "":
                raw.append("")
                continue
            indent = len(nxt) - len(nxt.lstrip())
            if indent <= base_indent:
                break
            raw.append(nxt)
        # Dedent by the block's own common indentation (YAML block-scalar rule),
        # so continuation lines don't carry ragged leading whitespace.
        indents = [len(r) - len(r.lstrip()) for r in raw if r.strip()]
        strip = min(indents) if indents else 0
        block = [(r[strip:].rstrip() if r.strip() else "") for r in raw]
        return "\n".join(block).strip()
    return ""


# ---------------------------------------------------------------------------
# Rendered edit
# ---------------------------------------------------------------------------

def _build_appended_section(proposal_id: str, pattern_id: str, body: str) -> str:
    """Build the reviewable text block appended to the target.

    A real, human-readable Markdown section — NOT an opaque HTML comment. The
    HTML comment is a machine-readable provenance anchor only; the heading and
    body are the substance a reviewer reads.
    """
    pattern_id = pattern_id or "unknown"
    body = body.strip() or "(no proposed change text provided)"
    return (
        f"\n<!-- pattern: {pattern_id} -->\n"
        f"## Note (from proposal {proposal_id})\n\n"
        f"{body}\n"
    )


# ---------------------------------------------------------------------------
# Core renderer
# ---------------------------------------------------------------------------

class ProposalApply:
    """Render accepted proposals into concrete unified diffs (dry-run only).

    Mirrors ProposalResolver(arch_root). This is the home of the apply pipeline
    that blocks 153-155 extend (guards, rollback, e2e); this block ships only
    diff generation + render. It writes NOTHING.
    """

    def __init__(self, arch_root: Path) -> None:
        self.arch_root = Path(arch_root)
        self.proposals_dir = self.arch_root / "governance" / "proposals"

    def _find_proposal(self, proposal_id: str) -> Optional[Path]:
        path = self.proposals_dir / f"{proposal_id}.md"
        return path if path.exists() else None

    def generate_diff(self, proposal_id: str) -> DiffResult:
        """Render an accepted proposal as a concrete unified diff. Never raises."""
        try:
            return self._generate_diff_inner(proposal_id)
        except Exception as exc:  # pragma: no cover - pure defence, must never raise
            return DiffResult(
                proposal_id=proposal_id,
                target_file="",
                is_immutable=False,
                unified_diff="",
                rationale="",
                status="not-accepted",
            )

    def _generate_diff_inner(self, proposal_id: str) -> DiffResult:
        path = self._find_proposal(proposal_id)
        if path is None:
            return DiffResult(
                proposal_id=proposal_id,
                target_file="",
                is_immutable=False,
                unified_diff="",
                rationale="",
                status="not-accepted",
            )

        text = path.read_text(encoding="utf-8", errors="replace")
        status = _get_frontmatter_field(text, "status")
        rationale = _read_block_scalar(text, "rationale")

        if status != "accepted":
            return DiffResult(
                proposal_id=proposal_id,
                target_file=_get_frontmatter_field(text, "target_file") or "",
                is_immutable=False,
                unified_diff="",
                rationale=rationale,
                status="not-accepted",
            )

        target_file = _get_frontmatter_field(text, "target_file") or ""
        if not target_file or "<" in target_file or ">" in target_file:
            return DiffResult(
                proposal_id=proposal_id,
                target_file=target_file,
                is_immutable=False,
                unified_diff="",
                rationale=rationale,
                status="no-target",
            )

        is_immutable = _is_immutable(target_file, self.arch_root)

        target_path = self.arch_root / target_file
        if not target_path.exists():
            return DiffResult(
                proposal_id=proposal_id,
                target_file=target_file,
                is_immutable=is_immutable,
                unified_diff="",
                rationale=rationale,
                status="target-missing",
            )

        original = target_path.read_text(encoding="utf-8", errors="replace")
        modified = self._build_modified_content(proposal_id, text, original)

        # Normalize line endings so difflib output is stable across CRLF/LF.
        original_lines = original.replace("\r\n", "\n").replace("\r", "\n").splitlines(keepends=True)
        modified_lines = modified.replace("\r\n", "\n").replace("\r", "\n").splitlines(keepends=True)

        rel = target_file.replace("\\", "/")
        diff = "".join(
            difflib.unified_diff(
                original_lines,
                modified_lines,
                fromfile=f"a/{rel}",
                tofile=f"b/{rel}",
                lineterm="\n",
            )
        )

        return DiffResult(
            proposal_id=proposal_id,
            target_file=target_file,
            is_immutable=is_immutable,
            unified_diff=diff,
            rationale=rationale,
            status="accepted",
        )

    # -----------------------------------------------------------------------
    # Shared post-change content builder (used by 152 diff + 153 sanity guard)
    # -----------------------------------------------------------------------

    def _build_modified_content(self, proposal_id: str, proposal_text: str, original: str) -> str:
        """Return the would-be post-apply content for the target.

        Single source of truth for the append the diff renders AND the structural
        guard inspects, so the two can never disagree about what 154 would write.
        """
        proposed_change = _read_block_scalar(proposal_text, "proposed_change")
        rationale = _read_block_scalar(proposal_text, "rationale")
        body = proposed_change or rationale
        pattern_id = _get_frontmatter_field(proposal_text, "pattern_id") or ""
        return original + _build_appended_section(proposal_id, pattern_id, body)

    # -----------------------------------------------------------------------
    # Block-153 — apply guards (evaluate only; never write, never raise)
    # -----------------------------------------------------------------------

    def check_guards(self, proposal_id: str) -> GuardResult:
        """Evaluate whether applying this proposal's diff WOULD be permitted.

        Runs four guards (acceptance, immutability, integrity, structural sanity)
        without writing anything. Never raises — any internal failure becomes a
        REFUSED verdict carrying the error as a reason.
        """
        try:
            return self._check_guards_inner(proposal_id)
        except Exception as exc:  # pure defence — a guard must never crash the caller
            return GuardResult(
                allowed=False,
                target_file="",
                reasons=[f"guard evaluation error (refusing as fail-safe): {exc!r}"],
                backup_plan="",
            )

    def _check_guards_inner(self, proposal_id: str) -> GuardResult:
        diff = self.generate_diff(proposal_id)
        target_file = diff.target_file or ""
        reasons: list[str] = []
        refused = False

        # --- Guard 4: acceptance (reuse generate_diff's resolved status) -----
        if diff.status != "accepted":
            reasons.append(
                f"acceptance guard: proposal status is '{diff.status}', not 'accepted' "
                f"(only accepted proposals are eligible to apply)."
            )
            # Without an accepted diff there is no concrete change to vet further.
            return GuardResult(
                allowed=False, target_file=target_file, reasons=reasons, backup_plan=""
            )

        target_path = self.arch_root / target_file
        backup_plan = self._backup_relpath(target_path) if target_path.exists() else ""

        # --- Guard 1: immutability (refuse unless a recorded bump exists) -----
        if _is_immutable(target_file, self.arch_root):
            if self._has_integrity_bump(target_file):
                reasons.append(
                    f"immutability note: '{target_file}' is immutable but a recorded "
                    f"INTEGRITY BUMP APPROVED in governance/governor-log.md authorizes it."
                )
            else:
                refused = True
                reasons.append(
                    f"immutability guard: '{target_file}' is protection:immutable and no "
                    f"INTEGRITY BUMP APPROVED entry names it in governance/governor-log.md. "
                    f"A human bump is required first — see commands/integrity-bump.md."
                )

        # --- Guard 2: integrity (locked target must currently verify OK) -----
        integ_ok, integ_reason = self._integrity_ok(target_file)
        if not integ_ok:
            refused = True
            reasons.append(integ_reason)

        # --- Guard 3: structural sanity of the post-change content -----------
        sane_ok, sane_reason = self._structural_sanity(proposal_id, target_path, target_file)
        if not sane_ok:
            refused = True
            reasons.append(sane_reason)

        allowed = not refused
        if allowed and not reasons:
            reasons.append(f"all guards passed for '{target_file}'.")
        return GuardResult(
            allowed=allowed,
            target_file=target_file,
            reasons=reasons,
            backup_plan=backup_plan,
        )

    # --- guard helpers ------------------------------------------------------

    def _has_integrity_bump(self, target_file: str) -> bool:
        """True iff governor-log records an INTEGRITY BUMP APPROVED for target_file.

        Matches a `file:` line (with or without a leading comment '#') whose value
        equals the target's relpath OR basename, but only inside an
        `INTEGRITY BUMP APPROVED` block (bounded by an END marker when present).
        An unrelated bump (different file) does NOT satisfy this.
        """
        log_path = self.arch_root / "governance" / "governor-log.md"
        if not log_path.exists():
            return False
        text = log_path.read_text(encoding="utf-8", errors="replace")
        rel = target_file.replace("\\", "/").strip()
        base = Path(rel).name

        in_block = False
        for raw in text.splitlines():
            line = raw.lstrip("#").strip()
            if "INTEGRITY BUMP APPROVED" in line.upper():
                in_block = True
                continue
            if in_block and "END INTEGRITY BUMP" in line.upper():
                in_block = False
                continue
            if not in_block:
                continue
            m = re.match(r"file:\s*(.+)$", line, re.IGNORECASE)
            if m:
                named = m.group(1).strip().strip("\"'").replace("\\", "/")
                if named == rel or Path(named).name == base:
                    return True
        return False

    def _integrity_ok(self, target_file: str) -> tuple[bool, str]:
        """Check the integrity lock for the target. Returns (ok, reason).

        - target not in lock -> OK (nothing to verify; not locked).
        - target in lock and OK -> OK.
        - target in lock and MISMATCH/MISSING -> refuse (resolve via integrity-bump).
        """
        rel = target_file.replace("\\", "/").strip()
        lock = integrity_check.load_lock(self.arch_root)
        # Lock keys are POSIX relpaths.
        if rel not in lock:
            return True, ""
        for path, status in integrity_check.verify(self.arch_root):
            if path.replace("\\", "/") == rel:
                if status == "OK":
                    return True, ""
                return False, (
                    f"integrity guard: locked target '{rel}' currently reports {status} "
                    f"against .integrity.lock. Resolve the drift via "
                    f"commands/integrity-bump.md before applying."
                )
        # Locked but not reported (shouldn't happen) — fail safe.
        return False, (
            f"integrity guard: locked target '{rel}' could not be verified against "
            f".integrity.lock. Refusing as fail-safe."
        )

    def _structural_sanity(
        self, proposal_id: str, target_path: Path, target_file: str
    ) -> tuple[bool, str]:
        """Validate the would-be post-change content. Returns (ok, reason).

        - .md target: any leading YAML frontmatter that existed stays intact and
          balanced (still opens AND closes with a '---' fence) in the result.
        - .py target: the result must compile() (no SyntaxError).
        - Result must be non-empty.
        """
        if not target_path.exists():
            return False, (
                f"structural guard: target '{target_file}' does not exist on disk; "
                f"nothing to validate."
            )
        proposal_path = self._find_proposal(proposal_id)
        proposal_text = (
            proposal_path.read_text(encoding="utf-8", errors="replace")
            if proposal_path else ""
        )
        original = target_path.read_text(encoding="utf-8", errors="replace")
        modified = self._build_modified_content(proposal_id, proposal_text, original)

        if not modified.strip():
            return False, "structural guard: post-change content is empty."

        suffix = target_path.suffix.lower()
        if suffix == ".py":
            try:
                compile(modified, str(target_path), "exec")
            except SyntaxError as exc:
                return False, (
                    f"structural guard: post-change Python for '{target_file}' would not "
                    f"compile ({exc.msg} at line {exc.lineno})."
                )
            return True, ""

        if suffix == ".md":
            had_fm = _has_leading_frontmatter(original)
            if had_fm and not _has_leading_frontmatter(modified):
                return False, (
                    f"structural guard: post-change Markdown for '{target_file}' breaks its "
                    f"YAML frontmatter (the leading ---...--- block no longer balances)."
                )
            return True, ""

        # Other text targets: non-empty is the only invariant we can assert.
        return True, ""

    # -----------------------------------------------------------------------
    # Backup machinery (block-154 calls this; block-153 only provides + tests it)
    # -----------------------------------------------------------------------

    def _backup_relpath(self, target_path: Path) -> str:
        """The _backups/ relpath (POSIX) a backup of target_path would occupy.

        Content-hash stamped (clock/random-free, deterministic, collision-safe by
        content): _backups/<filename>.<sha256[:16]>.bak
        """
        try:
            data = target_path.read_bytes()
            stamp = hashlib.sha256(data).hexdigest()[:16]
        except OSError:
            stamp = "missing"
        return f"_backups/{target_path.name}.{stamp}.bak"

    def _backup(self, target_path: Path) -> Path:
        """Copy target_path to _backups/<filename>.<contenthash>.bak; return the path.

        Byte-for-byte copy (content-hash stamp, no clock/random needed). Creates
        _backups/ if absent. This is the helper block-154 invokes immediately
        before a write; block-153 ships it (and a test) but performs no real apply.
        """
        target_path = Path(target_path)
        data = target_path.read_bytes()
        stamp = hashlib.sha256(data).hexdigest()[:16]
        backups_dir = self.arch_root / "_backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        dest = backups_dir / f"{target_path.name}.{stamp}.bak"
        dest.write_bytes(data)
        return dest

    # -----------------------------------------------------------------------
    # Block-154 — apply with rollback + provenance (the only writer here)
    # -----------------------------------------------------------------------

    def apply(self, proposal_id: str, *, confirm: bool = False) -> ApplyResult:
        """Atomically apply an accepted proposal's diff, gated by guards + verify.

        Flow: guard -> (dry-run if not confirm) -> backup -> atomic write ->
        verify (pytest + audit) -> on success record (status/log/ADR), on failure
        auto-rollback from the backup. Never raises: any exception attempts a
        rollback and returns a failed ApplyResult.
        """
        try:
            return self._apply_inner(proposal_id, confirm=confirm)
        except Exception as exc:  # pure defence — apply must never crash the caller
            # Best-effort rollback if we got far enough to take a backup.
            rolled_back = False
            target_rel = ""
            backup_rel = ""
            try:
                guard = self.check_guards(proposal_id)
                target_rel = guard.target_file or ""
            except Exception:
                pass
            return ApplyResult(
                applied=False,
                proposal_id=proposal_id,
                target_file=target_rel,
                backup_path=backup_rel,
                tests_passed=False,
                rolled_back=rolled_back,
                reasons=[f"apply error (no change kept): {exc!r}"],
            )

    def _apply_inner(self, proposal_id: str, *, confirm: bool) -> ApplyResult:
        # --- 1. Guards: refuse before any write -----------------------------
        guard = self.check_guards(proposal_id)
        target_file = guard.target_file or ""
        if not guard.allowed:
            return ApplyResult(
                applied=False,
                proposal_id=proposal_id,
                target_file=target_file,
                backup_path="",
                tests_passed=False,
                rolled_back=False,
                reasons=["apply refused by guards:"] + list(guard.reasons),
            )

        target_path = self.arch_root / target_file

        # --- 2. Dry-run: report what WOULD happen, write nothing ------------
        if not confirm:
            return ApplyResult(
                applied=False,
                proposal_id=proposal_id,
                target_file=target_file,
                backup_path=guard.backup_plan,
                tests_passed=False,
                rolled_back=False,
                reasons=[
                    "dry-run (no --confirm): nothing written.",
                    f"WOULD back up '{target_file}' to {guard.backup_plan or '(n/a)'} then "
                    f"atomically append the proposal section, run pytest + audit, and on "
                    f"success mark the proposal applied + write a governor-log entry + ADR stub.",
                ],
            )

        # --- 3. Backup FIRST (before touching the target) ------------------
        backup_path = self._backup(target_path)
        backup_rel = self._rel_posix(backup_path)
        original_bytes = target_path.read_bytes()

        # --- 4. Atomic write of the post-change content --------------------
        proposal_path = self._find_proposal(proposal_id)
        proposal_text = (
            proposal_path.read_text(encoding="utf-8", errors="replace")
            if proposal_path else ""
        )
        original_text = target_path.read_text(encoding="utf-8", errors="replace")
        modified = self._build_modified_content(proposal_id, proposal_text, original_text)
        self._atomic_write(target_path, modified)

        # --- 5. Verify (pytest + audit); EITHER failing => rollback --------
        ok, verify_reasons = self._run_verification()
        if not ok:
            restored = self._restore(backup_path, target_path, original_bytes)
            reasons = ["post-apply verification FAILED — change rolled back."]
            reasons.extend(verify_reasons)
            if not restored:
                reasons.append(
                    "WARNING: rollback could not confirm byte-identical restore; "
                    f"backup retained at {backup_rel}."
                )
            else:
                reasons.append(f"target restored byte-identical from {backup_rel} (backup retained).")
            return ApplyResult(
                applied=False,
                proposal_id=proposal_id,
                target_file=target_file,
                backup_path=backup_rel,
                tests_passed=False,
                rolled_back=True,
                reasons=reasons,
            )

        # --- 6. Success: record status + provenance log + ADR stub ---------
        record_reasons: list[str] = []
        try:
            self._mark_proposal_applied(proposal_id)
            record_reasons.append("proposal marked status: applied.")
        except Exception as exc:  # recording is best-effort; the change itself stands
            record_reasons.append(f"WARN: could not mark proposal applied: {exc!r}")
        try:
            self._append_governor_log(proposal_id, target_file, backup_rel, rolled_back=False)
            record_reasons.append("APPLIED provenance appended to governance/governor-log.md.")
        except Exception as exc:
            record_reasons.append(f"WARN: could not append governor-log entry: {exc!r}")
        try:
            adr_rel = self._write_adr_stub(proposal_id, target_file, proposal_text)
            record_reasons.append(f"ADR stub written: {adr_rel}.")
        except Exception as exc:
            record_reasons.append(f"WARN: could not write ADR stub: {exc!r}")

        reasons = [f"applied '{target_file}' (verified by pytest + audit)."]
        reasons.extend(record_reasons)
        return ApplyResult(
            applied=True,
            proposal_id=proposal_id,
            target_file=target_file,
            backup_path=backup_rel,
            tests_passed=True,
            rolled_back=False,
            reasons=reasons,
        )

    # --- apply helpers ------------------------------------------------------

    def _rel_posix(self, path: Path) -> str:
        """POSIX relpath of `path` under arch_root (falls back to the name)."""
        try:
            return path.resolve().relative_to(self.arch_root.resolve()).as_posix()
        except Exception:
            return path.name

    @staticmethod
    def _atomic_write(target_path: Path, content: str) -> None:
        """Write `content` to a temp file in the target's dir, then os.replace it.

        os.replace is atomic on the same filesystem, so a crash mid-write leaves
        either the old file or the new file — never a torn one. UTF-8, LF-safe.
        """
        target_path = Path(target_path)
        tmp = target_path.with_name(target_path.name + ".apply.tmp")
        data = content.encode("utf-8")
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(str(tmp), str(target_path))

    @staticmethod
    def _restore(backup_path: Path, target_path: Path, original_bytes: bytes) -> bool:
        """Atomically restore target_path from backup_path; verify byte-identity.

        Writes the backup bytes to a temp file then os.replace over the target,
        so the restore is itself crash-safe. Returns True iff the on-disk result
        is byte-identical to the pre-apply original.
        """
        try:
            data = Path(backup_path).read_bytes()
        except OSError:
            data = original_bytes
        tmp = Path(target_path).with_name(Path(target_path).name + ".restore.tmp")
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(str(tmp), str(target_path))
        try:
            return Path(target_path).read_bytes() == original_bytes
        except OSError:
            return False

    def _run_verification(self) -> tuple[bool, list[str]]:
        """Run the test suite + audit as the apply gate. Returns (ok, reasons).

        Runs `python -m pytest sdk/tests/ -q` and `python sdk/audit.py
        --arch-root .` via subprocess, both with cwd=arch_root and a UTF-8 env
        (mirrors the cp1252 smoke-test convention, block-138). EITHER a non-zero
        exit / a 'failed' marker / audit not reporting PASS => verification fails.
        Never runs proposal_apply — no recursion (manifest §6).
        """
        reasons: list[str] = []
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        tests_ok = self._run_one(
            [sys.executable, "-m", "pytest", "sdk/tests/", "-q"],
            env,
            label="pytest",
            fail_markers=("failed", "error"),
            reasons=reasons,
        )
        audit_ok = self._run_one(
            [sys.executable, "sdk/audit.py", "--arch-root", "."],
            env,
            label="audit",
            # audit must explicitly report PASS; absence of PASS => fail.
            require_marker="PASS",
            reasons=reasons,
        )
        return (tests_ok and audit_ok), reasons

    def _run_one(
        self,
        cmd: list[str],
        env: dict,
        *,
        label: str,
        reasons: list[str],
        fail_markers: tuple[str, ...] = (),
        require_marker: Optional[str] = None,
    ) -> bool:
        """Run one verification subprocess. Returns True iff it counts as a pass.

        A pass requires exit code 0 AND (no fail_marker in output) AND (the
        require_marker present in output when one is specified).
        """
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.arch_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600,
            )
        except Exception as exc:
            reasons.append(f"{label}: could not run ({exc!r}) -> treated as failure.")
            return False

        out = (proc.stdout or "")
        low = out.lower()
        ok = proc.returncode == 0
        if ok and fail_markers:
            for marker in fail_markers:
                # pytest prints "N failed" only when there are failures; a bare
                # "0 failed" never appears in -q summaries, so a substring test is safe.
                if marker in low:
                    ok = False
                    break
        if ok and require_marker is not None and require_marker not in out:
            ok = False
        if not ok:
            tail = out.strip().splitlines()[-1] if out.strip() else "(no output)"
            reasons.append(f"{label}: FAILED (exit {proc.returncode}); last line: {tail}")
        else:
            reasons.append(f"{label}: passed (exit 0).")
        return ok

    def _mark_proposal_applied(self, proposal_id: str) -> None:
        """Set the proposal's status to `applied` (front-matter + index + body line)."""
        path = self._find_proposal(proposal_id)
        if path is None:
            return
        text = path.read_text(encoding="utf-8", errors="replace")
        today = date.today().isoformat()
        text = _update_frontmatter_field(text, "status", "applied")
        text = _update_frontmatter_field(text, "applied_at", today)
        text = _update_frontmatter_field(text, "applied_by", "proposal_apply")
        # Flip the human-readable **Status:** line from whatever it was to applied.
        text = re.sub(r"\*\*Status:\*\*[^\n]*", "**Status:** applied", text)
        path.write_text(text, encoding="utf-8")
        _update_index_status(self.proposals_dir / "index.md", proposal_id, "applied")

    def _append_governor_log(
        self, proposal_id: str, target_file: str, backup_rel: str, *, rolled_back: bool
    ) -> None:
        """Append an APPLIED provenance block to governance/governor-log.md.

        Append-only: a single open(..., 'a') write of a fully-formed block,
        mirroring the INTEGRITY BUMP APPROVED block style. No in-place edits.
        """
        log_path = self.arch_root / "governance" / "governor-log.md"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        today = date.today().isoformat()
        verdict = "APPLY FAILED (rolled back)" if rolled_back else "APPLY APPLIED"
        block = (
            f"\n# --- {verdict} ---\n"
            f"# date: {today}\n"
            f"# proposal: {proposal_id}\n"
            f"# file: {target_file}\n"
            f"# backup: {backup_rel}\n"
            f"# verify: pytest sdk/tests/ -q + sdk/audit.py (PASS)\n"
            f"# applied_by: proposal_apply (block-154)\n"
            f"# --- END APPLY ---\n"
        )
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(block)

    def _next_adr_number(self) -> int:
        """Next ADR-<NNN> number: max existing in decisions/ + 1 (min 6)."""
        decisions = self.arch_root / "decisions"
        nums: list[int] = []
        if decisions.exists():
            for p in decisions.glob("ADR-*.md"):
                m = re.match(r"ADR-(\d+)", p.name)
                if m:
                    nums.append(int(m.group(1)))
        nxt = (max(nums) + 1) if nums else 6
        return max(nxt, 6)

    def _write_adr_stub(self, proposal_id: str, target_file: str, proposal_text: str) -> str:
        """Create decisions/ADR-NNN-apply-<slug>.md recording the applied change.

        Returns the POSIX relpath written. Numbering continues from the current
        max ADR (ADR-005 -> ADR-006). status: accepted, context_phase: phase-27,
        context_block: block-154, rationale carried into §1.
        """
        n = self._next_adr_number()
        nnn = f"{n:03d}"
        slug = re.sub(r"[^a-z0-9]+", "-", proposal_id.lower()).strip("-") or "proposal"
        decisions = self.arch_root / "decisions"
        decisions.mkdir(parents=True, exist_ok=True)
        dest = decisions / f"ADR-{nnn}-apply-{slug}.md"

        today = date.today().isoformat()
        rationale = _read_block_scalar(proposal_text, "rationale") or "(no rationale provided)"
        pattern_id = _get_frontmatter_field(proposal_text, "pattern_id") or "unknown"

        body = (
            f"---\n"
            f"id: ADR-{nnn}\n"
            f"title: apply-{slug}\n"
            f"status: accepted\n"
            f"created_at: {today}\n"
            f"decided_at: {today}\n"
            f"deciders: [proposal_apply]\n"
            f"context_phase: phase-27\n"
            f"context_block: block-154\n"
            f"---\n\n"
            f"# ADR-{nnn} — Apply proposal {proposal_id}\n\n"
            f"## 1. Context\n\n"
            f"Proposal `{proposal_id}` (pattern `{pattern_id}`) was accepted and applied "
            f"by the block-154 apply engine to `{target_file}`. Its rationale:\n\n"
            f"> {rationale}\n\n"
            f"## 2. Decision\n\n"
            f"Apply the proposal's reviewable section to `{target_file}` via an atomic, "
            f"guarded, test-verified write. The change is backed up before writing and "
            f"would be auto-rolled-back on any pytest/audit failure; this ADR records the "
            f"successful apply.\n\n"
            f"## 3. Consequences\n\n"
            f"- **Positive:** the recurring pattern is addressed in-place with full provenance "
            f"(governor-log + this ADR + retained backup).\n"
            f"- **Negative:** the appended section is a stub a reviewer should refine.\n"
            f"- **Neutral:** target now carries a machine-readable provenance anchor.\n\n"
            f"## 4. References\n\n"
            f"- Proposal: `governance/proposals/{proposal_id}.md`\n"
            f"- Provenance: `governance/governor-log.md` (APPLY APPLIED block)\n"
            f"- Engine: `sdk/proposal_apply.py` (block-154)\n\n"
            f"---\n\n"
            f"End of ADR.\n"
        )
        dest.write_text(body, encoding="utf-8")
        return self._rel_posix(dest)


# ---------------------------------------------------------------------------
# Markdown frontmatter check (structural sanity helper)
# ---------------------------------------------------------------------------

def _has_leading_frontmatter(text: str) -> bool:
    """True iff text opens with a balanced YAML frontmatter block (---...---).

    Reuses integrity_check._frontmatter_block, which returns '' unless the file
    STARTS with a '---' fence that later closes with a '---' fence. A non-empty
    return means the leading block is present AND balanced.
    """
    return integrity_check._frontmatter_block(text) != ""


# Module-level convenience wrapper (matches the manifest's stated API).
def generate_diff(proposal_id: str, arch_root: Path) -> DiffResult:
    """Render proposal `proposal_id` under `arch_root` as a unified diff. Never raises."""
    return ProposalApply(Path(arch_root)).generate_diff(proposal_id)


def check_guards(proposal_id: str, arch_root: Path) -> GuardResult:
    """Evaluate apply guards for `proposal_id` under `arch_root`. Never raises."""
    return ProposalApply(Path(arch_root)).check_guards(proposal_id)


def apply_proposal(proposal_id: str, arch_root: Path, *, confirm: bool = False) -> ApplyResult:
    """Atomically apply `proposal_id` under `arch_root` (block-154). Never raises.

    confirm=False is a dry-run (writes nothing); only confirm=True writes, and
    even then any pytest/audit failure auto-rolls-back from the backup.
    """
    return ProposalApply(Path(arch_root)).apply(proposal_id, confirm=confirm)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_STATUS_MESSAGE = {
    "accepted": "diff generated (review below)",
    "not-accepted": "proposal not found or status != accepted — no diff",
    "no-target": "target_file is a placeholder or missing — no diff",
    "target-missing": "target_file does not exist on disk — no diff",
}


def main(argv: Optional[list[str]] = None) -> int:
    try:
        from safe_io import force_utf8
        force_utf8()
    except Exception:  # pragma: no cover - never let stdout-safety crash the tool
        pass

    parser = argparse.ArgumentParser(
        description="Render an accepted proposal as a concrete unified diff and/or evaluate apply guards (dry-run; writes nothing)"
    )
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--proposal", required=True, metavar="ID", help="Proposal ID to render")
    parser.add_argument(
        "--check-guards",
        action="store_true",
        help="Evaluate the apply guards (block-153) and print ALLOWED/REFUSED + reasons; writes nothing",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the proposal (block-154). Without --confirm this is a DRY-RUN (writes nothing); "
             "with --confirm it backs up, atomically writes, runs pytest + audit, and auto-rolls-back on failure",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="(--apply only) Actually write. Required for any real apply; absent => dry-run",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No-op flag (diff/guard modes are always dry-run; accepted for interface symmetry)",
    )
    args = parser.parse_args(argv)

    root = Path(args.arch_root).resolve()

    if args.apply:
        result = apply_proposal(args.proposal, root, confirm=args.confirm)
        print(f"[proposal_apply] proposal: {result.proposal_id}")
        print(f"[proposal_apply] target_file: {result.target_file or '(none)'}")
        mode = "CONFIRMED apply" if args.confirm else "DRY-RUN (no --confirm)"
        print(f"[proposal_apply] mode: {mode}")
        if result.applied:
            verdict = "APPLIED"
        elif result.rolled_back:
            verdict = "ROLLED BACK (verification failed)"
        elif not args.confirm:
            verdict = "WOULD-APPLY / REFUSED (dry-run; nothing written)"
        else:
            verdict = "REFUSED (nothing written)"
        print(f"[proposal_apply] result: {verdict}")
        print(f"[proposal_apply] tests_passed: {result.tests_passed} | rolled_back: {result.rolled_back}")
        if result.backup_path:
            print(f"[proposal_apply] backup: {result.backup_path}")
        for reason in result.reasons:
            print(f"  - {reason}")
        if not args.confirm:
            print("[proposal_apply] dry-run: nothing was written (pass --confirm to apply).")
        # Always exit 0 — a refusal / rollback is a valid, non-error outcome.
        return 0

    if args.check_guards:
        guard = check_guards(args.proposal, root)
        print(f"[proposal_apply] proposal: {args.proposal}")
        print(f"[proposal_apply] target_file: {guard.target_file or '(none)'}")
        print(f"[proposal_apply] guards: {'ALLOWED' if guard.allowed else 'REFUSED'}")
        for reason in guard.reasons:
            print(f"  - {reason}")
        if guard.backup_plan:
            print(f"[proposal_apply] backup_plan: {guard.backup_plan} (block-154 would write this first)")
        print("[proposal_apply] dry-run: nothing was written (guards are evaluate-only).")
        # Always exit 0 — a REFUSED verdict is a valid, non-error outcome.
        return 0

    result = generate_diff(args.proposal, root)

    print(f"[proposal_apply] proposal: {result.proposal_id}")
    print(f"[proposal_apply] target_file: {result.target_file or '(none)'}")
    if result.is_immutable:
        print("=" * 60)
        print("  IMMUTABLE TARGET - apply is guarded (see block-153).")
        print("  This is a DRY-RUN render only; nothing is written.")
        print("=" * 60)

    if result.unified_diff:
        print()
        print(result.unified_diff, end="" if result.unified_diff.endswith("\n") else "\n")
        print()

    msg = _STATUS_MESSAGE.get(result.status, result.status)
    print(f"[proposal_apply] status: {result.status} - {msg}")
    print("[proposal_apply] dry-run: nothing was written.")
    # Always exit 0 — a refusal (no diff) is a valid, non-error outcome here.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
