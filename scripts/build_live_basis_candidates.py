#!/usr/bin/env python3
"""Build live perp-spot basis candidates (same venue) from Binance + Bybit.

Pipeline:
1) Pull spot top-of-book and perp mark/funding snapshots.
2) Normalize perp-spot basis rows into a common payload.
3) Build conservative basis-carry candidates with explicit friction fields.

Outputs:
- data/normalized_basis_latest.json
- data/opportunity_candidates.basis.live.json
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASIS_OUT = ROOT / "data" / "normalized_basis_latest.json"
DEFAULT_CANDIDATES_OUT = ROOT / "data" / "opportunity_candidates.basis.live.json"

BINANCE_SPOT_URL = "https://api.binance.com/api/v3/ticker/bookTicker"
BINANCE_PERP_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
BYBIT_SPOT_URL = "https://api.bybit.com/v5/market/tickers?category=spot"
BYBIT_PERP_URL = "https://api.bybit.com/v5/market/tickers?category=linear"

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

SPOT_TAKER_FEE_BPS = {
    "binance": 7.5,
    "bybit": 10.0,
}

PERP_TAKER_FEE_BPS = {
    "binance": 5.0,
    "bybit": 5.5,
}

SPOT_SLIPPAGE_PER_SIDE_BPS = {
    "binance": 1.0,
    "bybit": 1.3,
}

PERP_SLIPPAGE_PER_SIDE_BPS = {
    "binance": 1.4,
    "bybit": 1.8,
}


@dataclass
class BasisQuote:
    detected_at: str
    venue: str
    symbol: str
    base: str
    quote: str
    spot_bid_price: float
    spot_ask_price: float
    spot_mid_price: float
    perp_bid_price: float
    perp_ask_price: float
    perp_mark_price: float
    perp_index_price: float
    funding_rate: float
    funding_rate_bps: float
    basis_mark_to_spot_bps: float
    basis_index_to_spot_bps: float
    next_funding_time: str
    minutes_to_funding: float


def _http_get_json(url: str, timeout: int = 12) -> dict | list:
    req = urllib.request.Request(url, headers={"User-Agent": "master-trading-intel/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _safe_float(value: str | float | int) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out


def _safe_int(value: str | int | float) -> int | None:
    try:
        out = int(value)
    except (TypeError, ValueError):
        return None
    return out


def _parse_symbol(symbol: str) -> tuple[str, str] | None:
    for quote in ("USDT", "USDC"):
        if symbol.endswith(quote) and len(symbol) > len(quote):
            return symbol[: -len(quote)], quote
    return None


def _iso_from_ms(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).isoformat()


def _minutes_to(now_ms: int, future_ms: int) -> float:
    return max(0.0, (future_ms - now_ms) / 60_000)


def fetch_binance_spot() -> dict[str, dict[str, float]]:
    payload = _http_get_json(BINANCE_SPOT_URL)
    out: dict[str, dict[str, float]] = {}

    for row in payload:
        symbol = row.get("symbol")
        bid = _safe_float(row.get("bidPrice"))
        ask = _safe_float(row.get("askPrice"))
        if not symbol or bid is None or ask is None or ask <= bid:
            continue
        out[symbol] = {"bid": bid, "ask": ask}

    return out


def fetch_bybit_spot() -> dict[str, dict[str, float]]:
    payload = _http_get_json(BYBIT_SPOT_URL)
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


def fetch_binance_perp() -> dict[str, dict[str, float | int]]:
    payload = _http_get_json(BINANCE_PERP_URL)
    out: dict[str, dict[str, float | int]] = {}

    for row in payload:
        symbol = row.get("symbol")
        if not symbol:
            continue

        mark = _safe_float(row.get("markPrice"))
        index = _safe_float(row.get("indexPrice"))
        funding_rate = _safe_float(row.get("lastFundingRate"))
        next_funding_ms = _safe_int(row.get("nextFundingTime"))

        if mark is None or index is None or funding_rate is None or next_funding_ms is None:
            continue

        out[symbol] = {
            "mark": mark,
            "index": index,
            "funding_rate": funding_rate,
            "next_funding_ms": next_funding_ms,
        }

    return out


def fetch_bybit_perp() -> dict[str, dict[str, float | int]]:
    payload = _http_get_json(BYBIT_PERP_URL)
    rows = payload.get("result", {}).get("list", [])
    out: dict[str, dict[str, float | int]] = {}

    for row in rows:
        symbol = row.get("symbol")
        if not symbol:
            continue

        bid = _safe_float(row.get("bid1Price"))
        ask = _safe_float(row.get("ask1Price"))
        mark = _safe_float(row.get("markPrice"))
        index = _safe_float(row.get("indexPrice"))
        funding_rate = _safe_float(row.get("fundingRate"))
        next_funding_ms = _safe_int(row.get("nextFundingTime"))

        if (
            bid is None
            or ask is None
            or ask <= bid
            or mark is None
            or index is None
            or funding_rate is None
            or next_funding_ms is None
        ):
            continue

        out[symbol] = {
            "bid": bid,
            "ask": ask,
            "mark": mark,
            "index": index,
            "funding_rate": funding_rate,
            "next_funding_ms": next_funding_ms,
        }

    return out


def normalize_basis(
    run_at: str,
    now_ms: int,
    symbols: list[str],
    binance_spot: dict[str, dict[str, float]],
    bybit_spot: dict[str, dict[str, float]],
    binance_perp: dict[str, dict[str, float | int]],
    bybit_perp: dict[str, dict[str, float | int]],
) -> list[BasisQuote]:
    normalized: list[BasisQuote] = []

    venue_sources = {
        "binance": {
            "spot": binance_spot,
            "perp": binance_perp,
        },
        "bybit": {
            "spot": bybit_spot,
            "perp": bybit_perp,
        },
    }

    for venue, source in venue_sources.items():
        for symbol in symbols:
            spot = source["spot"].get(symbol)
            perp = source["perp"].get(symbol)
            if not spot or not perp:
                continue

            parsed = _parse_symbol(symbol)
            if not parsed:
                continue
            base, quote = parsed

            spot_bid = float(spot["bid"])
            spot_ask = float(spot["ask"])
            spot_mid = (spot_bid + spot_ask) / 2

            if venue == "binance":
                perp_mark = float(perp["mark"])
                perp_index = float(perp["index"])
                # Binance premiumIndex endpoint does not provide perp top-of-book directly.
                perp_bid = perp_mark
                perp_ask = perp_mark
            else:
                perp_bid = float(perp["bid"])
                perp_ask = float(perp["ask"])
                perp_mark = float(perp["mark"])
                perp_index = float(perp["index"])

            funding_rate = float(perp["funding_rate"])
            funding_rate_bps = funding_rate * 10_000
            next_funding_ms = int(perp["next_funding_ms"])

            basis_mark_bps = ((perp_mark - spot_mid) / spot_mid) * 10_000
            basis_index_bps = ((perp_index - spot_mid) / spot_mid) * 10_000

            normalized.append(
                BasisQuote(
                    detected_at=run_at,
                    venue=venue,
                    symbol=f"{base}/{quote}",
                    base=base,
                    quote=quote,
                    spot_bid_price=round(spot_bid, 10),
                    spot_ask_price=round(spot_ask, 10),
                    spot_mid_price=round(spot_mid, 10),
                    perp_bid_price=round(perp_bid, 10),
                    perp_ask_price=round(perp_ask, 10),
                    perp_mark_price=round(perp_mark, 10),
                    perp_index_price=round(perp_index, 10),
                    funding_rate=round(funding_rate, 10),
                    funding_rate_bps=round(funding_rate_bps, 6),
                    basis_mark_to_spot_bps=round(basis_mark_bps, 6),
                    basis_index_to_spot_bps=round(basis_index_bps, 6),
                    next_funding_time=_iso_from_ms(next_funding_ms),
                    minutes_to_funding=round(_minutes_to(now_ms, next_funding_ms), 4),
                )
            )

    return normalized


def _build_candidate(
    run_at: str,
    row: BasisQuote,
    size_usd: float,
    min_gross_edge_bps: float,
    basis_capture_ratio: float,
    inventory_mode: str,
) -> dict | None:
    basis_bps = row.basis_mark_to_spot_bps
    funding_bps = row.funding_rate_bps

    if basis_bps >= 0:
        # Perp premium: short perp + long spot.
        buy_venue = f"long_{row.venue}_spot"
        sell_venue = f"short_{row.venue}_perp"
        direction = "cash_and_carry"
        funding_edge_bps = funding_bps
    else:
        # Perp discount: long perp + short spot.
        buy_venue = f"long_{row.venue}_perp"
        sell_venue = f"short_{row.venue}_spot"
        direction = "reverse_carry"
        funding_edge_bps = -funding_bps

    basis_capture_bps = abs(basis_bps) * basis_capture_ratio
    gross_edge_bps = basis_capture_bps + funding_edge_bps

    if gross_edge_bps < min_gross_edge_bps:
        return None

    spot_fee = SPOT_TAKER_FEE_BPS[row.venue]
    perp_fee = PERP_TAKER_FEE_BPS[row.venue]

    # Entry + exit on both legs.
    fees_bps = 2 * (spot_fee + perp_fee)

    spot_slip = SPOT_SLIPPAGE_PER_SIDE_BPS[row.venue]
    perp_slip = PERP_SLIPPAGE_PER_SIDE_BPS[row.venue]
    slippage_bps = 2 * (spot_slip + perp_slip)

    if inventory_mode == "prepositioned":
        transfer_delay_min = 0.25
    else:
        transfer_delay_min = 5.0

    latency_risk_bps = 0.7 + (row.minutes_to_funding / 60) * 0.2 + abs(basis_bps) * 0.015

    return {
        "detected_at": run_at,
        "strategy_type": "perp_spot_basis",
        "symbol": row.symbol,
        "buy_venue": buy_venue,
        "sell_venue": sell_venue,
        "gross_edge_bps": round(gross_edge_bps, 6),
        "fees_bps": round(fees_bps, 6),
        "slippage_bps": round(slippage_bps, 6),
        "latency_risk_bps": round(latency_risk_bps, 6),
        "transfer_delay_min": round(transfer_delay_min, 4),
        "size_usd": round(size_usd, 2),
        "notes": (
            f"{direction}; venue={row.venue}; basis_mark={basis_bps:.3f}bps; "
            f"funding={funding_bps:.3f}bps; basis_capture_ratio={basis_capture_ratio:.2f}; "
            f"basis_capture={basis_capture_bps:.3f}bps; funding_component={funding_edge_bps:.3f}bps; "
            f"minutes_to_funding={row.minutes_to_funding:.2f}; inventory_mode={inventory_mode}"
        ),
    }


def build_candidates(
    run_at: str,
    normalized_basis: list[BasisQuote],
    size_usd: float,
    min_gross_edge_bps: float,
    basis_capture_ratio: float,
    inventory_mode: str,
) -> list[dict]:
    out: list[dict] = []

    for row in normalized_basis:
        candidate = _build_candidate(
            run_at=run_at,
            row=row,
            size_usd=size_usd,
            min_gross_edge_bps=min_gross_edge_bps,
            basis_capture_ratio=basis_capture_ratio,
            inventory_mode=inventory_mode,
        )
        if candidate:
            out.append(candidate)

    return sorted(out, key=lambda x: x["gross_edge_bps"], reverse=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build live perp-spot basis candidates (Binance + Bybit).")
    p.add_argument("--symbols", nargs="*", default=DEFAULT_SYMBOLS)
    p.add_argument("--size-usd", type=float, default=10_000)
    p.add_argument(
        "--basis-capture-ratio",
        type=float,
        default=0.22,
        help="Conservative fraction of observed basis assumed capturable in next cycle.",
    )
    p.add_argument("--min-gross-edge-bps", type=float, default=0.2)
    p.add_argument(
        "--inventory-mode",
        choices=["prepositioned", "transfer"],
        default="prepositioned",
        help="Transfer delay assumption for spot/perp inventory.",
    )
    p.add_argument("--basis-out", type=Path, default=DEFAULT_BASIS_OUT)
    p.add_argument("--candidates-out", type=Path, default=DEFAULT_CANDIDATES_OUT)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_at = datetime.now(tz=timezone.utc).isoformat()
    now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)

    symbols = sorted(set(args.symbols))

    binance_spot = fetch_binance_spot()
    bybit_spot = fetch_bybit_spot()
    binance_perp = fetch_binance_perp()
    bybit_perp = fetch_bybit_perp()

    normalized_basis = normalize_basis(
        run_at=run_at,
        now_ms=now_ms,
        symbols=symbols,
        binance_spot=binance_spot,
        bybit_spot=bybit_spot,
        binance_perp=binance_perp,
        bybit_perp=bybit_perp,
    )

    candidates = build_candidates(
        run_at=run_at,
        normalized_basis=normalized_basis,
        size_usd=args.size_usd,
        min_gross_edge_bps=args.min_gross_edge_bps,
        basis_capture_ratio=max(0.0, min(args.basis_capture_ratio, 1.0)),
        inventory_mode=args.inventory_mode,
    )

    args.basis_out.parent.mkdir(parents=True, exist_ok=True)
    args.candidates_out.parent.mkdir(parents=True, exist_ok=True)

    args.basis_out.write_text(json.dumps([asdict(row) for row in normalized_basis], indent=2))
    args.candidates_out.write_text(json.dumps(candidates, indent=2))

    print(f"Basis rows normalized: {len(normalized_basis)}")
    print(f"Candidates built: {len(candidates)}")
    print(f"Wrote: {args.basis_out}")
    print(f"Wrote: {args.candidates_out}")


if __name__ == "__main__":
    main()
