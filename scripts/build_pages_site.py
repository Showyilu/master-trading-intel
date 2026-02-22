#!/usr/bin/env python3
"""Build static GitHub Pages site from latest opportunity outputs."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHORTLIST = ROOT / "opportunities" / "shortlist-latest.json"
DEFAULT_DASHBOARD_MD = ROOT / "opportunities" / "dashboard-latest.md"
DEFAULT_OUT_DIR = ROOT / "site"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build static dashboard site for GitHub Pages")
    p.add_argument("--shortlist", type=Path, default=DEFAULT_SHORTLIST)
    p.add_argument("--dashboard", type=Path, default=DEFAULT_DASHBOARD_MD)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return p.parse_args()


def _fmt(v: float, n: int = 2) -> str:
    return f"{v:.{n}f}"


def _read_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text())
    return payload if isinstance(payload, list) else []


def build_html(rows: list[dict], generated_at: str) -> str:
    qualified = [r for r in rows if r.get("is_qualified")]

    def render_rows(data: list[dict]) -> str:
        if not data:
            return "<tr><td colspan='8'>No rows</td></tr>"
        out = []
        for i, r in enumerate(data, start=1):
            out.append(
                "<tr>"
                f"<td>{i}</td>"
                f"<td>{html.escape(str(r.get('symbol', '-')))}</td>"
                f"<td>{html.escape(str(r.get('buy_venue', '-')))} → {html.escape(str(r.get('sell_venue', '-')))}</td>"
                f"<td>{_fmt(float(r.get('gross_edge_bps', 0.0)))}</td>"
                f"<td>{_fmt(float(r.get('net_edge_bps', 0.0)))}</td>"
                f"<td>{_fmt(float(r.get('risk_score', 0.0)))}</td>"
                f"<td>{_fmt(float(r.get('size_usd', 0.0)))}" "</td>"
                f"<td>{'✅' if r.get('is_qualified') else '❌'}</td>"
                "</tr>"
            )
        return "\n".join(out)

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Master Trading Intel — Opportunity Dashboard</title>
  <style>
    body {{ font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; background: #0b1020; color: #e7ecff; }}
    .card {{ background: #121935; border: 1px solid #2a3568; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    .muted {{ color: #9fb0e6; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #283463; padding: 8px; text-align: left; }}
    th {{ color: #b9c7f5; font-weight: 600; }}
    .pill {{ display:inline-block; padding: 2px 8px; border-radius: 999px; background:#1d2a5c; margin-right:8px; }}
    a {{ color: #7db4ff; }}
  </style>
</head>
<body>
  <h1>Master Trading Intel — Opportunity Dashboard</h1>
  <div class=\"muted\">Generated: {html.escape(generated_at)} UTC</div>

  <div class=\"card\">
    <span class=\"pill\">Candidates: <b>{len(rows)}</b></span>
    <span class=\"pill\">Qualified: <b>{len(qualified)}</b></span>
    <span class=\"pill\">Pass rate: <b>{(len(qualified)/len(rows)*100 if rows else 0):.1f}%</b></span>
    <p class=\"muted\">Net edge formula: gross - fees - slippage - latency risk - transfer risk</p>
    <p><a href=\"shortlist-latest.json\">shortlist-latest.json</a> · <a href=\"dashboard-latest.md\">dashboard-latest.md</a></p>
  </div>

  <div class=\"card\">
    <h2>Qualified Opportunities</h2>
    <table>
      <thead><tr><th>#</th><th>Symbol</th><th>Path</th><th>Gross bps</th><th>Net bps</th><th>Risk</th><th>Size USD</th><th>Pass</th></tr></thead>
      <tbody>
      {render_rows(qualified)}
      </tbody>
    </table>
  </div>

  <div class=\"card\">
    <h2>All Candidates</h2>
    <table>
      <thead><tr><th>#</th><th>Symbol</th><th>Path</th><th>Gross bps</th><th>Net bps</th><th>Risk</th><th>Size USD</th><th>Pass</th></tr></thead>
      <tbody>
      {render_rows(rows)}
      </tbody>
    </table>
  </div>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    rows = _read_json(args.shortlist)
    generated_at = datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    dashboard_md = args.dashboard.read_text() if args.dashboard.exists() else "# Dashboard not generated yet\n"
    (out_dir / "dashboard-latest.md").write_text(dashboard_md)
    (out_dir / "shortlist-latest.json").write_text(json.dumps(rows, indent=2))
    (out_dir / "index.html").write_text(build_html(rows, generated_at))

    print(f"Site built at: {out_dir}")


if __name__ == "__main__":
    main()
