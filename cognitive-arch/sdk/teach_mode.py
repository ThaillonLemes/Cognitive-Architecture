# sdk/teach_mode.py
# PURPOSE: Teach mode — always mandatory before closing a corporate ticket block.
#          Generates 3 HTMLs by audience (technical, team, learning) + text exports.
#          Abstraction dial (leigo/iniciante/técnico) configured in ux-config.yaml.
#          Can loopback to implementing if Piloto identifies a correction.
# INPUTS:  --block-id, --arch-root, --level (ad-hoc override)
# OUTPUTS: governance/teach-<block-id>-technical.html, -team.html, -learning.html
#          governance/teach-<block-id>-<audience>.txt (text exports)
# DEPS:    stdlib only
# USAGE:   python sdk/teach_mode.py --block-id block-XXX --arch-root .
# SEE:     design/pipeline.md §3

from __future__ import annotations

import argparse
import re
import sys
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
# Abstraction levels
# ---------------------------------------------------------------------------

ABSTRACTION_LEVELS = ("leigo", "iniciante", "tecnico")


def _read_abstraction_level(arch_root: Path) -> str:
    cfg = arch_root / "governance" / "ux-config.yaml"
    if cfg.exists():
        text = cfg.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^abstraction_level:\s*(\S+)", text, re.MULTILINE)
        if m and m.group(1) in ABSTRACTION_LEVELS:
            return m.group(1)
    return "tecnico"


def _read_teach_html_config(arch_root: Path) -> dict[str, bool]:
    defaults = {"technical": True, "team": True, "learning": True}
    cfg = arch_root / "governance" / "ux-config.yaml"
    if not cfg.exists():
        return defaults
    text = cfg.read_text(encoding="utf-8", errors="replace")
    for key in defaults:
        m = re.search(rf"^\s+{key}:\s*(true|false)", text, re.MULTILINE)
        if m:
            defaults[key] = m.group(1) == "true"
    return defaults


# ---------------------------------------------------------------------------
# Block meta reader
# ---------------------------------------------------------------------------

def _read_block_meta(arch_root: Path, block_id: str) -> dict[str, str]:
    """Read key fields from manifest and retro for teach context."""
    meta: dict[str, str] = {"block_id": block_id}

    manifests_dir = arch_root / "manifests"
    cands = list(manifests_dir.glob(f"{block_id}-*.md"))
    if cands:
        text = cands[0].read_text(encoding="utf-8", errors="replace")
        for key in ("ticket_id", "acceptance_criteria", "client_id", "kind", "size"):
            m = re.search(rf"^{key}:\s*(.+)", text, re.MULTILINE)
            if m:
                meta[key] = m.group(1).strip()

    # Try retro for summary
    retros = list((arch_root / "blocks").glob(f"{block_id}-*.md"))
    retros = [r for r in retros if "LOG" not in r.name.upper() and "retro" not in r.name.lower()]
    if retros:
        rtext = retros[0].read_text(encoding="utf-8", errors="replace")
        sm = re.search(r"## 1\. Summary\n+(.+?)(?:\n## |\Z)", rtext, re.DOTALL)
        if sm:
            meta["summary"] = sm.group(1).strip()[:500]

    return meta


# ---------------------------------------------------------------------------
# HTML builders per audience
# ---------------------------------------------------------------------------

_BASE_STYLE = """
  :root { --bg: #0f1117; --card: #1a1d27; --border: #2d3148; --text: #e2e8f0; --muted: #8892a4; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system,sans-serif;
         font-size: 14px; line-height: 1.6; padding: 24px; max-width: 760px; }
  h1 { font-size: 20px; color: #6c8af7; margin-bottom: 6px; }
  h2 { font-size: 15px; border-bottom: 1px solid var(--border); padding-bottom: 6px; margin: 20px 0 10px; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px;
          padding: 16px; margin-bottom: 12px; }
  .label { color: var(--muted); font-size: 12px; text-transform: uppercase; }
  .footer { color: var(--muted); font-size: 12px; margin-top: 24px; border-top: 1px solid var(--border); padding-top: 10px; }
"""


