#!/usr/bin/env python3
"""Build normalized live CEX quotes and CEX-CEX arb candidates.

Pipeline:
1) Pull top-of-book quotes from Binance Spot + Bybit Spot.
2) Pull orderbook depth for both venues.
3) Build size-aware slippage curves (USD tiers).
4) Construct directional arb candidates with explicit edge/friction fields.

Output files:
- data/normalized_quotes_cex_latest.json
- data/cex_depth_slippage_latest.json
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
DEFAULT_DEPTH_OUT = ROOT / "data" / "cex_depth_slippage_latest.json"
DEFAULT_CANDIDATES_OUT = ROOT / "data" / "opportunity_candidates.live.json"

BINANCE_URL = "https://api.binance.com/api/v3/ticker/bookTicker"
BYBIT_URL = "https://api.bybit.com/v5/market/tickers?category=spot"
BINANCE_DEPTH_URL = "https://api.binance.com/api/v3/depth?symbol={symbol}&limit=100"
BYBIT_DEPTH_URL = "https://api.bybit.com/v5/market/orderbook?category=spot&symbol={symbol}&limit=200"

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
DEFAULT_SIZE_TIERS_USD = [1000.0, 5000.0, 10000.0]

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


def fetch_binance_orderbook(symbol: str) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    payload = _http_get_json(BINANCE_DEPTH_URL.format(symbol=symbol))
    bids: list[tuple[float, float]] = []
    asks: list[tuple[float, float]] = []

    for row in payload.get("bids", []):
        if len(row) < 2:
            continue
        price = _safe_float(row[0])
        qty = _safe_float(row[1])
        if price is None or qty is None:
            continue
        bids.append((price, qty))

    for row in payload.get("asks", []):
        if len(row) < 2:
            continue
        price = _safe_float(row[0])
        qty = _safe_float(row[1])
        if price is None or qty is None:
            continue
        asks.append((price, qty))

    bids.sort(key=lambda x: x[0], reverse=True)
    asks.sort(key=lambda x: x[0])
    return bids, asks


def fetch_bybit_orderbook(symbol: str) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    payload = _http_get_json(BYBIT_DEPTH_URL.format(symbol=symbol))
    result = payload.get("result", {})

    bids: list[tuple[float, float]] = []
    asks: list[tuple[float, float]] = []

    for row in result.get("b", []):
        if len(row) < 2:
            continue
        price = _safe_float(row[0])
        qty = _safe_float(row[1])
        if price is None or qty is None:
            continue
        bids.append((price, qty))

    for row in result.get("a", []):
        if len(row) < 2:
            continue
        price = _safe_float(row[0])
        qty = _safe_float(row[1])
        if price is None or qty is None:
            continue
        asks.append((price, qty))

    bids.sort(key=lambda x: x[0], reverse=True)
    asks.sort(key=lambda x: x[0])
    return bids, asks


def _calc_buy_slippage_bps(mid_price: float, asks: list[tuple[float, float]], size_usd: float) -> float | None:
    target_quote = size_usd
    spent_quote = 0.0
    bought_base = 0.0

    for price, qty in asks:
        level_quote = price * qty
        take_quote = min(target_quote - spent_quote, level_quote)
        if take_quote <= 0:
            break
        take_base = take_quote / price
        spent_quote += take_quote
        bought_base += take_base
        if spent_quote >= target_quote:
            break

    if spent_quote < target_quote or bought_base <= 0:
        return None

    avg_exec = spent_quote / bought_base
    return max(0.0, (avg_exec / mid_price - 1.0) * 10_000)


def _calc_sell_slippage_bps(mid_price: float, bids: list[tuple[float, float]], size_usd: float) -> float | None:
    target_base = size_usd / mid_price
    sold_base = 0.0
    received_quote = 0.0

    for price, qty in bids:
        take_base = min(target_base - sold_base, qty)
        if take_base <= 0:
            break
        received_quote += take_base * price
        sold_base += take_base
        if sold_base >= target_base:
            break

    if sold_base < target_base or sold_base <= 0:
        return None

    avg_exec = received_quote / sold_base
    return max(0.0, (1.0 - avg_exec / mid_price) * 10_000)


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


def build_depth_slippage(
    symbols: list[str],
    normalized_quotes: list[Quote],
    size_tiers_usd: list[float],
) -> dict[str, dict[str, dict]]:
    mid_lookup: dict[str, dict[str, float]] = {}
    for q in normalized_quotes:
        sym = q.base + q.quote
        mid_lookup.setdefault(sym, {})[q.venue] = q.mid_price

    out: dict[str, dict[str, dict]] = {}

    for symbol in symbols:
        out[symbol] = {}
        for venue in ("binance", "bybit"):
            mid = mid_lookup.get(symbol, {}).get(venue)
            if mid is None:
                continue

            try:
                if venue == "binance":
                    bids, asks = fetch_binance_orderbook(symbol)
                else:
                    bids, asks = fetch_bybit_orderbook(symbol)
            except Exception:
                continue

            tier_rows: list[dict] = []
            tier_lookup: dict[str, dict[str, float]] = {}
            for size in size_tiers_usd:
                buy_slip = _calc_buy_slippage_bps(mid, asks, size)
                sell_slip = _calc_sell_slippage_bps(mid, bids, size)

                tier_rows.append(
                    {
                        "size_usd": round(size, 2),
                        "buy_slippage_bps": round(buy_slip, 6) if buy_slip is not None else None,
                        "sell_slippage_bps": round(sell_slip, 6) if sell_slip is not None else None,
                    }
                )

                tier_lookup[f"{int(size)}"] = {
                    "buy_slippage_bps": round(buy_slip, 6) if buy_slip is not None else None,
                    "sell_slippage_bps": round(sell_slip, 6) if sell_slip is not None else None,
                }

            out[symbol][venue] = {
                "mid_price": round(mid, 10),
                "book_levels": {"bids": len(bids), "asks": len(asks)},
                "slippage_bps_by_tier": tier_rows,
                "slippage_lookup": tier_lookup,
            }

    return out


def _resolve_depth_slippage(
    depth_slippage: dict[str, dict[str, dict]],
    symbol: str,
    venue: str,
    size_usd: float,
    side: str,
) -> tuple[float | None, str | None]:
    venue_payload = depth_slippage.get(symbol, {}).get(venue)
    if not venue_payload:
        return None, None

    tiers = venue_payload.get("slippage_bps_by_tier", [])
    if not tiers:
        return None, None

    best = min(tiers, key=lambda row: abs(float(row["size_usd"]) - size_usd))
    key = "buy_slippage_bps" if side == "buy" else "sell_slippage_bps"
    value = best.get(key)
    if value is None:
        return None, None
    return float(value), f"{int(float(best['size_usd']))}"


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
    depth_slippage: dict[str, dict[str, dict]],
) -> dict | None:
    gross_edge_bps = ((sell_bid - buy_ask) / buy_ask) * 10_000
    if gross_edge_bps < min_gross_edge_bps:
        return None

    fees_bps = TAKER_FEE_BPS[buy_venue] + TAKER_FEE_BPS[sell_venue]

    buy_depth_slip, buy_tier = _resolve_depth_slippage(depth_slippage, symbol, buy_venue, size_usd, "buy")
    sell_depth_slip, sell_tier = _resolve_depth_slippage(depth_slippage, symbol, sell_venue, size_usd, "sell")

    if buy_depth_slip is not None and sell_depth_slip is not None:
        slippage_bps = buy_depth_slip + sell_depth_slip + 0.80
        slip_model_note = (
            f"depth_model tiers buy={buy_tier} sell={sell_tier}, "
            f"buy_depth={buy_depth_slip:.3f}bps sell_depth={sell_depth_slip:.3f}bps"
        )
    else:
        slippage_bps = 0.55 * buy_spread_bps + 0.55 * sell_spread_bps + 1.20
        slip_model_note = "fallback_top_of_book_spread_model"

    latency_risk_bps = 0.8 + max(0.0, 8.0 - gross_edge_bps) * 0.10

    return {
        "detected_at": run_at,
        "strategy_type": "cex_cex",
        "symbol": symbol.replace("USDT", "/USDT"),
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
            f"buy_spread={buy_spread_bps:.3f}bps, sell_spread={sell_spread_bps:.3f}bps; "
            f"slippage={slip_model_note}"
        ),
    }


def build_candidates(
    run_at: str,
    symbols: list[str],
    normalized_quotes: list[Quote],
    size_usd: float,
    transfer_delay_min: float,
    min_gross_edge_bps: float,
    depth_slippage: dict[str, dict[str, dict]],
) -> list[dict]:
    by_symbol_venue: dict[str, dict[str, Quote]] = {}
    for q in normalized_quotes:
        symbol_raw = q.base + q.quote
        by_symbol_venue.setdefault(symbol_raw, {})[q.venue] = q

    candidates: list[dict] = []
    for symbol in symbols:
        venue_quotes = by_symbol_venue.get(symbol, {})
        bq = venue_quotes.get("binance")
        yq = venue_quotes.get("bybit")
        if not bq or not yq:
            continue

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
            depth_slippage=depth_slippage,
        )
        if c1:
            candidates.append(c1)

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
            depth_slippage=depth_slippage,
        )
        if c2:
            candidates.append(c2)

    return sorted(candidates, key=lambda x: x["gross_edge_bps"], reverse=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build live CEX-CEX opportunity candidates.")
    p.add_argument("--symbols", nargs="*", default=DEFAULT_SYMBOLS, help="Symbols like BTCUSDT ETHUSDT")
    p.add_argument("--size-usd", type=float, default=10_000, help="Assumed scan size in USD")
    p.add_argument(
        "--size-tiers-usd",
        nargs="*",
        type=float,
        default=DEFAULT_SIZE_TIERS_USD,
        help="USD tiers for orderbook slippage curve (e.g. 1000 5000 10000)",
    )
    p.add_argument("--transfer-delay-min", type=float, default=5.0, help="Estimated transfer delay minutes")
    p.add_argument("--min-gross-edge-bps", type=float, default=0.2, help="Drop directions below this gross edge")
    p.add_argument("--quotes-out", type=Path, default=DEFAULT_QUOTES_OUT)
    p.add_argument("--depth-out", type=Path, default=DEFAULT_DEPTH_OUT)
    p.add_argument("--candidates-out", type=Path, default=DEFAULT_CANDIDATES_OUT)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_at = datetime.now(tz=timezone.utc).isoformat()

    binance = fetch_binance_quotes()
    bybit = fetch_bybit_quotes()

    symbols = sorted(set(args.symbols))
    normalized_quotes = normalize_quotes(run_at, symbols, binance, bybit)

    size_tiers_usd = sorted({float(x) for x in args.size_tiers_usd if x > 0})
    depth_slippage = build_depth_slippage(
        symbols=symbols,
        normalized_quotes=normalized_quotes,
        size_tiers_usd=size_tiers_usd,
    )

    candidates = build_candidates(
        run_at=run_at,
        symbols=symbols,
        normalized_quotes=normalized_quotes,
        size_usd=args.size_usd,
        transfer_delay_min=args.transfer_delay_min,
        min_gross_edge_bps=args.min_gross_edge_bps,
        depth_slippage=depth_slippage,
    )

    depth_payload = {
        "generated_at": run_at,
        "size_tiers_usd": [round(x, 2) for x in size_tiers_usd],
        "symbols": depth_slippage,
    }

    args.quotes_out.parent.mkdir(parents=True, exist_ok=True)
    args.depth_out.parent.mkdir(parents=True, exist_ok=True)
    args.candidates_out.parent.mkdir(parents=True, exist_ok=True)

    args.quotes_out.write_text(json.dumps([asdict(q) for q in normalized_quotes], indent=2))
    args.depth_out.write_text(json.dumps(depth_payload, indent=2))
    args.candidates_out.write_text(json.dumps(candidates, indent=2))

    venues_covered = sum(len(v) for v in depth_slippage.values())

    print(f"Quotes normalized: {len(normalized_quotes)}")
    print(f"Depth models built: {venues_covered}")
    print(f"Candidates built: {len(candidates)}")
    print(f"Wrote: {args.quotes_out}")
    print(f"Wrote: {args.depth_out}")
    print(f"Wrote: {args.candidates_out}")


if __name__ == "__main__":
    main()
