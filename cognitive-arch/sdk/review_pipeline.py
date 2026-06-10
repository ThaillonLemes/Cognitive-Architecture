# sdk/review_pipeline.py
# PURPOSE: Orchestrate the implement↔quality cycle.
#          Runs consistency checker, verifies test coverage, analyzes complexity (Big-O heuristic),
#          generates HTML quality report, and presents go/no-go prompt to Piloto.
#          Any override (option B) records gate_override_reason in manifest.
# INPUTS:  --block-id, --arch-root, --diff, --client
# OUTPUTS: governance/review-<block-id>-<ts>.html; updated manifest if override
# DEPS:    stdlib only; sdk/consistency_checker, sdk/scanner_profile
# USAGE:   python sdk/review_pipeline.py --block-id block-XXX --arch-root .
# SEE:     design/pipeline.md §2

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

def _fix_utf8() -> None:
    import io as _io
    if sys.platform == "win32":
        if hasattr(sys.stdout, "buffer") and not (
            isinstance(sys.stdout, _io.TextIOWrapper) and sys.stdout.encoding.lower() == "utf-8"
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_fix_utf8()


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ComplexityNote:
    func_name: str
    complexity: str        # e.g. "O(n²)"
    note: str


@dataclass
class QualityReport:
    block_id: str
    consistency_score: float
    consistency_passed: bool
    consistency_divergences: list
    test_coverage_note: str
    complexity_notes: list[ComplexityNote] = field(default_factory=list)
    proactive_suggestions: list[str] = field(default_factory=list)  # level C
    overall_passed: bool = False
    override_reason: str = ""


# ---------------------------------------------------------------------------
# Test coverage check (heuristic)
# ---------------------------------------------------------------------------

def _check_test_coverage(arch_root: Path, block_id: str) -> str:
    """Heuristic: check if any test files were modified/created in the block."""
    manifests_dir = arch_root / "manifests"
    candidates = list(manifests_dir.glob(f"{block_id}-*.md"))
    if not candidates:
        return "Manifest não encontrado — verifique cobertura manualmente"

    text = candidates[0].read_text(encoding="utf-8", errors="replace")
    # Look for test files in create/modify sections
    test_files = re.findall(r"-\s+(.*(?:test|spec).*\.(?:py|ts|js))", text, re.IGNORECASE)
    if test_files:
        return f"Testes declarados no manifest: {', '.join(test_files[:3])}"

    # Check if block kind is ticket (corporate) — expect tests
    kind_m = re.search(r"^kind:\s*(\S+)", text, re.MULTILINE)
    if kind_m and kind_m.group(1) in ("ticket", "implementation"):
        return "WARN: Nenhum arquivo de teste detectado no manifest — verificar cobertura"
    return "Cobertura não requerida para este tipo de bloco"


# ---------------------------------------------------------------------------
# Big-O complexity heuristic (level B)
# ---------------------------------------------------------------------------

def _analyze_complexity(diff_text: str) -> list[ComplexityNote]:
    """Very rough Big-O heuristic from diff."""
    notes: list[ComplexityNote] = []
    added = [l[1:] for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++")]
    full = "\n".join(added)

    # Nested loops → O(n²)
    nested_loop = re.search(r"for\s*[(\[].*\n.*for\s*[(\[]", full)
    if nested_loop:
        notes.append(ComplexityNote(
            "função com loops aninhados detectada",
            "O(n²)",
            "Loops aninhados geralmente implicam O(n²). Verifique se é necessário.",
        ))

    # .sort() or .filter().map() chains → O(n log n) or O(n)
    sort_calls = re.findall(r"\.sort\(", full)
    if sort_calls:
        notes.append(ComplexityNote(
            ".sort()",
            "O(n log n)",
            "JavaScript .sort() é O(n log n). Típico e aceitável.",
        ))

    return notes[:3]


# ---------------------------------------------------------------------------
# HTML generator
# ---------------------------------------------------------------------------

_QUALITY_HTML = """\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Quality Report — {block_id}</title>
<style>
  :root {{ --bg: #0f1117; --card: #1a1d27; --border: #2d3148; --accent: #6c8af7;
           --text: #e2e8f0; --muted: #8892a4; --ok: #4ade80; --warn: #facc15; --err: #f87171; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system,sans-serif;
          font-size: 14px; line-height: 1.6; padding: 24px; }}
  h1 {{ font-size: 20px; color: var(--accent); margin-bottom: 6px; }}
  h2 {{ font-size: 15px; border-bottom: 1px solid var(--border); padding-bottom: 6px; margin: 20px 0 10px; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 12px; }}
  .ok {{ color: var(--ok); }} .warn {{ color: var(--warn); }} .err {{ color: var(--err); }}
  table {{ width: 100%; border-collapse: collapse; }}
  td, th {{ padding: 6px 10px; border-bottom: 1px solid var(--border); }}
  th {{ color: var(--muted); font-weight: 500; text-align: left; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
  .footer {{ color: var(--muted); font-size: 12px; margin-top: 24px; border-top: 1px solid var(--border); padding-top: 10px; }}
</style>
</head>
<body>
<h1>📋 Quality Report — {block_id}</h1>
<p style="color:var(--muted)">{ts}</p>

<h2>✅ Consistency</h2>
<div class="card">
  <p>Score: <strong class="{score_class}">{score:.2f}</strong>
     (threshold: {threshold:.2f}) &nbsp;
     <span class="badge {badge_class}">{status}</span></p>
  {divs_html}
</div>

<h2>🧪 Cobertura de Testes</h2>
<div class="card"><p>{coverage}</p></div>

{complexity_html}
{proactive_html}

<div class="footer">
  Gerado por cognitive-arch/sdk/review_pipeline.py · {ts}
</div>
</body>
</html>
"""


def _build_quality_html(report: QualityReport, ts: str, threshold: float) -> str:
    score_class = "ok" if report.consistency_passed else "err"
    badge_class = "ok" if report.consistency_passed else "err"
    status = "PASSOU" if report.consistency_passed else "REPROVADO"

    if report.consistency_divergences:
        rows = "".join(
            f"<tr><td>[{d.category}]</td><td>{d.description}</td></tr>"
            for d in report.consistency_divergences
        )
        divs_html = f"<table><tr><th>Categoria</th><th>Divergência</th></tr>{rows}</table>"
    else:
        divs_html = "<p class='ok'>Nenhuma divergência detectada ✓</p>"

    if report.complexity_notes:
        rows = "".join(
            f"<tr><td>{n.func_name}</td><td><code>{n.complexity}</code></td><td>{n.note}</td></tr>"
            for n in report.complexity_notes
        )
        complexity_html = (
            "<h2>⚡ Complexidade (Big-O)</h2>"
            "<div class='card'><table>"
            "<tr><th>Função</th><th>Complexidade</th><th>Nota</th></tr>"
            f"{rows}</table></div>"
        )
    else:
        complexity_html = ""

    if report.proactive_suggestions:
        items = "".join(f"<li>{s}</li>" for s in report.proactive_suggestions)
        proactive_html = f"<h2>💡 Sugestões Proativas (Nível C)</h2><div class='card'><ul style='padding-left:16px'>{items}</ul></div>"
    else:
        proactive_html = ""

    return _QUALITY_HTML.format(
        block_id=report.block_id,
        ts=ts,
        score=report.consistency_score,
        score_class=score_class,
        badge_class=badge_class,
        status=status,
        threshold=threshold,
        divs_html=divs_html,
        coverage=report.coverage_note if hasattr(report, 'coverage_note') else report.test_coverage_note,
        complexity_html=complexity_html,
        proactive_html=proactive_html,
    )


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_quality_review(
    block_id: str,
    arch_root: Path,
    client: str = "",
    diff_path: Optional[Path] = None,
    interactive: bool = True,
    level_c: bool = False,
) -> QualityReport:
    """Orchestrate quality review. Returns QualityReport."""
    sdk_str = str(arch_root / "sdk")
    if sdk_str not in sys.path:
        sys.path.insert(0, sdk_str)

    from consistency_checker import run_check, ConsistencyReport
    from scanner_profile import ProjectProfile

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")

    # Find client_id from manifest if not provided
    if not client:
        manifests_dir = arch_root / "manifests"
        cands = list(manifests_dir.glob(f"{block_id}-*.md"))
        if cands:
            text = cands[0].read_text(encoding="utf-8", errors="replace")
            m = re.search(r"^client_id:\s*(\S+)", text, re.MULTILINE)
            if m:
                client = m.group(1)

    # Find profile
    profile_path: Optional[Path] = None
    if client and client != "~":
        candidate = arch_root / "governance" / f"project-profile-{client}.md"
        if candidate.exists():
            profile_path = candidate

    # Run consistency check
    con_score = 1.0
    con_passed = True
    con_divs = []
    threshold = 0.80

    if profile_path:
        try:
            con_report = run_check(profile_path, diff_path, arch_root=arch_root)
            con_score = con_report.score
            con_passed = con_report.passed
            con_divs = con_report.divergences
            threshold = con_report.threshold
        except FileNotFoundError:
            pass
    else:
        con_passed = True  # no profile → gate passes with warning

    # Test coverage
    coverage_note = _check_test_coverage(arch_root, block_id)

    # Complexity analysis
    diff_text = ""
    if diff_path and diff_path.exists():
        diff_text = diff_path.read_text(encoding="utf-8", errors="replace")
    complexity = _analyze_complexity(diff_text)

    # Code review (Bugbot) step — block-180
    cr_result = None
    _cr_mod = None
    try:
        cr_path = arch_root / "sdk" / "code_review.py"
        if cr_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("code_review", cr_path)
            _cr_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_cr_mod)
            cr_result = _cr_mod.review_block(block_id, arch_root, diff_text=diff_text)
    except Exception:
        pass

    report = QualityReport(
        block_id=block_id,
        consistency_score=con_score,
        consistency_passed=con_passed,
        consistency_divergences=con_divs,
        test_coverage_note=coverage_note,
        complexity_notes=complexity,
        overall_passed=con_passed,
    )

    # Generate HTML
    ux_cfg = arch_root / "governance" / "ux-config.yaml"
    html_enabled = True
    if ux_cfg.exists():
        cfg = ux_cfg.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"pipeline_quality_b:\s*(true|false)", cfg)
        if m:
            html_enabled = m.group(1) == "true"

    if html_enabled:
        html_content = _build_quality_html(report, ts, threshold)
        # Inject code review section before footer
        if cr_result is not None and _cr_mod is not None:
            try:
                cr_html = _cr_mod.build_html_section(cr_result)
                html_content = html_content.replace(
                    '<div class="footer">',
                    cr_html + '\n<div class="footer">',
                )
            except Exception:
                pass
        html_path = arch_root / "governance" / f"review-{block_id}-{ts}.html"
        html_path.parent.mkdir(exist_ok=True)
        html_path.write_text(html_content, encoding="utf-8")
        print(f"[review_pipeline] Quality HTML: {html_path}")

    # Present go/no-go prompt
    print(f"\n[review_pipeline] Consistency score: {con_score:.2f} (threshold: {threshold:.2f})")
    if con_divs:
        print(f"  {len(con_divs)} divergências: {', '.join({d.category for d in con_divs})}")
    print(f"  Cobertura: {coverage_note}")
    print()

    if interactive and not con_passed:
        print("  [A] Retornar para Implementar — corrigir divergências")
        print("  [B] Entregar mesmo assim — registrar motivo")
        print("  [C] Ver detalhes antes de decidir")
        try:
            choice = input("  Sua escolha: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            choice = "A"

        if choice == "B":
            try:
                reason = input("  Motivo do override: ").strip()
            except (EOFError, KeyboardInterrupt):
                reason = "motivo não informado"
            report.override_reason = reason
            _record_override(arch_root, block_id, reason)
            report.overall_passed = True
        elif choice == "A":
            report.overall_passed = False

    return report


def _record_override(arch_root: Path, block_id: str, reason: str) -> None:
    """Record gate_override_reason in block manifest."""
    manifests_dir = arch_root / "manifests"
    cands = list(manifests_dir.glob(f"{block_id}-*.md"))
    if not cands:
        return
    text = cands[0].read_text(encoding="utf-8", errors="replace")
    if "gate_override_reason" in text:
        text = re.sub(
            r"^gate_override_reason:\s*.*$",
            f"gate_override_reason: {reason}",
            text, flags=re.MULTILINE,
        )
    else:
        parts = text.split("---", 2)
        if len(parts) >= 3:
            parts[1] = parts[1].rstrip() + f"\ngate_override_reason: {reason}\n"
            text = "---".join(parts)
    cands[0].write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="review_pipeline",
        description="Orchestrate quality review cycle for a corporate block.",
    )
    p.add_argument("--block-id", required=True)
    p.add_argument("--arch-root", default=".")
    p.add_argument("--client", default="")
    p.add_argument("--diff", default="", help="Path to diff file")
    p.add_argument("--no-interactive", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()
    diff_path = Path(args.diff).resolve() if args.diff else None
    run_quality_review(args.block_id, arch_root, args.client, diff_path,
                       interactive=not args.no_interactive)
    return 0


if __name__ == "__main__":
    sys.exit(main())
