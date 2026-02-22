#!/usr/bin/env python3
"""Build live network-friction model for DEX execution costs.

Current scope:
- Solana: recent prioritization fees + base tx fee, translated into USD/bps for Jupiter roundtrip.
- Polygon: gas-station maxFee estimate translated to USD/bps for 2-leg AMM roundtrip.
- Ethereum: beaconcha.in gas estimate translated to USD/bps for 2-leg AMM roundtrip.

This output is a reusable input for candidate builders so DEX fees are not a static guess.
"""

from __future__ import annotations

import argparse
import json
import statistics
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "network_friction.latest.json"

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
POLYGON_GAS_URL = "https://gasstation.polygon.technology/v2"
ETH_GAS_URL = "https://beaconcha.in/api/v1/execution/gasnow"
BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/bookTicker"

FALLBACK_USD = {
    "SOLUSDT": 150.0,
    "ETHUSDT": 2500.0,
    "MATICUSDT": 0.9,
}


def _http_get_json(url: str, timeout: int = 15) -> dict[str, Any] | list[Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "master-trading-intel/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_post_json(url: str, payload: dict[str, Any], timeout: int = 15) -> dict[str, Any] | list[Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": "master-trading-intel/0.1",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ranked = sorted(values)
    if len(ranked) == 1:
        return ranked[0]
    idx = (len(ranked) - 1) * max(0.0, min(1.0, q))
    lo = int(idx)
    hi = min(lo + 1, len(ranked) - 1)
    frac = idx - lo
    return ranked[lo] * (1.0 - frac) + ranked[hi] * frac


def _fetch_mid_price_map() -> tuple[dict[str, float], list[str]]:
    symbols_needed = set(FALLBACK_USD.keys())
    out: dict[str, float] = {}
    warnings: list[str] = []

    try:
        rows = _http_get_json(BINANCE_TICKER_URL)
        if isinstance(rows, list):
            for row in rows:
                symbol = str(row.get("symbol", ""))
                if symbol not in symbols_needed:
                    continue
                bid = _as_float(row.get("bidPrice"), 0.0)
                ask = _as_float(row.get("askPrice"), 0.0)
                if bid > 0 and ask > 0 and ask >= bid:
                    out[symbol] = (bid + ask) / 2.0
    except Exception as exc:
        warnings.append(f"binance_price_fetch_failed: {exc}")

    for symbol, fallback in FALLBACK_USD.items():
        if symbol not in out:
            out[symbol] = fallback
            warnings.append(f"{symbol}_fallback_used")

    return out, warnings


def _bps(cost_usd: float, size_usd: float) -> float:
    if size_usd <= 0:
        return 0.0
    return max(0.0, (cost_usd / size_usd) * 10_000.0)


def build_solana_model(size_usd: float, sol_usd: float, dex_tx_legs: int, compute_units_per_leg: int) -> dict[str, Any]:
    source = "live"
    warnings: list[str] = []
    base_fee_lamports = 5_000
    priority_micro_lamports_per_cu = 0.0
    p75_micro_lamports_per_cu = 0.0

    try:
        payload = _http_post_json(
            SOLANA_RPC_URL,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getRecentPrioritizationFees",
                "params": [[]],
            },
        )
        rows = payload.get("result", []) if isinstance(payload, dict) else []
        fee_samples = [
            _as_float(row.get("prioritizationFee"), 0.0)
            for row in rows
            if isinstance(row, dict)
        ]
        fee_samples = [x for x in fee_samples if x >= 0]
        if fee_samples:
            priority_micro_lamports_per_cu = statistics.median(fee_samples)
            p75_micro_lamports_per_cu = _percentile(fee_samples, 0.75)
        else:
            warnings.append("solana_priority_fee_samples_empty")
    except Exception as exc:
        source = "fallback"
        warnings.append(f"solana_priority_fee_fetch_failed: {exc}")

    priority_lamports_per_leg = (priority_micro_lamports_per_cu * compute_units_per_leg) / 1_000_000.0
    total_lamports_roundtrip = dex_tx_legs * (base_fee_lamports + priority_lamports_per_leg)
    total_sol = total_lamports_roundtrip / 1_000_000_000.0
    cost_usd = total_sol * sol_usd

    return {
        "source": source,
        "base_fee_lamports_per_tx": base_fee_lamports,
        "priority_micro_lamports_per_cu_median": round(priority_micro_lamports_per_cu, 6),
        "priority_micro_lamports_per_cu_p75": round(p75_micro_lamports_per_cu, 6),
        "compute_units_per_leg": int(compute_units_per_leg),
        "dex_roundtrip_tx_legs": int(dex_tx_legs),
        "sol_usd": round(sol_usd, 8),
        "estimated_cost_usd_roundtrip": round(cost_usd, 8),
        "estimated_cost_bps_roundtrip": round(_bps(cost_usd, size_usd), 8),
        "warnings": warnings,
    }


