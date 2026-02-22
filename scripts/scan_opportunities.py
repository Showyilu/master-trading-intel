#!/usr/bin/env python3
"""Opportunity scanner with net-edge math and risk gating.

Formula (bps):
net_edge = gross_edge - fees - slippage - latency_risk - transfer_risk
transfer_risk = transfer_delay_min * transfer_penalty_bps_per_min

Supports execution profiles (taker/maker/inventory assumptions) so the same
candidate set can be stress-tested under different execution realities.
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

EXECUTION_PROFILES: dict[str, dict[str, float]] = {
    "taker_default": {
        "fee_multiplier": 1.0,
        "slippage_multiplier": 1.0,
        "latency_multiplier": 1.0,
        "transfer_delay_multiplier": 1.0,
        "transfer_penalty_bps_per_min": 0.45,
        "min_net_edge_bps": 8.0,
        "max_risk_score": 0.60,
    },
    "maker_inventory": {
        "fee_multiplier": 0.42,
        "slippage_multiplier": 0.72,
        "latency_multiplier": 0.95,
        "transfer_delay_multiplier": 0.30,
        "transfer_penalty_bps_per_min": 0.24,
        "min_net_edge_bps": 4.5,
        "max_risk_score": 0.62,
    },
    "maker_inventory_vip": {
        "fee_multiplier": 0.25,
        "slippage_multiplier": 0.60,
        "latency_multiplier": 0.90,
        "transfer_delay_multiplier": 0.20,
        "transfer_penalty_bps_per_min": 0.18,
        "min_net_edge_bps": 3.0,
        "max_risk_score": 0.65,
    },
}


@dataclass
class ScoredOpportunity:
    detected_at: str
    strategy_type: str
    symbol: str
    buy_venue: str
    sell_venue: str
    execution_profile: str
    gross_edge_bps: float
    source_fees_bps: float
    source_slippage_bps: float
    source_latency_risk_bps: float
    source_transfer_delay_min: float
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
    execution_profile: str,
    fee_multiplier: float,
    slippage_multiplier: float,
    latency_multiplier: float,
    transfer_delay_multiplier: float,
    transfer_penalty_bps_per_min: float,
    min_net_edge_bps: float,
    max_risk_score: float,
) -> ScoredOpportunity:
    source_fees_bps = float(item["fees_bps"])
    source_slippage_bps = float(item["slippage_bps"])
    source_latency_risk_bps = float(item["latency_risk_bps"])
    source_transfer_delay_min = float(item["transfer_delay_min"])

    fees_bps = round(source_fees_bps * fee_multiplier, 6)
    slippage_bps = round(source_slippage_bps * slippage_multiplier, 6)
    latency_risk_bps = round(source_latency_risk_bps * latency_multiplier, 6)
    transfer_delay_min = round(source_transfer_delay_min * transfer_delay_multiplier, 6)

    transfer_risk_bps = round(transfer_delay_min * transfer_penalty_bps_per_min, 4)
    net_edge_bps = round(
        float(item["gross_edge_bps"]) - fees_bps - slippage_bps - latency_risk_bps - transfer_risk_bps,
        4,
    )

    scoring_view = {
        "gross_edge_bps": float(item["gross_edge_bps"]),
        "fees_bps": fees_bps,
        "slippage_bps": slippage_bps,
        "latency_risk_bps": latency_risk_bps,
    }

    risk_score = _risk_score(scoring_view, net_edge_bps, transfer_risk_bps)
    is_qualified = net_edge_bps >= min_net_edge_bps and risk_score <= max_risk_score
    dominant_drag = _dominant_drag(scoring_view, transfer_risk_bps)
    rejection_reasons = []
    if not is_qualified:
        rejection_reasons = _rejection_reasons(
            scoring_view,
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
        execution_profile=execution_profile,
        gross_edge_bps=float(item["gross_edge_bps"]),
        source_fees_bps=source_fees_bps,
        source_slippage_bps=source_slippage_bps,
        source_latency_risk_bps=source_latency_risk_bps,
        source_transfer_delay_min=source_transfer_delay_min,
        fees_bps=fees_bps,
        slippage_bps=slippage_bps,
        latency_risk_bps=latency_risk_bps,
        transfer_delay_min=transfer_delay_min,
        transfer_risk_bps=transfer_risk_bps,
        net_edge_bps=net_edge_bps,
        risk_score=risk_score,
        size_usd=float(item["size_usd"]),
        dominant_drag=dominant_drag,
        is_qualified=is_qualified,
        rejection_reasons=rejection_reasons,
        notes=item.get("notes", ""),
    )


def _build_summary(
    scored: list[ScoredOpportunity],
    input_path: Path,
    execution_profile: str,
    fee_multiplier: float,
    slippage_multiplier: float,
    latency_multiplier: float,
    transfer_delay_multiplier: float,
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
        "execution_profile": execution_profile,
        "rules": {
            "fee_multiplier": fee_multiplier,
            "slippage_multiplier": slippage_multiplier,
            "latency_multiplier": latency_multiplier,
            "transfer_delay_multiplier": transfer_delay_multiplier,
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
    execution_profile: str,
    fee_multiplier: float,
    slippage_multiplier: float,
    latency_multiplier: float,
    transfer_delay_multiplier: float,
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
        f"Execution profile: `{execution_profile}`",
        "",
        "## Rules",
        (
            "- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk "
            f"({transfer_penalty_bps_per_min} bps/min)"
        ),
        (
            "- Profile multipliers: "
            f"fees×{fee_multiplier}, slippage×{slippage_multiplier}, "
            f"latency×{latency_multiplier}, transfer_delay×{transfer_delay_multiplier}"
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
        "--execution-profile",
        choices=sorted(EXECUTION_PROFILES.keys()),
        default="taker_default",
        help="Execution friction profile for scenario scoring.",
    )

    p.add_argument("--fee-multiplier", type=float, default=None)
    p.add_argument("--slippage-multiplier", type=float, default=None)
    p.add_argument("--latency-multiplier", type=float, default=None)
    p.add_argument("--transfer-delay-multiplier", type=float, default=None)

    p.add_argument("--transfer-penalty-bps-per-min", type=float, default=None)
    p.add_argument("--min-net-edge-bps", type=float, default=None)
    p.add_argument("--max-risk-score", type=float, default=None)

    return p.parse_args()


def main() -> None:
    args = parse_args()
    data = json.loads(args.input.read_text())

    profile = EXECUTION_PROFILES[args.execution_profile]

    fee_multiplier = (
        float(args.fee_multiplier)
        if args.fee_multiplier is not None
        else float(profile["fee_multiplier"])
    )
    slippage_multiplier = (
        float(args.slippage_multiplier)
        if args.slippage_multiplier is not None
        else float(profile["slippage_multiplier"])
    )
    latency_multiplier = (
        float(args.latency_multiplier)
        if args.latency_multiplier is not None
        else float(profile["latency_multiplier"])
    )
    transfer_delay_multiplier = (
        float(args.transfer_delay_multiplier)
        if args.transfer_delay_multiplier is not None
        else float(profile["transfer_delay_multiplier"])
    )

    transfer_penalty_bps_per_min = (
        float(args.transfer_penalty_bps_per_min)
        if args.transfer_penalty_bps_per_min is not None
        else float(profile.get("transfer_penalty_bps_per_min", DEFAULT_TRANSFER_PENALTY_BPS_PER_MIN))
    )
    min_net_edge_bps = (
        float(args.min_net_edge_bps)
        if args.min_net_edge_bps is not None
        else float(profile.get("min_net_edge_bps", DEFAULT_MIN_NET_EDGE_BPS))
    )
    max_risk_score = (
        float(args.max_risk_score)
        if args.max_risk_score is not None
        else float(profile.get("max_risk_score", DEFAULT_MAX_RISK_SCORE))
    )

    scored = [
        score_item(
            item,
            execution_profile=args.execution_profile,
            fee_multiplier=fee_multiplier,
            slippage_multiplier=slippage_multiplier,
            latency_multiplier=latency_multiplier,
            transfer_delay_multiplier=transfer_delay_multiplier,
            transfer_penalty_bps_per_min=transfer_penalty_bps_per_min,
            min_net_edge_bps=min_net_edge_bps,
            max_risk_score=max_risk_score,
        )
        for item in data
    ]

    scored_sorted = sorted(scored, key=lambda x: (x.is_qualified, x.net_edge_bps), reverse=True)
    summary = _build_summary(
        scored_sorted,
        input_path=args.input,
        execution_profile=args.execution_profile,
        fee_multiplier=fee_multiplier,
        slippage_multiplier=slippage_multiplier,
        latency_multiplier=latency_multiplier,
        transfer_delay_multiplier=transfer_delay_multiplier,
        transfer_penalty_bps_per_min=transfer_penalty_bps_per_min,
        min_net_edge_bps=min_net_edge_bps,
        max_risk_score=max_risk_score,
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_summary.parent.mkdir(parents=True, exist_ok=True)

    args.output_json.write_text(json.dumps([asdict(item) for item in scored_sorted], indent=2))
    args.output_md.write_text(
        render_markdown(
            scored_sorted,
            input_path=args.input,
            execution_profile=args.execution_profile,
            fee_multiplier=fee_multiplier,
            slippage_multiplier=slippage_multiplier,
            latency_multiplier=latency_multiplier,
            transfer_delay_multiplier=transfer_delay_multiplier,
            transfer_penalty_bps_per_min=transfer_penalty_bps_per_min,
            min_net_edge_bps=min_net_edge_bps,
            max_risk_score=max_risk_score,
        )
    )
    args.output_summary.write_text(json.dumps(summary, indent=2))

    print(f"Scored {len(scored)} candidates.")
    print(f"Qualified: {sum(1 for item in scored if item.is_qualified)}")
    print(f"Execution profile: {args.execution_profile}")
    print(f"Wrote: {args.output_json}")
    print(f"Wrote: {args.output_md}")
    print(f"Wrote: {args.output_summary}")


if __name__ == "__main__":
    main()
