# sdk/scanner_html.py
# PURPOSE: Generate HTML dossier from scanner results. Full dossier with Mermaid diagrams,
#          proof-of-reasoning, flags, cost footer. One HTML per scan.
# INPUTS:  ProjectProfile, scan result dict, arch_root, timestamp
# OUTPUTS: governance/scanner-output-<client>-<YYYYMMDD-HHMM>.html
# DEPS:    stdlib only; sdk/scanner_profile
# USAGE:   from scanner_html import generate_html; path = generate_html(profile, result, arch, ts)
# SEE:     design/scanner.md §3

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Mermaid diagram builders
# ---------------------------------------------------------------------------

def _build_arch_diagram(tree_lines: list[str]) -> str:
    """Build a Mermaid flowchart from directory tree."""
    if not tree_lines:
        return "graph TD\n    A[Root] --> B[...]\n"
    nodes = []
    edges = []
    prev_depth = 0
    prev_id = "ROOT"
    id_map: dict[str, str] = {"": "ROOT"}
    node_id = 0

    nodes.append(f'    ROOT["📁 repo root"]')
    for line in tree_lines[:20]:
        depth = (len(line) - len(line.lstrip())) // 2
        clean = line.strip().rstrip("/")
        if not clean:
            continue
        nid = f"N{node_id}"
        node_id += 1
        label = clean.replace("[", "").replace("]", "")
        nodes.append(f'    {nid}["{label}"]')

        # Find parent
        parent = "ROOT"
        for stored_depth in range(depth - 1, -1, -1):
            key = f"d{stored_depth}"
            if key in id_map:
                parent = id_map[key]
                break
        id_map[f"d{depth}"] = nid
        edges.append(f"    {parent} --> {nid}")

    return "graph TD\n" + "\n".join(nodes[:15]) + "\n" + "\n".join(edges[:15])


