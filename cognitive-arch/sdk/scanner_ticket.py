# sdk/scanner_ticket.py
# PURPOSE: Ticket-directed scan entry point. Given ticket text, infers affected area,
#          shows confirmation to Piloto, then runs targeted L2/L3 scan on that area.
# INPUTS:  --ticket <text>, --client <name>, --target-repo <path>, --arch-root <path>
# OUTPUTS: Partial profile update (L2/L3 for inferred area) + HTML
# DEPS:    stdlib only; sdk/scanner_adaptive, sdk/codebase_scanner
# USAGE:   python sdk/scanner_ticket.py --ticket "fix JWT refresh bug" --client acme --target-repo /path
# SEE:     design/scanner.md §5 (--ticket flag)

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _fix_utf8() -> None:
    import io as _io
    if sys.platform == "win32":
        if hasattr(sys.stdout, "buffer") and not (
            isinstance(sys.stdout, _io.TextIOWrapper) and sys.stdout.encoding.lower() == "utf-8"
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


_fix_utf8()


def scan_for_ticket(
    ticket_text: str,
    target_repo: Path,
    arch_root: Path,
    client: str,
    interactive: bool = True,
    no_html: bool = False,
) -> dict:
    """Infer area from ticket, confirm with Piloto, run L2+L3 scan on area."""
    sdk_str = str(arch_root / "sdk")
    if sdk_str not in sys.path:
        sys.path.insert(0, sdk_str)

    from scanner_adaptive import infer_area_from_ticket, confirm_area
    from codebase_scanner import run_scan

    print(f"[scanner_ticket] Analisando ticket: {ticket_text[:80]}")

    area = infer_area_from_ticket(ticket_text, target_repo)
    confirmed_area = confirm_area(area, ticket_text, interactive=interactive)

    if confirmed_area is None:
        print("[scanner_ticket] Scan cancelado.")
        return {}

    print(f"[scanner_ticket] Rodando L2+L3 em: {confirmed_area}")
    result = run_scan(
        target_repo=target_repo,
        level="L2+L3",
        arch_root=arch_root,
        client=client,
        context=f"ticket: {ticket_text[:100]}",
        area=confirmed_area,
        no_html=no_html,
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="scanner_ticket",
        description="Ticket-directed scan: infer area, confirm, scan L2+L3.",
    )
    p.add_argument("--ticket", required=True, help="Free-text ticket description")
    p.add_argument("--client", required=True, help="Client name")
    p.add_argument("--target-repo", required=True, help="Path to target repo")
    p.add_argument("--arch-root", default=".", help="Cognitive-arch root")
    p.add_argument("--no-html", action="store_true", help="Suppress HTML output")
    p.add_argument("--no-interactive", action="store_true", help="Skip confirmation prompts")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()
    target_repo = Path(args.target_repo).resolve()

    if not target_repo.exists():
        print(f"[scanner_ticket] ERROR: --target-repo not found: {target_repo}")
        return 1

    scan_for_ticket(
        args.ticket, target_repo, arch_root, args.client,
        interactive=not args.no_interactive, no_html=args.no_html,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
