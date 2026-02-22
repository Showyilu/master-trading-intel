#!/usr/bin/env python3
"""Build live CEX-DEX arbitrage candidates using Binance/Bybit + Jupiter quotes.

Outputs:
- data/normalized_quotes_dex_latest.json
- data/opportunity_candidates.cex_dex.live.json
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEX_QUOTES_OUT = ROOT / "data" / "normalized_quotes_dex_latest.json"
DEFAULT_CANDIDATES_OUT = ROOT / "data" / "opportunity_candidates.cex_dex.live.json"
DEFAULT_NETWORK_FRICTION_PATH = ROOT / "data" / "network_friction.latest.json"

BINANCE_URL = "https://api.binance.com/api/v3/ticker/bookTicker"
BYBIT_URL = "https://api.bybit.com/v5/market/tickers?category=spot"
JUP_QUOTE_URL = "https://lite-api.jup.ag/swap/v1/quote"

USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDC_DECIMALS = 6

TAKER_FEE_BPS = {
    "binance": 7.5,
    "bybit": 10.0,
}
DEFAULT_DEX_ROUTER_FEE_BPS = 4.0

TOKENS = [
    {
        "symbol": "SOLUSDT",
        "base": "SOL",
        "mint": "So11111111111111111111111111111111111111112",
        "decimals": 9,
    },
    {
        "symbol": "BTCUSDT",
        "base": "BTC",
        "mint": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
        "decimals": 6,
    },
]


def _http_get_json(url: str, timeout: int = 15) -> dict | list:
    req = urllib.request.Request(url, headers={"User-Agent": "master-trading-intel/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _safe_float(value: str | int | float | None) -> float | None:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v <= 0:
        return None
    return v


def _impact_bps(raw: str | float | int | None) -> float:
    try:
        pct_as_fraction = float(raw)
    except (TypeError, ValueError):
        return 0.0
    if pct_as_fraction <= 0:
        return 0.0
    return pct_as_fraction * 10_000


def load_jupiter_fee_model(network_friction_path: Path, fallback_router_fee_bps: float) -> tuple[float, float, str]:
    router_fee_bps = max(0.0, float(fallback_router_fee_bps))
    network_fee_bps = 0.0
    source = "static_router_fee"

    if not network_friction_path.exists():
        return router_fee_bps, network_fee_bps, source

    try:
        payload = json.loads(network_friction_path.read_text())
    except Exception:
        return router_fee_bps, network_fee_bps, source

    if not isinstance(payload, dict):
        return router_fee_bps, network_fee_bps, source

    override = payload.get("dex_fee_overrides", {}).get("jupiter", {})
    if not isinstance(override, dict):
        return router_fee_bps, network_fee_bps, source

    router_fee_bps = max(0.0, _safe_float(override.get("router_fee_bps")) or router_fee_bps)
    network_fee_bps = max(0.0, _safe_float(override.get("network_fee_bps")) or 0.0)

    version = str(payload.get("version", "unknown")).strip() or "unknown"
    source = f"network_friction:{version}"
    return router_fee_bps, network_fee_bps, source


def fetch_cex_quotes(symbols: set[str]) -> dict[str, dict[str, dict[str, float]]]:
    out: dict[str, dict[str, dict[str, float]]] = {"binance": {}, "bybit": {}}

    binance_payload = _http_get_json(BINANCE_URL)
    for row in binance_payload:
        symbol = row.get("symbol")
        if symbol not in symbols:
            continue
        bid = _safe_float(row.get("bidPrice"))
        ask = _safe_float(row.get("askPrice"))
        if bid is None or ask is None or ask <= bid:
            continue
        mid = (bid + ask) / 2
        spread_bps = ((ask - bid) / mid) * 10_000
        out["binance"][symbol] = {
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "spread_bps": spread_bps,
        }

    bybit_payload = _http_get_json(BYBIT_URL)
    for row in bybit_payload.get("result", {}).get("list", []):
        symbol = row.get("symbol")
        if symbol not in symbols:
            continue
        bid = _safe_float(row.get("bid1Price"))
        ask = _safe_float(row.get("ask1Price"))
        if bid is None or ask is None or ask <= bid:
            continue
        mid = (bid + ask) / 2
        spread_bps = ((ask - bid) / mid) * 10_000
        out["bybit"][symbol] = {
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "spread_bps": spread_bps,
        }

    return out


def fetch_jupiter_quote(input_mint: str, output_mint: str, amount_atomic: int, slippage_bps: int) -> dict:
    query = urllib.parse.urlencode(
        {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount_atomic),
            "slippageBps": str(slippage_bps),
            "restrictIntermediateTokens": "true",
        }
    )
    return _http_get_json(f"{JUP_QUOTE_URL}?{query}")


def build_dex_quote(run_at: str, token: dict, ref_mid: float, size_usd: float, slippage_bps: int) -> dict | None:
    base_decimals = token["decimals"]

    # Size base leg from USD notional anchored by CEX mid.
    base_amount = max(0.0001, size_usd / ref_mid)
    base_amount_atomic = int(base_amount * (10**base_decimals))
    usdc_amount_atomic = int(size_usd * (10**USDC_DECIMALS))

    if base_amount_atomic <= 0 or usdc_amount_atomic <= 0:
        return None

    sell_quote = fetch_jupiter_quote(token["mint"], USDC_MINT, base_amount_atomic, slippage_bps)
    buy_quote = fetch_jupiter_quote(USDC_MINT, token["mint"], usdc_amount_atomic, slippage_bps)

    out_usdc_atomic = _safe_float(sell_quote.get("outAmount"))
    out_base_atomic = _safe_float(buy_quote.get("outAmount"))
    if out_usdc_atomic is None or out_base_atomic is None:
        return None

    out_usdc = out_usdc_atomic / (10**USDC_DECIMALS)
    out_base = out_base_atomic / (10**base_decimals)
    if out_usdc <= 0 or out_base <= 0:
        return None

    dex_bid = out_usdc / base_amount  # sell base -> receive USDC
    dex_ask = size_usd / out_base  # spend USDC -> receive base
    dex_mid = (dex_bid + dex_ask) / 2
    raw_spread_bps = ((dex_ask - dex_bid) / dex_mid) * 10_000
    dex_spread_bps = max(0.0, raw_spread_bps)
    crossed_quote = raw_spread_bps < -1.0
    reference_deviation_bps = abs(dex_mid - ref_mid) / ref_mid * 10_000

    sell_impact_bps = _impact_bps(sell_quote.get("priceImpactPct"))
    buy_impact_bps = _impact_bps(buy_quote.get("priceImpactPct"))

    return {
        "detected_at": run_at,
        "venue": "jupiter",
        "market": "solana-spot",
        "symbol": f"{token['base']}/USDC",
        "base": token["base"],
        "quote": "USDC",
        "bid_price": round(dex_bid, 10),
        "ask_price": round(dex_ask, 10),
        "mid_price": round(dex_mid, 10),
        "spread_bps": round(dex_spread_bps, 6),
        "raw_spread_bps": round(raw_spread_bps, 6),
        "crossed_quote": crossed_quote,
        "buy_leg_price_impact_bps": round(buy_impact_bps, 6),
        "sell_leg_price_impact_bps": round(sell_impact_bps, 6),
        "route_hops_buy": len(buy_quote.get("routePlan", [])),
        "route_hops_sell": len(sell_quote.get("routePlan", [])),
        "cex_reference_mid": round(ref_mid, 10),
        "reference_deviation_bps": round(reference_deviation_bps, 6),
        "scan_size_usd": round(size_usd, 2),
    }


def build_candidates(
    run_at: str,
    cex_quotes: dict[str, dict[str, dict[str, float]]],
    dex_quotes_by_symbol: dict[str, dict],
    size_usd: float,
    transfer_delay_min: float,
    min_gross_edge_bps: float,
    max_ref_deviation_bps: float,
    dex_router_fee_bps: float,
    dex_network_fee_bps: float,
    dex_fee_source: str,
) -> list[dict]:
    candidates: list[dict] = []
    dex_total_fee_bps = max(0.0, dex_router_fee_bps) + max(0.0, dex_network_fee_bps)

    for token in TOKENS:
        symbol = token["symbol"]
        base = token["base"]
        dex = dex_quotes_by_symbol.get(symbol)
        if not dex:
            continue

        if dex.get("reference_deviation_bps", 0) > max_ref_deviation_bps:
            continue
        if dex.get("crossed_quote"):
            continue

        dex_bid = dex["bid_price"]
        dex_ask = dex["ask_price"]
        dex_spread = dex["spread_bps"]
        dex_impact = (dex["buy_leg_price_impact_bps"] + dex["sell_leg_price_impact_bps"]) / 2

        for venue, venue_quotes in cex_quotes.items():
            cex = venue_quotes.get(symbol)
            if not cex:
                continue

            cex_bid = cex["bid"]
            cex_ask = cex["ask"]
            cex_spread = cex["spread_bps"]

            # Direction 1: buy on DEX, sell on CEX.
            gross_1 = ((cex_bid - dex_ask) / dex_ask) * 10_000
            if gross_1 >= min_gross_edge_bps:
                slippage_1 = 0.55 * cex_spread + 0.65 * dex_spread + 0.5 * dex_impact + 0.8
                latency_1 = 2.4 + max(0.0, 10.0 - gross_1) * 0.08
                candidates.append(
                    {
                        "detected_at": run_at,
                        "strategy_type": "cex_dex",
                        "symbol": f"{base}/USDT",
                        "buy_venue": "jupiter",
                        "sell_venue": venue,
                        "gross_edge_bps": round(gross_1, 6),
                        "fees_bps": round(dex_total_fee_bps + TAKER_FEE_BPS[venue], 6),
                        "slippage_bps": round(slippage_1, 6),
                        "latency_risk_bps": round(latency_1, 6),
                        "transfer_delay_min": round(transfer_delay_min, 4),
                        "size_usd": round(size_usd, 2),
                        "notes": (
                            f"buy_dex_sell_cex dex_ask={dex_ask:.8f} cex_bid={cex_bid:.8f} "
                            f"dex_spread={dex_spread:.2f}bps dex_impact={dex_impact:.2f}bps "
                            f"dex_router_fee={dex_router_fee_bps:.4f}bps dex_network_fee={dex_network_fee_bps:.6f}bps source={dex_fee_source}"
                        ),
                    }
                )

            # Direction 2: buy on CEX, sell on DEX.
            gross_2 = ((dex_bid - cex_ask) / cex_ask) * 10_000
            if gross_2 >= min_gross_edge_bps:
                slippage_2 = 0.55 * cex_spread + 0.65 * dex_spread + 0.5 * dex_impact + 0.8
                latency_2 = 2.4 + max(0.0, 10.0 - gross_2) * 0.08
                candidates.append(
                    {
                        "detected_at": run_at,
                        "strategy_type": "cex_dex",
                        "symbol": f"{base}/USDT",
                        "buy_venue": venue,
                        "sell_venue": "jupiter",
                        "gross_edge_bps": round(gross_2, 6),
                        "fees_bps": round(dex_total_fee_bps + TAKER_FEE_BPS[venue], 6),
                        "slippage_bps": round(slippage_2, 6),
                        "latency_risk_bps": round(latency_2, 6),
                        "transfer_delay_min": round(transfer_delay_min, 4),
                        "size_usd": round(size_usd, 2),
                        "notes": (
                            f"buy_cex_sell_dex cex_ask={cex_ask:.8f} dex_bid={dex_bid:.8f} "
                            f"dex_spread={dex_spread:.2f}bps dex_impact={dex_impact:.2f}bps "
                            f"dex_router_fee={dex_router_fee_bps:.4f}bps dex_network_fee={dex_network_fee_bps:.6f}bps source={dex_fee_source}"
                        ),
                    }
                )

    return sorted(candidates, key=lambda x: x["gross_edge_bps"], reverse=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build CEX-DEX live candidates (Binance/Bybit vs Jupiter).")
    p.add_argument("--size-usd", type=float, default=5000.0, help="Notional size for quoting and friction model")
    p.add_argument("--slippage-bps", type=int, default=30, help="Jupiter quote slippage setting")
    p.add_argument("--transfer-delay-min", type=float, default=12.0, help="Conservative cross-venue transfer delay")
    p.add_argument("--min-gross-edge-bps", type=float, default=0.2, help="Drop directions below this gross edge")
    p.add_argument(
        "--max-ref-deviation-bps",
        type=float,
        default=400.0,
        help="Reject DEX quotes that drift too far from CEX reference mid",
    )
    p.add_argument(
        "--network-friction",
        type=Path,
        default=DEFAULT_NETWORK_FRICTION_PATH,
        help="Network friction model JSON to load dynamic DEX fee adjustments",
    )
    p.add_argument(
        "--dex-router-fee-bps",
        type=float,
        default=DEFAULT_DEX_ROUTER_FEE_BPS,
        help="Fallback Jupiter router fee bps when no network model exists",
    )
    p.add_argument("--dex-quotes-out", type=Path, default=DEFAULT_DEX_QUOTES_OUT)
    p.add_argument("--candidates-out", type=Path, default=DEFAULT_CANDIDATES_OUT)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_at = datetime.now(tz=timezone.utc).isoformat()

    symbols = {token["symbol"] for token in TOKENS}
    cex_quotes = fetch_cex_quotes(symbols)

    dex_router_fee_bps, dex_network_fee_bps, dex_fee_source = load_jupiter_fee_model(
        args.network_friction,
        fallback_router_fee_bps=args.dex_router_fee_bps,
    )

    dex_quotes: list[dict] = []
    dex_quotes_by_symbol: dict[str, dict] = {}

    for token in TOKENS:
        symbol = token["symbol"]
        mids = [
            venue_quotes[symbol]["mid"]
            for venue_quotes in cex_quotes.values()
            if symbol in venue_quotes
        ]
        if not mids:
            continue

        ref_mid = sum(mids) / len(mids)
        try:
            dex = build_dex_quote(run_at, token, ref_mid, args.size_usd, args.slippage_bps)
        except Exception:
            dex = None

        if not dex:
            continue

        dex_quotes.append(dex)
        dex_quotes_by_symbol[symbol] = dex

    candidates = build_candidates(
        run_at=run_at,
        cex_quotes=cex_quotes,
        dex_quotes_by_symbol=dex_quotes_by_symbol,
        size_usd=args.size_usd,
        transfer_delay_min=args.transfer_delay_min,
        min_gross_edge_bps=args.min_gross_edge_bps,
        max_ref_deviation_bps=args.max_ref_deviation_bps,
        dex_router_fee_bps=dex_router_fee_bps,
        dex_network_fee_bps=dex_network_fee_bps,
        dex_fee_source=dex_fee_source,
    )

    args.dex_quotes_out.parent.mkdir(parents=True, exist_ok=True)
    args.candidates_out.parent.mkdir(parents=True, exist_ok=True)
    args.dex_quotes_out.write_text(json.dumps(dex_quotes, indent=2))
    args.candidates_out.write_text(json.dumps(candidates, indent=2))

    rejected_by_reference = sum(1 for q in dex_quotes if q.get("reference_deviation_bps", 0) > args.max_ref_deviation_bps)
    rejected_by_cross = sum(1 for q in dex_quotes if q.get("crossed_quote"))

    print(f"DEX quotes normalized: {len(dex_quotes)}")
    print(f"DEX quotes rejected by reference guard: {rejected_by_reference}")
    print(f"DEX quotes rejected by crossed-book guard: {rejected_by_cross}")
    print(
        "Jupiter fee model: router={:.4f}bps, network={:.6f}bps, total={:.6f}bps ({})".format(
            dex_router_fee_bps,
            dex_network_fee_bps,
            dex_router_fee_bps + dex_network_fee_bps,
            dex_fee_source,
        )
    )
    print(f"CEX-DEX candidates built: {len(candidates)}")
    print(f"Wrote: {args.dex_quotes_out}")
    print(f"Wrote: {args.candidates_out}")


if __name__ == "__main__":
    main()
