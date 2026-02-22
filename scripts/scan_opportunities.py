#!/usr/bin/env python3
"""Simple opportunity scanner with net-edge math and risk gating.

Formula (bps):
net_edge = gross_edge - fees - slippage - latency_risk - transfer_risk
transfer_risk = transfer_delay_min * TRANSFER_PENALTY_BPS_PER_MIN
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "opportunity_candidates.sample.json"
OUTPUT_JSON = ROOT / "opportunities" / "shortlist-latest.json"
OUTPUT_MD = ROOT / "opportunities" / "dashboard-latest.md"

TRANSFER_PENALTY_BPS_PER_MIN = 0.45
MIN_NET_EDGE_BPS = 8.0
MAX_RISK_SCORE = 0.60


@dataclass
class ScoredOpportunity:
    detected_at: str
    strategy_type: str
    symbol: str
    buy_venue: str
    sell_venue: str
    gross_edge_bps: float
    fees_bps: float
    slippage_bps: float
    latency_risk_bps: float
    transfer_delay_min: float
    transfer_risk_bps: float
    net_edge_bps: float
    risk_score: float
    size_usd: float
    is_qualified: bool
    notes: str = ""


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _risk_score(item: dict[str, Any], net_edge_bps: float, transfer_risk_bps: float) -> float:
    # Weighted normalized risk dimensions.
    fee_component = _clamp(item["fees_bps"] / 20)
    slip_component = _clamp(item["slippage_bps"] / 20)
    latency_component = _clamp(item["latency_risk_bps"] / 12)
    transfer_component = _clamp(transfer_risk_bps / 12)
    edge_buffer_component = _clamp((10 - max(net_edge_bps, 0)) / 10)

    return round(
        0.20 * fee_component
        + 0.25 * slip_component
        + 0.20 * latency_component
        + 0.20 * transfer_component
        + 0.15 * edge_buffer_component,
        4,
    )


def score_item(item: dict[str, Any]) -> ScoredOpportunity:
    transfer_risk_bps = round(item["transfer_delay_min"] * TRANSFER_PENALTY_BPS_PER_MIN, 4)
    net_edge_bps = round(
        item["gross_edge_bps"]
        - item["fees_bps"]
        - item["slippage_bps"]
        - item["latency_risk_bps"]
        - transfer_risk_bps,
        4,
    )
    risk_score = _risk_score(item, net_edge_bps, transfer_risk_bps)
    is_qualified = net_edge_bps >= MIN_NET_EDGE_BPS and risk_score <= MAX_RISK_SCORE

    return ScoredOpportunity(
        detected_at=item["detected_at"],
        strategy_type=item["strategy_type"],
        symbol=item["symbol"],
        buy_venue=item["buy_venue"],
        sell_venue=item["sell_venue"],
        gross_edge_bps=item["gross_edge_bps"],
        fees_bps=item["fees_bps"],
        slippage_bps=item["slippage_bps"],
        latency_risk_bps=item["latency_risk_bps"],
        transfer_delay_min=item["transfer_delay_min"],
        transfer_risk_bps=transfer_risk_bps,
        net_edge_bps=net_edge_bps,
        risk_score=risk_score,
        size_usd=item["size_usd"],
        is_qualified=is_qualified,
        notes=item.get("notes", ""),
    )


def render_markdown(scored: list[ScoredOpportunity]) -> str:
    run_at = datetime.now(tz=timezone.utc).isoformat()
    qualified = [s for s in scored if s.is_qualified]

    lines = [
        "# Opportunity Dashboard (Latest)",
        "",
        f"Generated at: `{run_at}`",
        "",
        "## Rules",
        f"- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk ({TRANSFER_PENALTY_BPS_PER_MIN} bps/min)",
        f"- Qualified if `net_edge_bps >= {MIN_NET_EDGE_BPS}` and `risk_score <= {MAX_RISK_SCORE}`",
        "",
        f"## Summary\n- Candidates: **{len(scored)}**\n- Qualified: **{len(qualified)}**",
        "",
        "## Ranked Candidates",
        "",
        "| Rank | Pair | Path | Gross bps | Net bps | Risk | Qualified |",
        "|---:|---|---|---:|---:|---:|:---:|",
    ]

    ranked = sorted(scored, key=lambda x: (x.is_qualified, x.net_edge_bps), reverse=True)
    for i, item in enumerate(ranked, start=1):
        lines.append(
            f"| {i} | {item.symbol} | {item.buy_venue} -> {item.sell_venue} | {item.gross_edge_bps:.2f} | {item.net_edge_bps:.2f} | {item.risk_score:.2f} | {'✅' if item.is_qualified else '❌'} |"
        )

    lines.extend(["", "## Notes", "- This dashboard is for screening only, not execution advice."])
    return "\n".join(lines) + "\n"


def main() -> None:
    data = json.loads(INPUT_PATH.read_text())
    scored = [score_item(item) for item in data]

    scored_sorted = sorted(scored, key=lambda x: (x.is_qualified, x.net_edge_bps), reverse=True)

    OUTPUT_JSON.write_text(json.dumps([asdict(item) for item in scored_sorted], indent=2))
    OUTPUT_MD.write_text(render_markdown(scored_sorted))

    print(f"Scored {len(scored)} candidates.")
    print(f"Qualified: {sum(1 for item in scored if item.is_qualified)}")
    print(f"Wrote: {OUTPUT_JSON}")
    print(f"Wrote: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
