#!/usr/bin/env python3
"""Overlay execution constraints with authenticated account snapshots.

Goal:
- Keep `data/execution_constraints.latest.json` as the single reproducible constraints file.
- Replace template `available_inventory_usd` with account-realized balances
  (Binance + Bybit) when credentials are available.
- Extend Binance overlay into borrow/rate terms:
  - `max_borrow_usd` from `/sapi/v1/margin/maxBorrowable`
  - `borrow_rate_bps_per_hour` from `/sapi/v1/margin/next-hourly-interest-rate`
- Update `max_position_usd` conservatively as:
    min(existing_max_position_usd, available_inventory_usd + max_borrow_usd)
- Fail soft: if auth is missing or an API call fails, keep template constraints.

Environment variables:
- BINANCE_API_KEY / BINANCE_API_SECRET
- BYBIT_API_KEY / BYBIT_API_SECRET
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONSTRAINTS = ROOT / "data" / "execution_constraints.latest.json"
DEFAULT_QUOTES = ROOT / "data" / "normalized_quotes_cex_latest.json"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Overlay constraints with authenticated balances")
    p.add_argument("--constraints", type=Path, default=DEFAULT_CONSTRAINTS)
    p.add_argument("--quotes", type=Path, default=DEFAULT_QUOTES)
    p.add_argument("--timeout-sec", type=float, default=8.0)
    p.add_argument("--min-inventory-usd", type=float, default=1.0)
    return p.parse_args()


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text())
    except Exception:
        return fallback


def _http_get_json(url: str, headers: dict[str, str], timeout_sec: float) -> Any:
    req = urllib.request.Request(url=url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _binance_signed_get(
    path: str,
    params: dict[str, Any],
    api_key: str,
    api_secret: str,
    timeout_sec: float,
) -> Any:
    payload = dict(params)
    payload["timestamp"] = int(time.time() * 1000)
    payload["recvWindow"] = 5000
    query = urllib.parse.urlencode(payload)
    signature = hmac.new(api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
    url = f"https://api.binance.com{path}?{query}&signature={signature}"
    return _http_get_json(url, headers={"X-MBX-APIKEY": api_key}, timeout_sec=timeout_sec)


def _bybit_signed_get(
    path: str,
    params: dict[str, Any],
    api_key: str,
    api_secret: str,
    timeout_sec: float,
) -> Any:
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    query = urllib.parse.urlencode(params)
    pre_sign = f"{timestamp}{api_key}{recv_window}{query}"
    sign = hmac.new(api_secret.encode("utf-8"), pre_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": sign,
    }
    url = f"https://api.bybit.com{path}?{query}"
    return _http_get_json(url, headers=headers, timeout_sec=timeout_sec)


def _to_float(raw: Any, fallback: float = 0.0) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        return fallback


def _chunk(items: list[str], size: int) -> list[list[str]]:
    if size <= 0:
        return [items]
    return [items[i : i + size] for i in range(0, len(items), size)]


def build_price_map(quotes: list[dict[str, Any]]) -> dict[str, float]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for row in quotes:
        if not isinstance(row, dict):
            continue
        base = str(row.get("base", "")).strip().upper()
        quote = str(row.get("quote", "")).strip().upper()
        mid = _to_float(row.get("mid_price", 0), 0.0)
        if not base or not quote or mid <= 0:
            continue
        if quote in {"USDT", "USDC", "USD"}:
            buckets[base].append(mid)

    out: dict[str, float] = {
        "USD": 1.0,
        "USDT": 1.0,
        "USDC": 1.0,
    }
    for asset, arr in buckets.items():
        if not arr:
            continue
        arr_sorted = sorted(arr)
        out[asset] = arr_sorted[len(arr_sorted) // 2]
    return out


def fetch_binance_inventory_usd(
    api_key: str,
    api_secret: str,
    price_map: dict[str, float],
    timeout_sec: float,
    min_inventory_usd: float,
) -> dict[str, float]:
    payload = _binance_signed_get(
        "/api/v3/account",
        {},
        api_key=api_key,
        api_secret=api_secret,
        timeout_sec=timeout_sec,
    )
    rows = payload.get("balances", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        return {}

    out: dict[str, float] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        asset = str(row.get("asset", "")).strip().upper()
        if not asset:
            continue
        qty = _to_float(row.get("free", 0), 0.0) + _to_float(row.get("locked", 0), 0.0)
        if qty <= 0:
            continue
        px = price_map.get(asset)
        if px is None:
            continue
        usd = qty * px
        if usd < min_inventory_usd:
            continue
        out[asset] = round(max(0.0, usd), 6)
    return out


def fetch_bybit_inventory_usd(
    api_key: str,
    api_secret: str,
    price_map: dict[str, float],
    timeout_sec: float,
    min_inventory_usd: float,
) -> dict[str, float]:
    payload = _bybit_signed_get(
        "/v5/account/wallet-balance",
        {"accountType": "UNIFIED"},
        api_key=api_key,
        api_secret=api_secret,
        timeout_sec=timeout_sec,
    )
    if not isinstance(payload, dict) or int(payload.get("retCode", -1)) != 0:
        return {}

    result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
    lists = result.get("list", []) if isinstance(result.get("list"), list) else []

    out: dict[str, float] = {}
    for block in lists:
        if not isinstance(block, dict):
            continue
        coins = block.get("coin", []) if isinstance(block.get("coin"), list) else []
        for coin in coins:
            if not isinstance(coin, dict):
                continue
            asset = str(coin.get("coin", "")).strip().upper()
            if not asset:
                continue
            qty = _to_float(coin.get("walletBalance", 0), 0.0)
            if qty <= 0:
                continue
            px = price_map.get(asset)
            if px is None:
                continue
            usd = qty * px
            if usd < min_inventory_usd:
                continue
            out[asset] = round(max(0.0, usd), 6)
    return out


def fetch_binance_borrow_overlay(
    api_key: str,
    api_secret: str,
    assets: list[str],
    price_map: dict[str, float],
    timeout_sec: float,
) -> tuple[dict[str, float], dict[str, float], list[str]]:
    """Fetch Binance borrow capacity + next-hour borrow rate for given assets.

    Returns:
      - max_borrow_usd_by_asset
      - borrow_rate_bps_per_hour_by_asset
      - failures list
    """

    target_assets = sorted({a.strip().upper() for a in assets if a and a.strip()})
    failures: list[str] = []
    max_borrow_usd: dict[str, float] = {}
    borrow_rate_bps_per_hour: dict[str, float] = {}

    if not target_assets:
        return max_borrow_usd, borrow_rate_bps_per_hour, failures

    for asset in target_assets:
        try:
            payload = _binance_signed_get(
                "/sapi/v1/margin/maxBorrowable",
                {"asset": asset},
                api_key=api_key,
                api_secret=api_secret,
                timeout_sec=timeout_sec,
            )
        except Exception:
            failures.append(f"binance_max_borrow_error:{asset}")
            continue

        if not isinstance(payload, dict):
            failures.append(f"binance_max_borrow_bad_payload:{asset}")
            continue

        amount = _to_float(payload.get("amount"), -1.0)
        borrow_limit = _to_float(payload.get("borrowLimit"), -1.0)
        asset_units = amount if amount >= 0 else borrow_limit
        if asset_units < 0:
            failures.append(f"binance_max_borrow_missing_amount:{asset}")
            continue

        px = price_map.get(asset)
        if px is None:
            failures.append(f"binance_price_missing:{asset}")
            continue

        max_borrow_usd[asset] = round(max(0.0, asset_units * px), 6)

    for group in _chunk(target_assets, 20):
        params = {"assets": ",".join(group), "isIsolated": "FALSE"}
        payload: Any = None

        try:
            payload = _binance_signed_get(
                "/sapi/v1/margin/next-hourly-interest-rate",
                params,
                api_key=api_key,
                api_secret=api_secret,
                timeout_sec=timeout_sec,
            )
        except Exception:
            # Endpoint compatibility fallback.
            try:
                payload = _binance_signed_get(
                    "/sapi/v1/margin/next-hourly-interest-rate",
                    {"assets": ",".join(group)},
                    api_key=api_key,
                    api_secret=api_secret,
                    timeout_sec=timeout_sec,
                )
            except Exception:
                failures.append(f"binance_interest_rate_error:{','.join(group)}")
                continue

        rows = payload if isinstance(payload, list) else []
        if isinstance(payload, dict):
            maybe_rows = payload.get("data")
            if isinstance(maybe_rows, list):
                rows = maybe_rows

        for row in rows:
            if not isinstance(row, dict):
                continue
            asset = str(row.get("asset", "")).strip().upper()
            if not asset:
                continue
            rate_fraction_per_hour = _to_float(row.get("nextHourlyInterestRate"), -1.0)
            if rate_fraction_per_hour < 0:
                continue
            # Fraction -> bps per hour.
            borrow_rate_bps_per_hour[asset] = round(max(0.0, rate_fraction_per_hour * 10000.0), 6)

    return max_borrow_usd, borrow_rate_bps_per_hour, failures


def main() -> None:
    args = parse_args()

    constraints = load_json(args.constraints, fallback={})
    if not isinstance(constraints, dict):
        raise SystemExit(f"Constraints is invalid JSON object: {args.constraints}")

    rules = constraints.get("rules", [])
    if not isinstance(rules, list):
        raise SystemExit("Constraints rules is not a list")

    quote_payload = load_json(args.quotes, fallback=[])
    if not isinstance(quote_payload, list):
        quote_payload = []
    price_map = build_price_map(quote_payload)

    binance_key = os.getenv("BINANCE_API_KEY", "").strip()
    binance_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    bybit_key = os.getenv("BYBIT_API_KEY", "").strip()
    bybit_secret = os.getenv("BYBIT_API_SECRET", "").strip()

    inventory_by_venue: dict[str, dict[str, float]] = {"binance": {}, "bybit": {}}
    binance_max_borrow_usd: dict[str, float] = {}
    binance_borrow_rate_bps: dict[str, float] = {}
    failures: list[str] = []

    if binance_key and binance_secret:
        try:
            inventory_by_venue["binance"] = fetch_binance_inventory_usd(
                api_key=binance_key,
                api_secret=binance_secret,
                price_map=price_map,
                timeout_sec=args.timeout_sec,
                min_inventory_usd=args.min_inventory_usd,
            )
        except Exception:
            failures.append("binance_inventory_error")

        binance_assets = sorted(
            {
                str(r.get("asset", "")).strip().upper()
                for r in rules
                if isinstance(r, dict) and str(r.get("venue", "")).strip().lower() == "binance"
            }
        )
        try:
            (
                binance_max_borrow_usd,
                binance_borrow_rate_bps,
                borrow_failures,
            ) = fetch_binance_borrow_overlay(
                api_key=binance_key,
                api_secret=binance_secret,
                assets=binance_assets,
                price_map=price_map,
                timeout_sec=args.timeout_sec,
            )
            failures.extend(borrow_failures)
        except Exception:
            failures.append("binance_borrow_overlay_error")
    else:
        failures.append("binance_auth_missing")

    if bybit_key and bybit_secret:
        try:
            inventory_by_venue["bybit"] = fetch_bybit_inventory_usd(
                api_key=bybit_key,
                api_secret=bybit_secret,
                price_map=price_map,
                timeout_sec=args.timeout_sec,
                min_inventory_usd=args.min_inventory_usd,
            )
        except Exception:
            failures.append("bybit_inventory_error")
    else:
        failures.append("bybit_auth_missing")

    updated_rules = 0
    inventory_updates = 0
    borrow_cap_updates = 0
    borrow_rate_updates = 0
    venues_touched: dict[str, int] = defaultdict(int)

    for row in rules:
        if not isinstance(row, dict):
            continue

        venue = str(row.get("venue", "")).strip().lower()
        asset = str(row.get("asset", "")).strip().upper()
        if venue not in {"binance", "bybit"} or not asset:
            continue

        row_updated = False

        venue_inventory = inventory_by_venue.get(venue, {})
        if venue_inventory:
            inv_usd = _to_float(venue_inventory.get(asset, 0.0), 0.0)
            row["available_inventory_usd"] = round(max(0.0, inv_usd), 6)
            row_updated = True
            inventory_updates += 1

        if venue == "binance":
            if asset in binance_max_borrow_usd:
                row["max_borrow_usd"] = round(max(0.0, _to_float(binance_max_borrow_usd[asset], 0.0)), 6)
                row_updated = True
                borrow_cap_updates += 1

            if asset in binance_borrow_rate_bps:
                row["borrow_rate_bps_per_hour"] = round(
                    max(0.0, _to_float(binance_borrow_rate_bps[asset], 0.0)),
                    6,
                )
                row_updated = True
                borrow_rate_updates += 1

        if not row_updated:
            continue

        existing_cap = max(0.0, _to_float(row.get("max_position_usd", 0.0), 0.0))
        inv_usd_for_cap = max(0.0, _to_float(row.get("available_inventory_usd", 0.0), 0.0))
        max_borrow_usd = max(0.0, _to_float(row.get("max_borrow_usd", 0.0), 0.0))

        conservative_cap = inv_usd_for_cap + max_borrow_usd
        new_cap = min(existing_cap, conservative_cap) if existing_cap > 0 else conservative_cap
        row["max_position_usd"] = round(max(0.0, new_cap), 6)

        updated_rules += 1
        venues_touched[venue] += 1

    constraints["generated_at"] = datetime.now(timezone.utc).isoformat()
    constraints["version"] = "execution_constraints_v1"
    constraints["rules"] = sorted(
        [r for r in rules if isinstance(r, dict)],
        key=lambda r: (str(r.get("venue", "")), str(r.get("asset", ""))),
    )

    args.constraints.parent.mkdir(parents=True, exist_ok=True)
    args.constraints.write_text(json.dumps(constraints, indent=2))

    print(f"Quotes loaded: {len(quote_payload)}")
    print(f"Price map assets: {len(price_map)}")
    print(f"Constraint rules total: {len(constraints['rules'])}")
    print(f"Authenticated rules updated: {updated_rules}")
    print(f"Inventory updates: {inventory_updates}")
    print(f"Borrow-cap updates: {borrow_cap_updates}")
    print(f"Borrow-rate updates: {borrow_rate_updates}")
    if venues_touched:
        print(
            "Updated by venue:",
            ", ".join(f"{venue}={count}" for venue, count in sorted(venues_touched.items())),
        )
    if failures:
        print("Auth notes:", ", ".join(sorted(set(failures))))
    print(f"Wrote: {args.constraints}")


if __name__ == "__main__":
    main()
