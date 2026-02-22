#!/usr/bin/env python3
"""Build normalized live CEX quotes and CEX-CEX arb candidates.

Pipeline:
1) Pull top-of-book quotes from Binance Spot + Bybit Spot.
2) Normalize to quote records.
3) Construct directional arb candidates with explicit edge/friction fields.

Output files:
- data/normalized_quotes_cex_latest.json
- data/opportunity_candidates.live.json
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUOTES_OUT = ROOT / "data" / "normalized_quotes_cex_latest.json"
DEFAULT_CANDIDATES_OUT = ROOT / "data" / "opportunity_candidates.live.json"

BINANCE_URL = "https://api.binance.com/api/v3/ticker/bookTicker"
BYBIT_URL = "https://api.bybit.com/v5/market/tickers?category=spot"

DEFAULT_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "BNBUSDT",
    "ADAUSDT",
    "LINKUSDT",
    "LTCUSDT",
    "AVAXUSDT",
]

TAKER_FEE_BPS = {
    "binance": 7.5,
    "bybit": 10.0,
}


@dataclass
class Quote:
    detected_at: str
    venue: str
    market: str
    symbol: str
    base: str
    quote: str
    bid_price: float
    ask_price: float
    mid_price: float
    spread_bps: float


def _http_get_json(url: str, timeout: int = 12) -> dict | list:
    req = urllib.request.Request(url, headers={"User-Agent": "master-trading-intel/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _parse_symbol(symbol: str) -> tuple[str, str] | None:
    for q in ("USDT", "USDC"):
        if symbol.endswith(q) and len(symbol) > len(q):
            return symbol[: -len(q)], q
    return None


def _safe_float(value: str | float | int) -> float | None:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v <= 0:
        return None
    return v


def fetch_binance_quotes() -> dict[str, dict[str, float]]:
    payload = _http_get_json(BINANCE_URL)
    out: dict[str, dict[str, float]] = {}
    for row in payload:
        symbol = row.get("symbol")
        bid = _safe_float(row.get("bidPrice"))
        ask = _safe_float(row.get("askPrice"))
        if not symbol or bid is None or ask is None or ask <= bid:
            continue
        out[symbol] = {"bid": bid, "ask": ask}
    return out


def fetch_bybit_quotes() -> dict[str, dict[str, float]]:
    payload = _http_get_json(BYBIT_URL)
    rows = payload.get("result", {}).get("list", [])
    out: dict[str, dict[str, float]] = {}
    for row in rows:
        symbol = row.get("symbol")
        bid = _safe_float(row.get("bid1Price"))
        ask = _safe_float(row.get("ask1Price"))
        if not symbol or bid is None or ask is None or ask <= bid:
            continue
        out[symbol] = {"bid": bid, "ask": ask}
    return out


def normalize_quotes(
    run_at: str,
    symbols: list[str],
    binance: dict[str, dict[str, float]],
    bybit: dict[str, dict[str, float]],
) -> list[Quote]:
    normalized: list[Quote] = []

    for venue, source in (("binance", binance), ("bybit", bybit)):
        for symbol in symbols:
            row = source.get(symbol)
            if not row:
                continue
            parsed = _parse_symbol(symbol)
            if not parsed:
                continue
            base, quote_ccy = parsed
            bid = row["bid"]
            ask = row["ask"]
            mid = (bid + ask) / 2
            spread_bps = ((ask - bid) / mid) * 10_000

            normalized.append(
                Quote(
                    detected_at=run_at,
                    venue=venue,
                    market="spot",
                    symbol=f"{base}/{quote_ccy}",
                    base=base,
                    quote=quote_ccy,
                    bid_price=round(bid, 10),
                    ask_price=round(ask, 10),
                    mid_price=round(mid, 10),
                    spread_bps=round(spread_bps, 6),
                )
            )

    return normalized


def _build_candidate(
    run_at: str,
    symbol: str,
    buy_venue: str,
    sell_venue: str,
    buy_ask: float,
    sell_bid: float,
    buy_spread_bps: float,
    sell_spread_bps: float,
    size_usd: float,
    transfer_delay_min: float,
    min_gross_edge_bps: float,
) -> dict | None:
    gross_edge_bps = ((sell_bid - buy_ask) / buy_ask) * 10_000
    if gross_edge_bps < min_gross_edge_bps:
        return None

    fees_bps = TAKER_FEE_BPS[buy_venue] + TAKER_FEE_BPS[sell_venue]
    # Conservative friction: half-spread impact on both legs + fixed execution buffer.
    slippage_bps = 0.55 * buy_spread_bps + 0.55 * sell_spread_bps + 1.20
    latency_risk_bps = 0.8 + max(0.0, 8.0 - gross_edge_bps) * 0.10

    return {
        "detected_at": run_at,
        "strategy_type": "cex_cex",
        "symbol": symbol,
        "buy_venue": buy_venue,
        "sell_venue": sell_venue,
        "gross_edge_bps": round(gross_edge_bps, 6),
        "fees_bps": round(fees_bps, 6),
        "slippage_bps": round(slippage_bps, 6),
        "latency_risk_bps": round(latency_risk_bps, 6),
        "transfer_delay_min": round(transfer_delay_min, 4),
        "size_usd": round(size_usd, 2),
        "notes": (
            f"live_top_of_book buy_ask={buy_ask:.8f}, sell_bid={sell_bid:.8f}, "
            f"buy_spread={buy_spread_bps:.3f}bps, sell_spread={sell_spread_bps:.3f}bps"
        ),
    }


def build_candidates(
    run_at: str,
    normalized_quotes: list[Quote],
    size_usd: float,
    transfer_delay_min: float,
    min_gross_edge_bps: float,
) -> list[dict]:
    by_symbol_venue: dict[str, dict[str, Quote]] = {}
    for q in normalized_quotes:
        by_symbol_venue.setdefault(q.symbol, {})[q.venue] = q

    candidates: list[dict] = []
    for symbol, venue_quotes in sorted(by_symbol_venue.items()):
        bq = venue_quotes.get("binance")
        yq = venue_quotes.get("bybit")
        if not bq or not yq:
            continue

        # Direction A: buy binance, sell bybit
        c1 = _build_candidate(
            run_at=run_at,
            symbol=symbol,
            buy_venue="binance",
            sell_venue="bybit",
            buy_ask=bq.ask_price,
            sell_bid=yq.bid_price,
            buy_spread_bps=bq.spread_bps,
            sell_spread_bps=yq.spread_bps,
            size_usd=size_usd,
            transfer_delay_min=transfer_delay_min,
            min_gross_edge_bps=min_gross_edge_bps,
        )
        if c1:
            candidates.append(c1)

        # Direction B: buy bybit, sell binance
        c2 = _build_candidate(
            run_at=run_at,
            symbol=symbol,
            buy_venue="bybit",
            sell_venue="binance",
            buy_ask=yq.ask_price,
            sell_bid=bq.bid_price,
            buy_spread_bps=yq.spread_bps,
            sell_spread_bps=bq.spread_bps,
            size_usd=size_usd,
            transfer_delay_min=transfer_delay_min,
            min_gross_edge_bps=min_gross_edge_bps,
        )
        if c2:
            candidates.append(c2)

    return sorted(candidates, key=lambda x: x["gross_edge_bps"], reverse=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build live CEX-CEX opportunity candidates.")
    p.add_argument("--symbols", nargs="*", default=DEFAULT_SYMBOLS, help="Symbols like BTCUSDT ETHUSDT")
    p.add_argument("--size-usd", type=float, default=10_000, help="Assumed scan size in USD")
    p.add_argument("--transfer-delay-min", type=float, default=5.0, help="Estimated transfer delay minutes")
    p.add_argument("--min-gross-edge-bps", type=float, default=0.2, help="Drop directions below this gross edge")
    p.add_argument("--quotes-out", type=Path, default=DEFAULT_QUOTES_OUT)
    p.add_argument("--candidates-out", type=Path, default=DEFAULT_CANDIDATES_OUT)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_at = datetime.now(tz=timezone.utc).isoformat()

    binance = fetch_binance_quotes()
    bybit = fetch_bybit_quotes()

    symbols = sorted(set(args.symbols))
    normalized_quotes = normalize_quotes(run_at, symbols, binance, bybit)
    candidates = build_candidates(
        run_at=run_at,
        normalized_quotes=normalized_quotes,
        size_usd=args.size_usd,
        transfer_delay_min=args.transfer_delay_min,
        min_gross_edge_bps=args.min_gross_edge_bps,
    )

    args.quotes_out.parent.mkdir(parents=True, exist_ok=True)
    args.candidates_out.parent.mkdir(parents=True, exist_ok=True)

    args.quotes_out.write_text(json.dumps([asdict(q) for q in normalized_quotes], indent=2))
    args.candidates_out.write_text(json.dumps(candidates, indent=2))

    print(f"Quotes normalized: {len(normalized_quotes)}")
    print(f"Candidates built: {len(candidates)}")
    print(f"Wrote: {args.quotes_out}")
    print(f"Wrote: {args.candidates_out}")


if __name__ == "__main__":
    main()
