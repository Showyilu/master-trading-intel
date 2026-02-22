#!/usr/bin/env python3
"""Build live funding/basis carry candidates from Binance + Bybit perp markets.

Pipeline:
1) Pull latest funding snapshots from Binance Futures + Bybit Linear Perp.
2) Normalize funding rows into a common schema-like payload.
3) Build market-neutral cross-venue carry candidates with explicit friction fields.

Outputs:
- data/normalized_funding_latest.json
- data/opportunity_candidates.funding.live.json
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FUNDING_OUT = ROOT / "data" / "normalized_funding_latest.json"
DEFAULT_CANDIDATES_OUT = ROOT / "data" / "opportunity_candidates.funding.live.json"

BINANCE_FUNDING_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
BYBIT_FUNDING_URL = "https://api.bybit.com/v5/market/tickers?category=linear"

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

# Conservative taker-fee assumptions for perp execution, round-trip (open+close handled in candidate builder).
PERP_TAKER_FEE_BPS = {
    "binance": 5.0,
    "bybit": 5.5,
}

# Per-side execution impact assumption (entry or exit, single leg).
PERP_SLIPPAGE_PER_SIDE_BPS = {
    "binance": 1.4,
    "bybit": 1.8,
}


@dataclass
class FundingQuote:
    detected_at: str
    venue: str
    market: str
    symbol: str
    base: str
    quote: str
    mark_price: float
    funding_rate: float
    funding_rate_bps: float
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


def fetch_binance_funding() -> dict[str, dict[str, float | int]]:
    payload = _http_get_json(BINANCE_FUNDING_URL)
    out: dict[str, dict[str, float | int]] = {}

    for row in payload:
        symbol = row.get("symbol")
        if not symbol:
            continue

        funding_rate = _safe_float(row.get("lastFundingRate"))
        mark_price = _safe_float(row.get("markPrice"))
        next_funding_ms = _safe_int(row.get("nextFundingTime"))
        if funding_rate is None or mark_price is None or next_funding_ms is None:
            continue

        out[symbol] = {
            "funding_rate": funding_rate,
            "mark_price": mark_price,
            "next_funding_ms": next_funding_ms,
        }

    return out


def fetch_bybit_funding() -> dict[str, dict[str, float | int]]:
    payload = _http_get_json(BYBIT_FUNDING_URL)
    rows = payload.get("result", {}).get("list", [])
    out: dict[str, dict[str, float | int]] = {}

    for row in rows:
        symbol = row.get("symbol")
        if not symbol:
            continue

        funding_rate = _safe_float(row.get("fundingRate"))
        mark_price = _safe_float(row.get("markPrice"))
        next_funding_ms = _safe_int(row.get("nextFundingTime"))
        if funding_rate is None or mark_price is None or next_funding_ms is None:
            continue

        out[symbol] = {
            "funding_rate": funding_rate,
            "mark_price": mark_price,
            "next_funding_ms": next_funding_ms,
        }

    return out


def normalize_funding(
    run_at: str,
    now_ms: int,
    symbols: list[str],
    binance: dict[str, dict[str, float | int]],
    bybit: dict[str, dict[str, float | int]],
) -> list[FundingQuote]:
    normalized: list[FundingQuote] = []

    for venue, source in (("binance", binance), ("bybit", bybit)):
        for symbol in symbols:
            row = source.get(symbol)
            if not row:
                continue

            parsed = _parse_symbol(symbol)
            if not parsed:
                continue
            base, quote = parsed

            next_funding_ms = int(row["next_funding_ms"])
            funding_rate = float(row["funding_rate"])
            mark_price = float(row["mark_price"])

            normalized.append(
                FundingQuote(
                    detected_at=run_at,
                    venue=venue,
                    market="perp",
                    symbol=f"{base}/{quote}",
                    base=base,
                    quote=quote,
                    mark_price=round(mark_price, 10),
                    funding_rate=round(funding_rate, 10),
                    funding_rate_bps=round(funding_rate * 10_000, 6),
                    next_funding_time=_iso_from_ms(next_funding_ms),
                    minutes_to_funding=round(_minutes_to(now_ms, next_funding_ms), 4),
                )
            )

    return normalized


def _build_candidate(
    run_at: str,
    symbol: str,
    long_venue: str,
    short_venue: str,
    long_row: dict[str, float | int],
    short_row: dict[str, float | int],
    size_usd: float,
    min_gross_edge_bps: float,
) -> dict | None:
    long_rate = float(long_row["funding_rate"])
    short_rate = float(short_row["funding_rate"])

    # Positive means this long/short pairing expects to RECEIVE net funding at next cycle.
    gross_edge_bps = (short_rate - long_rate) * 10_000
    if gross_edge_bps < min_gross_edge_bps:
        return None

    long_next_ms = int(long_row["next_funding_ms"])
    short_next_ms = int(short_row["next_funding_ms"])
    hold_minutes = max(long_next_ms, short_next_ms) - int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    hold_minutes = max(0.0, hold_minutes / 60_000)

    funding_skew_min = abs(long_next_ms - short_next_ms) / 60_000

    fees_bps = 2 * (PERP_TAKER_FEE_BPS[long_venue] + PERP_TAKER_FEE_BPS[short_venue])
    slippage_bps = 2 * (
        PERP_SLIPPAGE_PER_SIDE_BPS[long_venue] + PERP_SLIPPAGE_PER_SIDE_BPS[short_venue]
    )

    # Exposure risk grows with hold time and with venue funding-time skew.
    latency_risk_bps = 0.75 + (hold_minutes / 60) * 0.35 + max(0.0, funding_skew_min - 5.0) * 0.06

    return {
        "detected_at": run_at,
        "strategy_type": "funding_carry_cex_cex",
        "symbol": symbol.replace("USDT", "/USDT"),
        "buy_venue": f"long_{long_venue}_perp",
        "sell_venue": f"short_{short_venue}_perp",
        "gross_edge_bps": round(gross_edge_bps, 6),
        "fees_bps": round(fees_bps, 6),
        "slippage_bps": round(slippage_bps, 6),
        "latency_risk_bps": round(latency_risk_bps, 6),
        "transfer_delay_min": 1.0,
        "size_usd": round(size_usd, 2),
        "notes": (
            f"funding_diff_bps=(short {short_venue} {short_rate * 10000:.3f} - "
            f"long {long_venue} {long_rate * 10000:.3f}); "
            f"hold_min={hold_minutes:.2f}; skew_min={funding_skew_min:.2f}; "
            f"mark_long={float(long_row['mark_price']):.6f}; mark_short={float(short_row['mark_price']):.6f}"
        ),
    }


def build_candidates(
    run_at: str,
    symbols: list[str],
    binance: dict[str, dict[str, float | int]],
    bybit: dict[str, dict[str, float | int]],
    size_usd: float,
    min_gross_edge_bps: float,
) -> list[dict]:
    out: list[dict] = []

    for symbol in symbols:
        b = binance.get(symbol)
        y = bybit.get(symbol)
        if not b or not y:
            continue

        c1 = _build_candidate(
            run_at=run_at,
            symbol=symbol,
            long_venue="binance",
            short_venue="bybit",
            long_row=b,
            short_row=y,
            size_usd=size_usd,
            min_gross_edge_bps=min_gross_edge_bps,
        )
        if c1:
            out.append(c1)

        c2 = _build_candidate(
            run_at=run_at,
            symbol=symbol,
            long_venue="bybit",
            short_venue="binance",
            long_row=y,
            short_row=b,
            size_usd=size_usd,
            min_gross_edge_bps=min_gross_edge_bps,
        )
        if c2:
            out.append(c2)

    return sorted(out, key=lambda row: row["gross_edge_bps"], reverse=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build live funding carry candidates (Binance + Bybit perp).")
    p.add_argument("--symbols", nargs="*", default=DEFAULT_SYMBOLS)
    p.add_argument("--size-usd", type=float, default=10_000)
    p.add_argument("--min-gross-edge-bps", type=float, default=0.4)
    p.add_argument("--funding-out", type=Path, default=DEFAULT_FUNDING_OUT)
    p.add_argument("--candidates-out", type=Path, default=DEFAULT_CANDIDATES_OUT)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_at = datetime.now(tz=timezone.utc).isoformat()
    now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)

    symbols = sorted(set(args.symbols))

    binance = fetch_binance_funding()
    bybit = fetch_bybit_funding()

    normalized_funding = normalize_funding(
        run_at=run_at,
        now_ms=now_ms,
        symbols=symbols,
        binance=binance,
        bybit=bybit,
    )

    candidates = build_candidates(
        run_at=run_at,
        symbols=symbols,
        binance=binance,
        bybit=bybit,
        size_usd=args.size_usd,
        min_gross_edge_bps=args.min_gross_edge_bps,
    )

    args.funding_out.parent.mkdir(parents=True, exist_ok=True)
    args.candidates_out.parent.mkdir(parents=True, exist_ok=True)

    args.funding_out.write_text(json.dumps([asdict(row) for row in normalized_funding], indent=2))
    args.candidates_out.write_text(json.dumps(candidates, indent=2))

    print(f"Funding rows normalized: {len(normalized_funding)}")
    print(f"Candidates built: {len(candidates)}")
    print(f"Wrote: {args.funding_out}")
    print(f"Wrote: {args.candidates_out}")


if __name__ == "__main__":
    main()