def _build_dep_graph(deps: list[str]) -> str:
    """Build a simple Mermaid graph from top dependencies."""
    if not deps:
        return "graph LR\n    A[No deps detected]\n"
    lines = ["graph LR\n    ROOT[App]"]
    for i, dep in enumerate(deps[:8]):
        name = re.sub(r"[@/].*", "", dep)  # strip version/scope
        lines.append(f"    ROOT --> D{i}[{name}]")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Scanner Dossier — {client} — {ts}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<style>
  :root {{ --bg: #0f1117; --card: #1a1d27; --border: #2d3148; --accent: #6c8af7;
           --text: #e2e8f0; --muted: #8892a4; --ok: #4ade80; --warn: #facc15; --err: #f87171; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
          font-size: 14px; line-height: 1.6; padding: 24px; }}
  h1 {{ font-size: 22px; color: var(--accent); margin-bottom: 6px; }}
  h2 {{ font-size: 16px; color: var(--text); border-bottom: 1px solid var(--border);
        padding-bottom: 6px; margin: 24px 0 12px; }}
  h3 {{ font-size: 14px; color: var(--muted); margin-bottom: 8px; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px;
           padding: 16px; margin-bottom: 16px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px;
            background: var(--border); color: var(--text); margin: 2px; }}
  .badge.ok {{ background: #1a3a2a; color: var(--ok); }}
  .badge.warn {{ background: #3a3010; color: var(--warn); }}
  .badge.err {{ background: #3a1010; color: var(--err); }}
  table {{ width: 100%; border-collapse: collapse; }}
  td, th {{ padding: 6px 10px; border-bottom: 1px solid var(--border); text-align: left; }}
  th {{ color: var(--muted); font-weight: 500; }}
  .mermaid {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px;
              padding: 16px; margin-bottom: 16px; overflow-x: auto; }}
  details summary {{ cursor: pointer; color: var(--muted); font-size: 13px; padding: 4px 0; }}
  details {{ border: 1px solid var(--border); border-radius: 6px; padding: 8px 12px; margin-top: 8px; }}
  .footer {{ text-align: center; color: var(--muted); font-size: 12px; margin-top: 32px;
             border-top: 1px solid var(--border); padding-top: 12px; }}
  .flag {{ border-left: 3px solid var(--warn); padding: 8px 12px; margin-bottom: 8px; background: #1e1a0a; border-radius: 0 4px 4px 0; }}
  pre {{ background: #0a0c14; padding: 10px; border-radius: 6px; overflow-x: auto;
         font-size: 12px; color: #a8b3d0; }}
</style>
</head>
<body>
<h1>🔍 Scanner Dossier — {client}</h1>
<p style="color:var(--muted)">Scan {level} · {ts} · cognitive-arch v3</p>

{stack_section}
{l1_section}
{arch_diagram_section}
{dep_graph_section}
{patterns_section}
{l4_section}
{proof_section}
{flags_section}

<div class="footer">
  <p>Tokens: ~{tokens} | Est. custo: ~${usd} USD | Gerado por cognitive-arch/sdk/scanner_html.py</p>
  <p style="margin-top:4px;color:#555">Somente metadados — nenhum código real do cliente foi armazenado.</p>
</div>

<script>mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});</script>
</body>
</html>
"""


def _stack_section(scan_result: dict) -> str:
    l0 = scan_result.get("l0", {})
    if not l0:
        return ""
    stack = l0.get("stack", {})
    sys_type = l0.get("sys_type", "unknown")
    entities = l0.get("domain_entities", [])

    rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in stack.items() if v)
    ent_badges = "".join(f'<span class="badge">{e}</span>' for e in entities[:12])

    return f"""
<h2>🏗️ Stack & Domínio</h2>
<div class="grid">
<div class="card">
  <h3>Sistema: <strong>{sys_type}</strong></h3>
  <table><tr><th>Campo</th><th>Valor</th></tr>{rows}</table>
</div>
<div class="card">
  <h3>Entidades detectadas</h3>
  {ent_badges or '<span class="badge warn">Nenhuma detectada</span>'}
</div>
</div>
"""


def _l1_section(scan_result: dict) -> str:
    l1 = scan_result.get("l1", scan_result.get("l0", {}))
    langs = l1.get("languages", {})
    entries = l1.get("entry_points", [])
    file_count = l1.get("file_count", scan_result.get("file_count", 0))

    if not langs and not entries:
        return ""

    lang_rows = "".join(f"<tr><td>{l}</td><td>{p}%</td></tr>" for l, p in list(langs.items())[:6])
    entry_items = "".join(f"<li><code>{e}</code></li>" for e in entries)

    return f"""
<h2>📂 Estrutura & Linguagens</h2>
<div class="grid">
<div class="card">
  <h3>Linguagens ({file_count} arquivos relevantes)</h3>
  <table><tr><th>Linguagem</th><th>%</th></tr>{lang_rows or "<tr><td colspan='2'>Não detectadas</td></tr>"}</table>
</div>
<div class="card">
  <h3>Entry Points</h3>
  <ul style="padding-left:16px">{entry_items or "<li>Nenhum detectado</li>"}</ul>
</div>
</div>
"""


def _arch_diagram_section(scan_result: dict) -> str:
    l0 = scan_result.get("l0", {})
    tree = l0.get("tree", [])
    diagram = _build_arch_diagram(tree)
    return f"""
<h2>🗺️ Mapa Arquitetural</h2>
<div class="mermaid">
{diagram}
</div>
"""


def _dep_graph_section(scan_result: dict) -> str:
    l0 = scan_result.get("l0", {})
    l1 = scan_result.get("l1", {})
    deps = l0.get("deps", l1.get("deps", []))
    diagram = _build_dep_graph(deps)
    return f"""
<h2>📦 Grafo de Dependências</h2>
<div class="mermaid">
{diagram}
</div>
"""


def _patterns_section(scan_result: dict) -> str:
    arch = scan_result.get("architecture", "")
    naming = scan_result.get("naming", {})
    import_style = scan_result.get("import_style", "")
    test_style = scan_result.get("test_style", "")

    if not arch and not naming:
        return ""

    naming_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in naming.items())

    return f"""
<h2>🎨 Padrões Detectados</h2>
<div class="grid">
<div class="card">
  <h3>Arquitetura</h3>
  <p><strong>{arch or "Não analisada"}</strong></p>
  {f'<p>Imports: {import_style}</p>' if import_style else ''}
  {f'<p>Testes: {test_style}</p>' if test_style else ''}
</div>
<div class="card">
  <h3>Convenções de Naming</h3>
  <table><tr><th>Contexto</th><th>Estilo</th></tr>
  {naming_rows or "<tr><td colspan='2'>Não analisadas</td></tr>"}
  </table>
</div>
</div>
"""


def _l4_section(scan_result: dict) -> str:
    coex = scan_result.get("l4_coexistence", {})
    if not coex:
        return ""
    vigente = coex.get("vigente", "?")
    legado = coex.get("legado", "?")
    confidence = coex.get("confidence", "low")
    badge_class = "ok" if confidence == "high" else ("warn" if confidence == "medium" else "err")

    return f"""
<h2>⚡ Coexistência de Padrões (L4)</h2>
<div class="card">
  <span class="badge {badge_class}">Confidence: {confidence}</span>
  <table style="margin-top:8px">
    <tr><th>Status</th><th>Padrão</th></tr>
    <tr><td>✅ Vigente (seguir)</td><td><code>{vigente}</code></td></tr>
    <tr><td>⚠️ Legado (não replicar)</td><td><code>{legado}</code></td></tr>
  </table>
</div>
"""


def _proof_section(scan_result: dict) -> str:
    proofs = scan_result.get("proofs", {})
    if not proofs:
        return ""
    items = "".join(
        f"<details><summary>Nível {lvl}</summary><p>{proof}</p></details>"
        for lvl, proof in proofs.items()
    )
    return f"""
<h2>🔎 Prova de Raciocínio</h2>
<div class="card">{items}</div>
"""


def _flags_section(scan_result: dict) -> str:
    flags: list[str] = []
    error = scan_result.get("error", "")
    if error:
        flags.append(f"⚠️ Erro no scan: {error}")
    l4 = scan_result.get("l4_coexistence", {})
    if l4.get("confidence") == "low":
        flags.append("⚠️ L4: baixa confiança na detecção de padrões — revisar manualmente")
    coex_legado = l4.get("legado", "")
    if coex_legado and coex_legado != "nenhum legado detectado":
        flags.append(f"⚠️ L4: legado detectado ({coex_legado}) — não replicar")

    if not flags:
        return ""

    items = "".join(f'<div class="flag">{f}</div>' for f in flags)
    return f"""
<h2>🚩 Flags de Atenção</h2>
{items}
"""


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_html(profile, scan_result: dict, arch_root: Path, ts: str) -> Path:
    """Generate HTML dossier. Returns path to created HTML file."""
    client = profile.client
    level = scan_result.get("level", "L0")
    tokens = scan_result.get("tokens_used", 0)
    usd = scan_result.get("usd_estimate", 0.0)

    html = _HTML_TEMPLATE.format(
        client=client,
        ts=ts,
        level=level,
        tokens=tokens,
        usd=usd,
        stack_section=_stack_section(scan_result),
        l1_section=_l1_section(scan_result),
        arch_diagram_section=_arch_diagram_section(scan_result),
        dep_graph_section=_dep_graph_section(scan_result),
        patterns_section=_patterns_section(scan_result),
        l4_section=_l4_section(scan_result),
        proof_section=_proof_section(scan_result),
        flags_section=_flags_section(scan_result),
    )

    out_dir = arch_root / "governance"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"scanner-output-{client}-{ts}.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path
