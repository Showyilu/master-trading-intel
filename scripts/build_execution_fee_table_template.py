#!/usr/bin/env python3
"""Generate/refresh execution fee table template from current candidate universe.

The output is consumed by scan_opportunities.py to replace embedded candidate fees
with explicit venue/instrument fee assumptions (taker/maker/maker_vip), so fee
math is versioned and editable in one place.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "opportunity_candidates.combined.live.json"
DEFAULT_OUTPUT = ROOT / "data" / "execution_fee_table.latest.json"

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

INSTRUMENT_KEYWORDS = {
    "perp": {"perp", "future", "futures", "swap"},
    "dex": {"dex", "jupiter", "uniswap", "raydium", "0x", "orca"},
    "spot": {"spot"},
}

DEFAULT_PROFILE_FEE_MODE = {
    "taker_default": "taker",
    "maker_inventory": "maker",
    "maker_inventory_vip": "maker_vip",
}

DEFAULT_STRATEGY_ROUNDTRIP_SIDE_MULTIPLIER = {
    "cex_cex": 1.0,
    "cex_dex": 1.0,
    "funding_carry_cex_cex": 2.0,
    "perp_spot_basis": 2.0,
}

DEFAULT_INSTRUMENT_FEES = {
    "spot": {"taker_bps": 10.0, "maker_bps": 8.0, "maker_vip_bps": 3.5},
    "perp": {"taker_bps": 5.5, "maker_bps": 2.0, "maker_vip_bps": 0.9},
    "dex": {"taker_bps": 6.0, "maker_bps": 6.0, "maker_vip_bps": 5.0},
    "unknown": {"taker_bps": 10.0, "maker_bps": 8.0, "maker_vip_bps": 4.0},
}

VENUE_BASELINES: dict[tuple[str, str], dict[str, float]] = {
    ("binance", "spot"): {"taker_bps": 10.0, "maker_bps": 8.0, "maker_vip_bps": 2.8},
    ("binance", "perp"): {"taker_bps": 5.0, "maker_bps": 2.0, "maker_vip_bps": 0.8},
    ("bybit", "spot"): {"taker_bps": 10.0, "maker_bps": 8.0, "maker_vip_bps": 3.2},
    ("bybit", "perp"): {"taker_bps": 5.5, "maker_bps": 2.0, "maker_vip_bps": 1.0},
    ("jupiter", "dex"): {"taker_bps": 6.0, "maker_bps": 6.0, "maker_vip_bps": 5.0},
}


def canonical_venue(raw_venue: str) -> str:
    lowered = str(raw_venue).strip().lower()
    if not lowered:
        return "unknown"

    tokens = [t for t in re.split(r"[^a-z0-9]+", lowered) if t]
    for token in tokens:
        if token not in VENUE_STOPWORDS:
            return token

    return lowered


def instrument_from_venue(raw_venue: str) -> str:
    lowered = str(raw_venue).strip().lower()
    if not lowered:
        return "unknown"

    tokens = [t for t in re.split(r"[^a-z0-9]+", lowered) if t]
    token_set = set(tokens)

    if token_set & INSTRUMENT_KEYWORDS["perp"]:
        return "perp"
    if token_set & INSTRUMENT_KEYWORDS["dex"]:
        return "dex"
    if token_set & INSTRUMENT_KEYWORDS["spot"]:
        return "spot"

    if "jupiter" in lowered or "uniswap" in lowered:
        return "dex"
    return "spot"


def _as_non_negative(value: Any, fallback: float) -> float:
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return fallback


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text())
    except Exception:
        return fallback


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build execution fee table template from candidates")
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return p.parse_args()


def baseline_for(venue: str, instrument: str) -> dict[str, float]:
    from_venue = VENUE_BASELINES.get((venue, instrument))
    if from_venue:
        return dict(from_venue)
    return dict(DEFAULT_INSTRUMENT_FEES.get(instrument, DEFAULT_INSTRUMENT_FEES["unknown"]))


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
        instrument = str(row.get("instrument", "")).strip().lower() or "unknown"
        if venue:
            existing_rules[(venue, instrument)] = row

    seen_pairs: set[tuple[str, str]] = set()
    for item in candidates:
        if not isinstance(item, dict):
            continue

        buy_venue = canonical_venue(item.get("buy_venue", ""))
        buy_instr = instrument_from_venue(item.get("buy_venue", ""))
        sell_venue = canonical_venue(item.get("sell_venue", ""))
        sell_instr = instrument_from_venue(item.get("sell_venue", ""))

        seen_pairs.add((buy_venue, buy_instr))
        seen_pairs.add((sell_venue, sell_instr))

    merged_rules: list[dict[str, Any]] = []
    for key in sorted(seen_pairs):
        if key in existing_rules:
            merged_rules.append(existing_rules[key])
            continue

        venue, instrument = key
        baseline = baseline_for(venue, instrument)
        merged_rules.append(
            {
                "venue": venue,
                "instrument": instrument,
                **baseline,
                "source": "template_baseline",
            }
        )

    # Keep manual entries even if current universe doesn't contain them.
    for key, row in sorted(existing_rules.items()):
        if key not in seen_pairs:
            merged_rules.append(row)

    defaults = existing.get("defaults", {}) if isinstance(existing.get("defaults"), dict) else {}
    defaults_out: dict[str, Any] = {}
    for instrument in ["spot", "perp", "dex", "unknown"]:
        bucket = defaults.get(instrument, {}) if isinstance(defaults.get(instrument), dict) else {}
        baseline = DEFAULT_INSTRUMENT_FEES[instrument]
        defaults_out[instrument] = {
            "taker_bps": _as_non_negative(bucket.get("taker_bps"), baseline["taker_bps"]),
            "maker_bps": _as_non_negative(bucket.get("maker_bps"), baseline["maker_bps"]),
            "maker_vip_bps": _as_non_negative(bucket.get("maker_vip_bps"), baseline["maker_vip_bps"]),
        }

    strategy_multiplier = dict(DEFAULT_STRATEGY_ROUNDTRIP_SIDE_MULTIPLIER)
    existing_multiplier = defaults.get("strategy_roundtrip_side_multiplier", {})
    if isinstance(existing_multiplier, dict):
        for k, v in existing_multiplier.items():
            strategy_multiplier[str(k)] = _as_non_negative(v, strategy_multiplier.get(str(k), 1.0))
    defaults_out["strategy_roundtrip_side_multiplier"] = strategy_multiplier

    profile_mode = dict(DEFAULT_PROFILE_FEE_MODE)
    existing_profile_mode = existing.get("profile_fee_mode", {})
    if isinstance(existing_profile_mode, dict):
        for k, v in existing_profile_mode.items():
            mode = str(v).strip().lower()
            if mode in {"taker", "maker", "maker_vip"}:
                profile_mode[str(k)] = mode

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": "execution_fee_table_v1",
        "defaults": defaults_out,
        "profile_fee_mode": profile_mode,
        "rules": merged_rules,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2))

    print(f"Loaded candidates: {len(candidates)}")
    print(f"Fee rules: {len(merged_rules)}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
