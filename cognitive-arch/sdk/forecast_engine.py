# sdk/forecast_engine.py
# PURPOSE: Generate HTML forecast: velocity (tickets/day + hours/ticket), delivery estimate
#          adjusted by calendar meetings, confidence band, parallelism recommendation.
#          Reorients phase_forecast.py to use actual_duration_hours from manifests.
# INPUTS:  --arch-root, optional --client
# OUTPUTS: governance/forecast-<client>-<ts>.html
# DEPS:    stdlib only; sdk/velocity_inference, sdk/calendar_manager (if available)
# USAGE:   python sdk/forecast_engine.py --arch-root .
# SEE:     design/forecast-calendar.md §2

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
# Velocity history
# ---------------------------------------------------------------------------

def _load_velocity_history(arch_root: Path, limit: int = 30) -> list[float]:
    """Load actual_duration_hours from the last N closed manifests."""
    hours_list: list[float] = []

    # Read BLOCK_LOG for recent done blocks
    log = arch_root / "blocks" / "BLOCK_LOG.md"
    if not log.exists():
        return []

    block_ids = []
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^(block-\d+)\s+done", line)
        if m:
            block_ids.append(m.group(1))

    # Load actual_duration_hours from manifests (most recent first)
    for bid in reversed(block_ids[-limit:]):
        manifests_dir = arch_root / "manifests"
        cands = list(manifests_dir.glob(f"{bid}-*.md"))
        if cands:
            text = cands[0].read_text(encoding="utf-8", errors="replace")
            m = re.search(r"^actual_duration_hours:\s*([0-9.]+)", text, re.MULTILINE)
            if m:
                try:
                    h = float(m.group(1))
                    if h > 0:
                        hours_list.append(h)
                except ValueError:
                    pass

    return hours_list


def _compute_velocity(history: list[float]) -> dict:
    """Compute velocity metrics from history."""
    if not history:
        return {
            "avg_hours_per_ticket": None,
            "tickets_per_day": None,
            "sample_count": 0,
        }
    avg_h = round(sum(history) / len(history), 2)
    # Assume 6 productive hours/day
    tickets_per_day = round(6.0 / avg_h, 2) if avg_h > 0 else None
    return {
        "avg_hours_per_ticket": avg_h,
        "tickets_per_day": tickets_per_day,
        "sample_count": len(history),
    }


def _confidence_band(sample_count: int) -> str:
    if sample_count < 3:
        return "BAIXO"
    elif sample_count <= 10:
        return "MÉDIO"
    return "ALTO"


# ---------------------------------------------------------------------------
# Calendar integration
# ---------------------------------------------------------------------------

def _load_meetings_today(arch_root: Path) -> float:
    """Return total meeting hours for today from pilot-calendar.yaml."""
    cal = arch_root / "governance" / "pilot-calendar.yaml"
    if not cal.exists():
        return 0.0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        text = cal.read_text(encoding="utf-8", errors="replace")
        total = 0.0
        # Simple parse: find meetings on today
        in_meeting = False
        date_match = False
        duration = 0.0
        for line in text.splitlines():
            if re.match(r"\s+- date:", line):
                in_meeting = True
                date_match = today in line
                duration = 0.0
            elif in_meeting and "duration_hours:" in line:
                m = re.search(r"duration_hours:\s*([0-9.]+)", line)
                if m:
                    duration = float(m.group(1))
            elif in_meeting and re.match(r"\s+- date:", line):
                if date_match:
                    total += duration
                in_meeting = True
                date_match = today in line
                duration = 0.0
        if date_match:
            total += duration
        return total
    except Exception:
        return 0.0


def _parallelism_recommendation(history: list[float], loop_back_count: int = 0) -> str:
    """Suggest parallelism level based on history quality."""
    if len(history) < 5:
        return "1 ticket (histórico insuficiente para paralelizar)"
    if loop_back_count > 0:
        return "1 ticket (houve loopbacks recentes — estabilizar antes)"
    avg_h = sum(history) / len(history)
    if avg_h > 0.5:  # pipeline takes > 30 min per step
        return "2 tickets em paralelo recomendado"
    return "1 ticket (pipeline rápido — paralelismo não agrega)"


# ---------------------------------------------------------------------------
# HTML generator
# ---------------------------------------------------------------------------