def _build_technical_html(meta: dict, level: str, ts: str) -> str:
    block_id = meta.get("block_id", "?")
    summary = meta.get("summary", "Consultar retrospectiva do bloco.")
    ticket = meta.get("ticket_id", "~")
    client = meta.get("client_id", "~")
    size = meta.get("size", "?")

    if level == "leigo":
        content = f"""
<p>O que foi feito neste bloco pode ser resumido assim:</p>
<div class="card">{summary}</div>
<p>Este trabalho foi solicitado pelo ticket <strong>{ticket}</strong>.</p>
"""
    elif level == "iniciante":
        content = f"""
<p>Bloco <code>{block_id}</code> implementou mudanças para o ticket <strong>{ticket}</strong>.</p>
<div class="card"><strong>O que foi feito:</strong><br>{summary}</div>
<p>Tamanho do bloco: {size}. Cliente: {client}.</p>
"""
    else:  # tecnico
        content = f"""
<p>Bloco <code>{block_id}</code> · Ticket: <code>{ticket}</code> · Cliente: <code>{client}</code> · Size: {size}</p>
<h2>O que foi implementado</h2>
<div class="card">{summary}</div>
<h2>Decisões arquiteturais</h2>
<div class="card">
  <p class="label">Para revisar:</p>
  <p>Consulte a seção Decisions na retrospectiva do bloco em <code>blocks/{block_id}-*.md</code></p>
</div>
"""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Teach — {block_id} — Technical</title>
<style>{_BASE_STYLE}</style></head>
<body>
<h1>🎓 Teach Mode — Technical</h1>
<p style="color:var(--muted)">Para: Senior / PR Description · {ts}</p>
{content}
<div class="footer">cognitive-arch/sdk/teach_mode.py · level: {level}</div>
</body></html>
"""


def _build_team_html(meta: dict, level: str, ts: str) -> str:
    block_id = meta.get("block_id", "?")
    summary = meta.get("summary", "Consultar retrospectiva do bloco.")
    ticket = meta.get("ticket_id", "~")

    if level == "leigo":
        content = f"""
<p>A mudança feita neste bloco:</p>
<div class="card">{summary}</div>
<p>Não afeta diretamente o trabalho de outros devs.</p>
"""
    else:
        content = f"""
<h2>O que mudou (para o time)</h2>
<div class="card">{summary}</div>
<h2>Impacto nos outros</h2>
<div class="card">
  <p>Ticket: <code>{ticket}</code></p>
  <p>Verificar se há dependências cruzadas antes de fazer merge.</p>
</div>
"""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Teach — {block_id} — Team</title>
<style>{_BASE_STYLE}</style></head>
<body>
<h1>🎓 Teach Mode — Team</h1>
<p style="color:var(--muted)">Para: Standup / Reunião · {ts}</p>
{content}
<div class="footer">cognitive-arch/sdk/teach_mode.py · level: {level}</div>
</body></html>
"""


