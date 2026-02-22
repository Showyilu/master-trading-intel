#!/usr/bin/env python3
"""Opportunity scanner with net-edge math and risk gating.

Formula (bps):
net_edge = gross_edge - fees - slippage - latency_risk - transfer_risk
transfer_risk = transfer_delay_min * transfer_penalty_bps_per_min
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = ROOT / "data" / "opportunity_candidates.sample.json"
DEFAULT_OUTPUT_JSON = ROOT / "opportunities" / "shortlist-latest.json"
DEFAULT_OUTPUT_MD = ROOT / "opportunities" / "dashboard-latest.md"
DEFAULT_OUTPUT_SUMMARY = ROOT / "opportunities" / "rejection-summary-latest.json"

DEFAULT_TRANSFER_PENALTY_BPS_PER_MIN = 0.45
DEFAULT_MIN_NET_EDGE_BPS = 8.0
DEFAULT_MAX_RISK_SCORE = 0.60


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
    dominant_drag: str
    is_qualified: bool
    rejection_reasons: list[str]
    notes: str = ""


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _risk_score(item: dict[str, Any], net_edge_bps: float, transfer_risk_bps: float) -> float:
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


def _dominant_drag(item: dict[str, Any], transfer_risk_bps: float) -> str:
    components = {
        "fees": item["fees_bps"],
        "slippage": item["slippage_bps"],
        "latency": item["latency_risk_bps"],
        "transfer": transfer_risk_bps,
    }
    return max(components.items(), key=lambda kv: kv[1])[0]


def _rejection_reasons(
    item: dict[str, Any],
    net_edge_bps: float,
    risk_score: float,
    transfer_risk_bps: float,
    min_net_edge_bps: float,
    max_risk_score: float,
) -> list[str]:
    reasons: list[str] = []

    if net_edge_bps < min_net_edge_bps:
        reasons.append("net_edge_below_threshold")
    if risk_score > max_risk_score:
        reasons.append("risk_score_above_threshold")

    gross = item["gross_edge_bps"]
    if item["fees_bps"] >= gross:
        reasons.append("fee_dominated")
    if item["slippage_bps"] >= gross:
        reasons.append("slippage_dominated")
    if (item["latency_risk_bps"] + transfer_risk_bps) >= gross:
        reasons.append("latency_transfer_dominated")

    return reasons


def score_item(
    item: dict[str, Any],
    transfer_penalty_bps_per_min: float,
    min_net_edge_bps: float,
    max_risk_score: float,
) -> ScoredOpportunity:
    transfer_risk_bps = round(item["transfer_delay_min"] * transfer_penalty_bps_per_min, 4)
    net_edge_bps = round(
        item["gross_edge_bps"]
        - item["fees_bps"]
        - item["slippage_bps"]
        - item["latency_risk_bps"]
        - transfer_risk_bps,
        4,
    )
    risk_score = _risk_score(item, net_edge_bps, transfer_risk_bps)
    is_qualified = net_edge_bps >= min_net_edge_bps and risk_score <= max_risk_score
    dominant_drag = _dominant_drag(item, transfer_risk_bps)
    rejection_reasons = []
    if not is_qualified:
        rejection_reasons = _rejection_reasons(
            item,
            net_edge_bps=net_edge_bps,
            risk_score=risk_score,
            transfer_risk_bps=transfer_risk_bps,
            min_net_edge_bps=min_net_edge_bps,
            max_risk_score=max_risk_score,
        )

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
        dominant_drag=dominant_drag,
        is_qualified=is_qualified,
        rejection_reasons=rejection_reasons,
        notes=item.get("notes", ""),
    )


def _build_summary(
    scored: list[ScoredOpportunity],
    input_path: Path,
    transfer_penalty_bps_per_min: float,
    min_net_edge_bps: float,
    max_risk_score: float,
) -> dict[str, Any]:
    rejected = [s for s in scored if not s.is_qualified]
    reason_counter = Counter(reason for s in rejected for reason in s.rejection_reasons)
    drag_counter = Counter(s.dominant_drag for s in rejected)

    return {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "input": str(input_path),
        "rules": {
            "transfer_penalty_bps_per_min": transfer_penalty_bps_per_min,
            "min_net_edge_bps": min_net_edge_bps,
            "max_risk_score": max_risk_score,
        },
        "counts": {
            "candidates": len(scored),
            "qualified": len(scored) - len(rejected),
            "rejected": len(rejected),
        },
        "rejection_reason_counts": dict(sorted(reason_counter.items())),
        "dominant_drag_counts": dict(sorted(drag_counter.items())),
        "top_rejected": [
            {
                "symbol": s.symbol,
                "path": f"{s.buy_venue}->{s.sell_venue}",
                "net_edge_bps": s.net_edge_bps,
                "risk_score": s.risk_score,
                "dominant_drag": s.dominant_drag,
                "rejection_reasons": s.rejection_reasons,
            }
            for s in sorted(rejected, key=lambda x: x.net_edge_bps, reverse=True)[:10]
        ],
    }


def render_markdown(
    scored: list[ScoredOpportunity],
    input_path: Path,
    transfer_penalty_bps_per_min: float,
    min_net_edge_bps: float,
    max_risk_score: float,
) -> str:
    run_at = datetime.now(tz=timezone.utc).isoformat()
    qualified = [s for s in scored if s.is_qualified]
    rejected = [s for s in scored if not s.is_qualified]
    reason_counter = Counter(reason for s in rejected for reason in s.rejection_reasons)
    dominant_drag_counter = Counter(s.dominant_drag for s in rejected)

    lines = [
        "# Opportunity Dashboard (Latest)",
        "",
        f"Generated at: `{run_at}`",
        f"Input: `{input_path}`",
        "",
        "## Rules",
        (
            "- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk "
            f"({transfer_penalty_bps_per_min} bps/min)"
        ),
        f"- Qualified if `net_edge_bps >= {min_net_edge_bps}` and `risk_score <= {max_risk_score}`",
        "",
        f"## Summary\n- Candidates: **{len(scored)}**\n- Qualified: **{len(qualified)}**\n- Rejected: **{len(rejected)}**",
        "",
        "## Rejection Breakdown",
    ]

    if not rejected:
        lines.append("- No rejected candidates this run.")
    else:
        if reason_counter:
            lines.append("- By reason:")
            for reason, count in sorted(reason_counter.items(), key=lambda kv: kv[1], reverse=True):
                lines.append(f"  - `{reason}`: **{count}**")
        if dominant_drag_counter:
            lines.append("- Dominant drag:")
            for drag, count in sorted(dominant_drag_counter.items(), key=lambda kv: kv[1], reverse=True):
                lines.append(f"  - `{drag}`: **{count}**")

    lines.extend(
        [
            "",
            "## Ranked Candidates",
            "",
            "| Rank | Pair | Path | Gross bps | Net bps | Risk | Drag | Qualified | Rejection Reasons |",
            "|---:|---|---|---:|---:|---:|---|:---:|---|",
        ]
    )

    ranked = sorted(scored, key=lambda x: (x.is_qualified, x.net_edge_bps), reverse=True)
    for i, item in enumerate(ranked, start=1):
        reasons = ", ".join(item.rejection_reasons) if item.rejection_reasons else "-"
        lines.append(
            f"| {i} | {item.symbol} | {item.buy_venue} -> {item.sell_venue} | {item.gross_edge_bps:.2f} | {item.net_edge_bps:.2f} | {item.risk_score:.2f} | {item.dominant_drag} | {'✅' if item.is_qualified else '❌'} | {reasons} |"
        )

    lines.extend(["", "## Notes", "- This dashboard is for screening only, not execution advice."])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Score opportunity candidates with risk gates.")
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="Input opportunity JSON list")
    p.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON, help="Output scored JSON")
    p.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD, help="Output dashboard markdown")
    p.add_argument("--output-summary", type=Path, default=DEFAULT_OUTPUT_SUMMARY, help="Output rejection summary JSON")
    p.add_argument(
        "--transfer-penalty-bps-per-min",
        type=float,
        default=DEFAULT_TRANSFER_PENALTY_BPS_PER_MIN,
    )
    p.add_argument("--min-net-edge-bps", type=float, default=DEFAULT_MIN_NET_EDGE_BPS)
    p.add_argument("--max-risk-score", type=float, default=DEFAULT_MAX_RISK_SCORE)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    data = json.loads(args.input.read_text())

    scored = [
        score_item(
            item,
            transfer_penalty_bps_per_min=args.transfer_penalty_bps_per_min,
            min_net_edge_bps=args.min_net_edge_bps,
            max_risk_score=args.max_risk_score,
        )
        for item in data
    ]

    scored_sorted = sorted(scored, key=lambda x: (x.is_qualified, x.net_edge_bps), reverse=True)
    summary = _build_summary(
        scored_sorted,
        input_path=args.input,
        transfer_penalty_bps_per_min=args.transfer_penalty_bps_per_min,
        min_net_edge_bps=args.min_net_edge_bps,
        max_risk_score=args.max_risk_score,
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_summary.parent.mkdir(parents=True, exist_ok=True)

    args.output_json.write_text(json.dumps([asdict(item) for item in scored_sorted], indent=2))
    args.output_md.write_text(
        render_markdown(
            scored_sorted,
            input_path=args.input,
            transfer_penalty_bps_per_min=args.transfer_penalty_bps_per_min,
            min_net_edge_bps=args.min_net_edge_bps,
            max_risk_score=args.max_risk_score,
        )
    )
    args.output_summary.write_text(json.dumps(summary, indent=2))

    print(f"Scored {len(scored)} candidates.")
    print(f"Qualified: {sum(1 for item in scored if item.is_qualified)}")
    print(f"Wrote: {args.output_json}")
    print(f"Wrote: {args.output_md}")
    print(f"Wrote: {args.output_summary}")


if __name__ == "__main__":
    main()