_FORECAST_HTML = """\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Forecast — {client} — {ts}</title>
<style>
  :root {{ --bg: #0f1117; --card: #1a1d27; --border: #2d3148; --accent: #6c8af7;
           --text: #e2e8f0; --muted: #8892a4; --ok: #4ade80; --warn: #facc15; --low: #f87171; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system,sans-serif;
          font-size: 14px; line-height: 1.6; padding: 24px; max-width: 680px; }}
  h1 {{ font-size: 20px; color: var(--accent); margin-bottom: 6px; }}
  h2 {{ font-size: 14px; color: var(--muted); border-bottom: 1px solid var(--border);
        padding-bottom: 6px; margin: 20px 0 10px; text-transform: uppercase; letter-spacing: .05em; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px;
           padding: 16px; margin-bottom: 12px; }}
  .big {{ font-size: 28px; font-weight: bold; color: var(--accent); }}
  .conf-HIGH {{ color: var(--ok); }} .conf-MÉDIO {{ color: var(--warn); }} .conf-BAIXO {{ color: var(--low); }}
  .footer {{ color: var(--muted); font-size: 12px; margin-top: 24px; border-top: 1px solid var(--border); padding-top: 10px; }}
</style>
</head>
<body>
<h1>📈 Forecast — {client}</h1>
<p style="color:var(--muted)">{ts}</p>

<h2>Velocity atual</h2>
<div class="card">
{velocity_block}
</div>

<h2>Estimativa de entrega</h2>
<div class="card">
{delivery_block}
</div>

<h2>Confidence</h2>
<div class="card">
  <p><span class="conf-{conf}">{conf}</span> — baseado em {sample_count} tickets</p>
  <p style="color:var(--muted);font-size:12px;margin-top:4px">
    &lt;3: BAIXO · 3-10: MÉDIO · &gt;10: ALTO
  </p>
</div>

<h2>Paralelismo</h2>
<div class="card">
  <p>{parallelism}</p>
</div>

{meetings_block}

<div class="footer">
  cognitive-arch/sdk/forecast_engine.py · {ts}
</div>
</body>
</html>
"""


def generate_forecast_html(
    arch_root: Path,
    client: str = "",
    open_tickets: int = 0,
    ts: Optional[str] = None,
) -> Path:
    """Generate forecast HTML. Returns path."""
    if ts is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")

    history = _load_velocity_history(arch_root)
    vel = _compute_velocity(history)
    conf = _confidence_band(vel["sample_count"])
    meetings_today = _load_meetings_today(arch_root)
    parallelism = _parallelism_recommendation(history)

    avg_h = vel.get("avg_hours_per_ticket")
    tpd = vel.get("tickets_per_day")

    if avg_h:
        velocity_block = (
            f'<p><span class="big">{tpd}</span> tickets/dia · '
            f'<strong>{avg_h}h</strong> por ticket (média)</p>'
        )
    else:
        velocity_block = "<p>Histórico insuficiente — feche ao menos 3 blocos com timestamps.</p>"

    if avg_h and open_tickets > 0 and tpd and tpd > 0:
        base_days = round(open_tickets / tpd, 1)
        meeting_days = round(meetings_today / 6.0, 2)
        adj_days = round(base_days + meeting_days, 1)
        delivery_block = (
            f"<p>Tickets em aberto: <strong>{open_tickets}</strong></p>"
            f"<p>Estimativa base: <strong>{base_days}</strong> dias úteis</p>"
            + (f"<p>Impacto reuniões: +{meeting_days} dias ({meetings_today}h hoje)</p>" if meetings_today else "")
            + f"<p>Estimativa ajustada: <strong>{adj_days}</strong> dias úteis</p>"
        )
    elif avg_h:
        delivery_block = "<p>Informe o número de tickets em aberto para estimativa de entrega.</p>"
    else:
        delivery_block = "<p>Dados insuficientes.</p>"

    meetings_block = ""
    if meetings_today > 0:
        meetings_block = (
            f"<h2>Reuniões hoje</h2>"
            f"<div class='card'><p>⚠️ {meetings_today}h de reunião hoje — capacidade reduzida</p></div>"
        )

    html = _FORECAST_HTML.format(
        client=client or "Piloto",
        ts=ts,
        velocity_block=velocity_block,
        delivery_block=delivery_block,
        conf=conf,
        sample_count=vel["sample_count"],
        parallelism=parallelism,
        meetings_block=meetings_block,
    )

    gov = arch_root / "governance"
    gov.mkdir(exist_ok=True)
    client_tag = f"-{client}" if client else ""
    out = gov / f"forecast{client_tag}-{ts}.html"
    out.write_text(html, encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="forecast_engine",
        description="Generate velocity forecast HTML with confidence and parallelism suggestion.",
    )
    p.add_argument("--arch-root", default=".")
    p.add_argument("--client", default="")
    p.add_argument("--open-tickets", type=int, default=0,
                   help="Number of open tickets for delivery estimate")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()
    path = generate_forecast_html(arch_root, args.client, args.open_tickets)
    print(f"[forecast_engine] HTML: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