def _build_learning_html(meta: dict, level: str, ts: str) -> str:
    block_id = meta.get("block_id", "?")
    summary = meta.get("summary", "Consultar retrospectiva do bloco.")
    ticket = meta.get("ticket_id", "~")

    content = f"""
<h2>O que foi feito</h2>
<div class="card">{summary}</div>
<h2>O que aprendi</h2>
<div class="card">
  <p>Preencha após reflexão:</p>
  <ul style="padding-left:16px;margin-top:8px">
    <li>Por que escolhi esta abordagem?</li>
    <li>O que faria diferente da próxima vez?</li>
    <li>Que padrão novo aprendi nesta codebase?</li>
  </ul>
</div>
<h2>Perguntas para testar o entendimento</h2>
<div class="card">
  <ul style="padding-left:16px">
    <li>Consigo explicar o que o ticket pediu em 1 frase?</li>
    <li>Consigo explicar minha solução técnica em 2 frases?</li>
    <li>Consigo explicar o impacto para o gestor em 1 frase?</li>
  </ul>
</div>
"""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Teach — {block_id} — Learning</title>
<style>{_BASE_STYLE}</style></head>
<body>
<h1>🎓 Teach Mode — Learning</h1>
<p style="color:var(--muted)">Para: Revisão pessoal · {ts}</p>
{content}
<div class="footer">cognitive-arch/sdk/teach_mode.py · level: {level}</div>
</body></html>
"""


# ---------------------------------------------------------------------------
# Text exports
# ---------------------------------------------------------------------------

def _build_text_export(meta: dict, audience: str, level: str) -> str:
    block_id = meta.get("block_id", "?")
    summary = meta.get("summary", "")
    ticket = meta.get("ticket_id", "~")
    client = meta.get("client_id", "~")

    if audience == "technical":
        return (
            f"## Teach — {block_id} (Technical)\n"
            f"Ticket: {ticket} · Client: {client}\n\n"
            f"**O que foi feito:**\n{summary or '[preencher da retro]'}\n"
        )
    elif audience == "team":
        return (
            f"**[{block_id}]** Ticket {ticket}: {summary[:100] or '[preencher]'}...\n"
            f"Verificar dependências antes do merge."
        )
    else:  # learning
        return (
            f"Bloco {block_id} · Ticket {ticket}\n"
            f"O que foi feito: {summary[:200] or '[preencher da retro]'}\n"
            f"O que aprendi: [preencher após reflexão]\n"
        )


# ---------------------------------------------------------------------------
# Main teach mode
# ---------------------------------------------------------------------------

def run_teach(
    block_id: str,
    arch_root: Path,
    level_override: Optional[str] = None,
    interactive: bool = True,
) -> dict[str, Path]:
    """Run teach mode for a block. Returns dict of generated {audience: path}."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    level = level_override or _read_abstraction_level(arch_root)
    html_config = _read_teach_html_config(arch_root)
    meta = _read_block_meta(arch_root, block_id)

    gov_dir = arch_root / "governance"
    gov_dir.mkdir(exist_ok=True)

    generated: dict[str, Path] = {}

    builders = {
        "technical": _build_technical_html,
        "team": _build_team_html,
        "learning": _build_learning_html,
    }

    for audience, builder in builders.items():
        if not html_config.get(audience, True):
            continue
        html = builder(meta, level, ts)
        path = gov_dir / f"teach-{block_id}-{audience}.html"
        path.write_text(html, encoding="utf-8")
        generated[audience] = path
        print(f"[teach_mode] {audience.capitalize()} HTML: {path.name}")

        # Text export
        text = _build_text_export(meta, audience, level)
        txt_path = gov_dir / f"teach-{block_id}-{audience}.txt"
        txt_path.write_text(text, encoding="utf-8")

    print(f"[teach_mode] Level: {level} · Generated: {', '.join(generated.keys())}")

    # Loopback prompt
    if interactive:
        print()
        print("[teach_mode] Enquanto você revisava, identificou algo a corrigir?")
        print("  [A] Não — código está bom, avançar para entrega")
        print("  [B] Sim — retornar para Implementar com nota do que corrigir")
        try:
            choice = input("  Sua escolha: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            choice = "A"

        if choice == "B":
            # Update wip_stage back to implementing in manifest
            manifests_dir = arch_root / "manifests"
            cands = list(manifests_dir.glob(f"{block_id}-*.md"))
            if cands:
                text = cands[0].read_text(encoding="utf-8", errors="replace")
                text = re.sub(r"^wip_stage:\s*\S+", "wip_stage: implementing", text, flags=re.MULTILINE)
                cands[0].write_text(text, encoding="utf-8")
            print("[teach_mode] Bloco retornado para wip_stage: implementing")
            try:
                note = input("  O que corrigir (nota): ").strip()
                if note:
                    print(f"[teach_mode] Nota: {note}")
            except (EOFError, KeyboardInterrupt):
                pass

    return generated


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="teach_mode",
        description="Generate teach HTMLs for a block (mandatory before corporate block close).",
    )
    p.add_argument("--block-id", required=True)
    p.add_argument("--arch-root", default=".")
    p.add_argument("--level", choices=list(ABSTRACTION_LEVELS),
                   help="Override abstraction level (default: from ux-config.yaml)")
    p.add_argument("--no-interactive", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()
    run_teach(args.block_id, arch_root, args.level, interactive=not args.no_interactive)
    return 0


if __name__ == "__main__":
    sys.exit(main())