def build_polygon_model(size_usd: float, matic_usd: float, dex_tx_legs: int, gas_units_per_leg: int) -> dict[str, Any]:
    source = "live"
    warnings: list[str] = []
    max_fee_gwei = 120.0

    try:
        payload = _http_get_json(POLYGON_GAS_URL)
        if isinstance(payload, dict):
            standard = payload.get("standard", {})
            max_fee_gwei = _as_float(standard.get("maxFee"), max_fee_gwei)
            if max_fee_gwei <= 0:
                max_fee_gwei = 120.0
                warnings.append("polygon_max_fee_invalid_fallback_used")
        else:
            source = "fallback"
            warnings.append("polygon_payload_not_object")
    except Exception as exc:
        source = "fallback"
        warnings.append(f"polygon_gas_fetch_failed: {exc}")

    total_gas_units = dex_tx_legs * gas_units_per_leg
    cost_native = max_fee_gwei * 1e-9 * total_gas_units
    cost_usd = cost_native * matic_usd

    return {
        "source": source,
        "max_fee_gwei": round(max_fee_gwei, 8),
        "gas_units_per_leg": int(gas_units_per_leg),
        "dex_roundtrip_tx_legs": int(dex_tx_legs),
        "matic_usd": round(matic_usd, 8),
        "estimated_cost_usd_roundtrip": round(cost_usd, 8),
        "estimated_cost_bps_roundtrip": round(_bps(cost_usd, size_usd), 8),
        "warnings": warnings,
    }


def build_eth_model(size_usd: float, eth_usd: float, dex_tx_legs: int, gas_units_per_leg: int) -> dict[str, Any]:
    source = "live"
    warnings: list[str] = []
    gas_wei = 30_000_000_000.0

    try:
        payload = _http_get_json(ETH_GAS_URL)
        if isinstance(payload, dict):
            data = payload.get("data", {})
            # endpoint reports integer-like values; assume wei and convert below.
            gas_wei = _as_float(data.get("standard"), gas_wei)
            if gas_wei <= 0:
                gas_wei = 30_000_000_000.0
                warnings.append("eth_gas_invalid_fallback_used")
        else:
            source = "fallback"
            warnings.append("eth_payload_not_object")
    except Exception as exc:
        source = "fallback"
        warnings.append(f"eth_gas_fetch_failed: {exc}")

    gas_gwei = gas_wei / 1e9
    total_gas_units = dex_tx_legs * gas_units_per_leg
    cost_eth = gas_gwei * 1e-9 * total_gas_units
    cost_usd = cost_eth * eth_usd

    return {
        "source": source,
        "standard_gas_wei": round(gas_wei, 4),
        "standard_gas_gwei": round(gas_gwei, 8),
        "gas_units_per_leg": int(gas_units_per_leg),
        "dex_roundtrip_tx_legs": int(dex_tx_legs),
        "eth_usd": round(eth_usd, 8),
        "estimated_cost_usd_roundtrip": round(cost_usd, 8),
        "estimated_cost_bps_roundtrip": round(_bps(cost_usd, size_usd), 8),
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build network friction model for DEX execution")
    p.add_argument("--size-usd", type=float, default=5000.0)
    p.add_argument("--dex-roundtrip-tx-legs", type=int, default=2)
    p.add_argument("--solana-compute-units-per-leg", type=int, default=250_000)
    p.add_argument("--evm-gas-units-per-leg", type=int, default=180_000)
    p.add_argument("--jupiter-router-fee-bps", type=float, default=4.0)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_at = datetime.now(tz=timezone.utc).isoformat()

    prices, price_warnings = _fetch_mid_price_map()

    sol_model = build_solana_model(
        size_usd=args.size_usd,
        sol_usd=prices["SOLUSDT"],
        dex_tx_legs=args.dex_roundtrip_tx_legs,
        compute_units_per_leg=args.solana_compute_units_per_leg,
    )
    polygon_model = build_polygon_model(
        size_usd=args.size_usd,
        matic_usd=prices["MATICUSDT"],
        dex_tx_legs=args.dex_roundtrip_tx_legs,
        gas_units_per_leg=args.evm_gas_units_per_leg,
    )
    eth_model = build_eth_model(
        size_usd=args.size_usd,
        eth_usd=prices["ETHUSDT"],
        dex_tx_legs=args.dex_roundtrip_tx_legs,
        gas_units_per_leg=args.evm_gas_units_per_leg,
    )

    jupiter_network_bps = sol_model["estimated_cost_bps_roundtrip"]

    out = {
        "generated_at": run_at,
        "version": "network_friction_v1",
        "size_usd": round(args.size_usd, 4),
        "assumptions": {
            "dex_roundtrip_tx_legs": int(args.dex_roundtrip_tx_legs),
            "solana_compute_units_per_leg": int(args.solana_compute_units_per_leg),
            "evm_gas_units_per_leg": int(args.evm_gas_units_per_leg),
        },
        "market_refs": {
            "SOLUSDT": round(prices["SOLUSDT"], 8),
            "ETHUSDT": round(prices["ETHUSDT"], 8),
            "MATICUSDT": round(prices["MATICUSDT"], 8),
        },
        "dex_fee_overrides": {
            "jupiter": {
                "router_fee_bps": round(max(0.0, float(args.jupiter_router_fee_bps)), 8),
                "network_fee_bps": round(jupiter_network_bps, 8),
                "total_fee_bps": round(max(0.0, float(args.jupiter_router_fee_bps)) + jupiter_network_bps, 8),
                "network_model": "solana",
            }
        },
        "networks": {
            "solana": sol_model,
            "polygon": polygon_model,
            "ethereum": eth_model,
        },
        "warnings": price_warnings,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2))

    print(f"Wrote: {args.output}")
    print(
        "Jupiter fee bps => router={:.4f}, network={:.6f}, total={:.6f}".format(
            out["dex_fee_overrides"]["jupiter"]["router_fee_bps"],
            out["dex_fee_overrides"]["jupiter"]["network_fee_bps"],
            out["dex_fee_overrides"]["jupiter"]["total_fee_bps"],
        )
    )


if __name__ == "__main__":
    main()
