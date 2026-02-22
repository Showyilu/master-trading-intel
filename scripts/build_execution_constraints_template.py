#!/usr/bin/env python3
"""Generate/refresh execution-constraint template from live candidate universe.

The output captures per (venue, asset) limits used by scan_opportunities.py:
- max_position_usd
- available_inventory_usd
- max_borrow_usd
- borrow_rate_bps_per_hour
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "opportunity_candidates.combined.live.json"
DEFAULT_OUTPUT = ROOT / "data" / "execution_constraints.latest.json"

DEFAULT_STRATEGY_HOLD_HOURS = {
    "cex_cex": 0.20,
    "cex_dex": 0.30,
    "funding_carry_cex_cex": 8.0,
    "perp_spot_basis": 8.0,
}

VENUE_STOPWORDS = {
    "long",
    "short",
    "spot",
    "perp",
    "futures",
    "future",
    "swap",
    "dex",
    "cex",
    "buy",
    "sell",
}

CORE_ASSETS = {"BTC", "ETH", "SOL"}


def canonical_venue(raw_venue: str) -> str:
    lowered = str(raw_venue).strip().lower()
    if not lowered:
        return "unknown"

    tokens = [t for t in re.split(r"[^a-z0-9]+", lowered) if t]
    for token in tokens:
        if token not in VENUE_STOPWORDS:
            return token

    return lowered


def asset_from_symbol(symbol: str) -> str:
    raw = str(symbol).strip().upper()
    if "/" in raw:
        return raw.split("/")[0].strip() or "UNKNOWN"
    parts = [p for p in re.split(r"[^A-Z0-9]+", raw) if p]
    return parts[0] if parts else "UNKNOWN"


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text())
    except Exception:
        return fallback


def suggest_limits(max_size_usd: float, asset: str) -> dict[str, float]:
    baseline = max(1000.0, max_size_usd)

    max_position = round(baseline * 1.4, 2)
    available_inventory = round(baseline * 0.35, 2)
    max_borrow = round(baseline * 0.75, 2)

    if asset in CORE_ASSETS:
        borrow_rate = 0.65
    else:
        borrow_rate = 1.15

    return {
        "max_position_usd": max_position,
        "available_inventory_usd": available_inventory,
        "max_borrow_usd": max_borrow,
        "borrow_rate_bps_per_hour": borrow_rate,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build execution constraints template from candidates")
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    candidates = load_json(args.input, fallback=[])
    if not isinstance(candidates, list):
        raise SystemExit(f"Input is not a candidate list: {args.input}")

    existing = load_json(args.output, fallback={})
    if not isinstance(existing, dict):
        existing = {}

    existing_rules: dict[tuple[str, str], dict[str, Any]] = {}
    for row in existing.get("rules", []):
        if not isinstance(row, dict):
            continue
        venue = str(row.get("venue", "")).strip().lower()
        asset = str(row.get("asset", "")).strip().upper()
        if venue and asset:
            existing_rules[(venue, asset)] = row

    sizes_by_key: dict[tuple[str, str], list[float]] = defaultdict(list)
    for item in candidates:
        if not isinstance(item, dict):
            continue
        try:
            size = float(item.get("size_usd", 0) or 0)
        except (TypeError, ValueError):
            size = 0.0
        if size <= 0:
            continue

        asset = asset_from_symbol(item.get("symbol", ""))
        buy_venue = canonical_venue(item.get("buy_venue", ""))
        sell_venue = canonical_venue(item.get("sell_venue", ""))

        sizes_by_key[(buy_venue, asset)].append(size)
        sizes_by_key[(sell_venue, asset)].append(size)

    merged_rules: list[dict[str, Any]] = []
    for venue, asset in sorted(sizes_by_key.keys()):
        key = (venue, asset)
        if key in existing_rules:
            merged_rules.append(existing_rules[key])
            continue

        max_size = max(sizes_by_key[key])
        suggested = suggest_limits(max_size, asset)
        merged_rules.append(
            {
                "venue": venue,
                "asset": asset,
                **suggested,
            }
        )

    # Keep legacy/manual entries that are no longer in current candidate universe.
    for key, row in sorted(existing_rules.items()):
        if key not in sizes_by_key:
            merged_rules.append(row)

    defaults = existing.get("defaults", {}) if isinstance(existing.get("defaults"), dict) else {}
    defaults_out = {
        "max_position_usd": float(defaults.get("max_position_usd", 12000.0)),
        "available_inventory_usd": float(defaults.get("available_inventory_usd", 0.0)),
        "max_borrow_usd": float(defaults.get("max_borrow_usd", 0.0)),
        "borrow_rate_bps_per_hour": float(defaults.get("borrow_rate_bps_per_hour", 1.0)),
    }

    hold_hours = dict(DEFAULT_STRATEGY_HOLD_HOURS)
    if isinstance(existing.get("strategy_hold_hours"), dict):
        for k, v in existing["strategy_hold_hours"].items():
            try:
                hold_hours[str(k)] = max(0.0, float(v))
            except (TypeError, ValueError):
                continue

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": "execution_constraints_v1",
        "defaults": defaults_out,
        "strategy_hold_hours": hold_hours,
        "rules": merged_rules,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2))

    print(f"Loaded candidates: {len(candidates)}")
    print(f"Constraint rules: {len(merged_rules)}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
