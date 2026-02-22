#!/usr/bin/env python3
"""Overlay execution fee table with authenticated venue fee data when available.

Goal:
- Keep fee assumptions reproducible in `data/execution_fee_table.latest.json`.
- Replace template baselines with account-realized fees (Binance/Bybit) when API
  credentials are available.
- Fail soft: if auth is missing or endpoint errors, preserve existing template fees.

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
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_CANDIDATES = ROOT / "data" / "opportunity_candidates.combined.live.json"
DEFAULT_FEE_TABLE = ROOT / "data" / "execution_fee_table.latest.json"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Overlay fee table with authenticated venue fees")
    p.add_argument("--input-candidates", type=Path, default=DEFAULT_INPUT_CANDIDATES)
    p.add_argument("--fee-table", type=Path, default=DEFAULT_FEE_TABLE)
    p.add_argument("--timeout-sec", type=float, default=8.0)
    return p.parse_args()


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text())
    except Exception:
        return fallback


def _as_bps_from_rate(raw: Any) -> float | None:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return round(max(0.0, value) * 10000.0, 6)


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


def _sanitize_symbol(raw_symbol: str) -> str:
    raw = str(raw_symbol).strip().upper()
    if not raw:
        return "BTCUSDT"

    if "/" in raw:
        base, quote = raw.split("/", 1)
        base = re.sub(r"[^A-Z0-9]", "", base)
        quote = re.sub(r"[^A-Z0-9]", "", quote)
        if base and quote:
            return f"{base}{quote}"

    cleaned = re.sub(r"[^A-Z0-9]", "", raw)
    return cleaned or "BTCUSDT"


def _collect_symbols_by_venue(candidates: list[dict[str, Any]]) -> dict[tuple[str, str], str]:
    out: dict[tuple[str, str], str] = {}

    def pick_instrument(venue_text: str) -> str:
        lowered = venue_text.lower()
        if any(k in lowered for k in ["perp", "future", "swap", "linear"]):
            return "perp"
        return "spot"

    def pick_venue(venue_text: str) -> str:
        lowered = venue_text.lower()
        if "binance" in lowered:
            return "binance"
        if "bybit" in lowered:
            return "bybit"
        return ""

    for item in candidates:
        if not isinstance(item, dict):
            continue
        symbol = _sanitize_symbol(str(item.get("symbol", "")))
        for key in ["buy_venue", "sell_venue"]:
            raw_venue = str(item.get(key, ""))
            venue = pick_venue(raw_venue)
            if not venue:
                continue
            instrument = pick_instrument(raw_venue)
            out.setdefault((venue, instrument), symbol)

    out.setdefault(("binance", "spot"), "BTCUSDT")
    out.setdefault(("binance", "perp"), "BTCUSDT")
    out.setdefault(("bybit", "spot"), "BTCUSDT")
    out.setdefault(("bybit", "perp"), "BTCUSDT")

    return out


def fetch_binance_spot_fee(
    symbol: str,
    api_key: str,
    api_secret: str,
    timeout_sec: float,
) -> tuple[float, float] | None:
    payload = _binance_signed_get(
        "/sapi/v1/asset/tradeFee",
        {"symbol": symbol},
        api_key=api_key,
        api_secret=api_secret,
        timeout_sec=timeout_sec,
    )
    if not isinstance(payload, list) or not payload:
        return None

    row = payload[0] if isinstance(payload[0], dict) else {}
    taker_bps = _as_bps_from_rate(row.get("takerCommission"))
    maker_bps = _as_bps_from_rate(row.get("makerCommission"))
    if taker_bps is None or maker_bps is None:
        return None
    return taker_bps, maker_bps


def fetch_binance_perp_fee(
    symbol: str,
    api_key: str,
    api_secret: str,
    timeout_sec: float,
) -> tuple[float, float] | None:
    payload = _binance_signed_get(
        "/fapi/v1/commissionRate",
        {"symbol": symbol},
        api_key=api_key,
        api_secret=api_secret,
        timeout_sec=timeout_sec,
    )
    if not isinstance(payload, dict):
        return None

    taker_bps = _as_bps_from_rate(payload.get("takerCommissionRate"))
    maker_bps = _as_bps_from_rate(payload.get("makerCommissionRate"))
    if taker_bps is None or maker_bps is None:
        return None
    return taker_bps, maker_bps


def fetch_bybit_fee(
    category: str,
    symbol: str,
    api_key: str,
    api_secret: str,
    timeout_sec: float,
) -> tuple[float, float] | None:
    payload = _bybit_signed_get(
        "/v5/account/fee-rate",
        {"category": category, "symbol": symbol},
        api_key=api_key,
        api_secret=api_secret,
        timeout_sec=timeout_sec,
    )
    if not isinstance(payload, dict):
        return None
    if int(payload.get("retCode", -1)) != 0:
        return None

    result = payload.get("result", {})
    rows = result.get("list", []) if isinstance(result, dict) else []
    if not isinstance(rows, list) or not rows:
        return None
    row = rows[0] if isinstance(rows[0], dict) else {}

    taker_bps = _as_bps_from_rate(row.get("takerFeeRate"))
    maker_bps = _as_bps_from_rate(row.get("makerFeeRate"))
    if taker_bps is None or maker_bps is None:
        return None
    return taker_bps, maker_bps


def _overlay_rule(
    rules: list[dict[str, Any]],
    venue: str,
    instrument: str,
    taker_bps: float,
    maker_bps: float,
    source: str,
) -> None:
    target = None
    for row in rules:
        if not isinstance(row, dict):
            continue
        if str(row.get("venue", "")).strip().lower() == venue and str(row.get("instrument", "")).strip().lower() == instrument:
            target = row
            break

    if target is None:
        target = {"venue": venue, "instrument": instrument}
        rules.append(target)

    existing_vip = target.get("maker_vip_bps", maker_bps)
    try:
        existing_vip = max(0.0, float(existing_vip))
    except (TypeError, ValueError):
        existing_vip = maker_bps

    target["taker_bps"] = round(max(0.0, float(taker_bps)), 6)
    target["maker_bps"] = round(max(0.0, float(maker_bps)), 6)
    target["maker_vip_bps"] = round(min(existing_vip, target["maker_bps"]), 6)
    target["source"] = source


def main() -> None:
    args = parse_args()

    fee_table = load_json(args.fee_table, fallback={})
    if not isinstance(fee_table, dict):
        raise SystemExit(f"Fee table is invalid JSON object: {args.fee_table}")

    rules = fee_table.get("rules", [])
    if not isinstance(rules, list):
        raise SystemExit("Fee table rules is not a list")

    candidates = load_json(args.input_candidates, fallback=[])
    if not isinstance(candidates, list):
        candidates = []

    symbols = _collect_symbols_by_venue(candidates)

    binance_key = os.getenv("BINANCE_API_KEY", "").strip()
    binance_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    bybit_key = os.getenv("BYBIT_API_KEY", "").strip()
    bybit_secret = os.getenv("BYBIT_API_SECRET", "").strip()

    updated = 0
    failures: list[str] = []

    if binance_key and binance_secret:
        try:
            spot_symbol = symbols.get(("binance", "spot"), "BTCUSDT")
            spot_fee = fetch_binance_spot_fee(spot_symbol, binance_key, binance_secret, timeout_sec=args.timeout_sec)
            if spot_fee is not None:
                _overlay_rule(
                    rules,
                    venue="binance",
                    instrument="spot",
                    taker_bps=spot_fee[0],
                    maker_bps=spot_fee[1],
                    source="binance_authenticated_api",
                )
                updated += 1
            else:
                failures.append("binance_spot_no_data")
        except urllib.error.HTTPError as e:
            failures.append(f"binance_spot_http_{e.code}")
        except Exception:
            failures.append("binance_spot_error")

        try:
            perp_symbol = symbols.get(("binance", "perp"), "BTCUSDT")
            perp_fee = fetch_binance_perp_fee(perp_symbol, binance_key, binance_secret, timeout_sec=args.timeout_sec)
            if perp_fee is not None:
                _overlay_rule(
                    rules,
                    venue="binance",
                    instrument="perp",
                    taker_bps=perp_fee[0],
                    maker_bps=perp_fee[1],
                    source="binance_authenticated_api",
                )
                updated += 1
            else:
                failures.append("binance_perp_no_data")
        except urllib.error.HTTPError as e:
            failures.append(f"binance_perp_http_{e.code}")
        except Exception:
            failures.append("binance_perp_error")
    else:
        failures.append("binance_auth_missing")

    if bybit_key and bybit_secret:
        try:
            spot_symbol = symbols.get(("bybit", "spot"), "BTCUSDT")
            spot_fee = fetch_bybit_fee("spot", spot_symbol, bybit_key, bybit_secret, timeout_sec=args.timeout_sec)
            if spot_fee is not None:
                _overlay_rule(
                    rules,
                    venue="bybit",
                    instrument="spot",
                    taker_bps=spot_fee[0],
                    maker_bps=spot_fee[1],
                    source="bybit_authenticated_api",
                )
                updated += 1
            else:
                failures.append("bybit_spot_no_data")
        except urllib.error.HTTPError as e:
            failures.append(f"bybit_spot_http_{e.code}")
        except Exception:
            failures.append("bybit_spot_error")

        try:
            perp_symbol = symbols.get(("bybit", "perp"), "BTCUSDT")
            perp_fee = fetch_bybit_fee("linear", perp_symbol, bybit_key, bybit_secret, timeout_sec=args.timeout_sec)
            if perp_fee is not None:
                _overlay_rule(
                    rules,
                    venue="bybit",
                    instrument="perp",
                    taker_bps=perp_fee[0],
                    maker_bps=perp_fee[1],
                    source="bybit_authenticated_api",
                )
                updated += 1
            else:
                failures.append("bybit_perp_no_data")
        except urllib.error.HTTPError as e:
            failures.append(f"bybit_perp_http_{e.code}")
        except Exception:
            failures.append("bybit_perp_error")
    else:
        failures.append("bybit_auth_missing")

    fee_table["generated_at"] = datetime.now(timezone.utc).isoformat()
    fee_table["version"] = "execution_fee_table_v1"
    fee_table["rules"] = sorted(
        [row for row in rules if isinstance(row, dict)],
        key=lambda row: (str(row.get("venue", "")), str(row.get("instrument", ""))),
    )

    args.fee_table.parent.mkdir(parents=True, exist_ok=True)
    args.fee_table.write_text(json.dumps(fee_table, indent=2))

    print(f"Candidates loaded: {len(candidates)}")
    print(f"Fee rules total: {len(fee_table['rules'])}")
    print(f"Authenticated rules updated: {updated}")
    if failures:
        print("Auth notes:", ", ".join(sorted(set(failures))))
    print(f"Wrote: {args.fee_table}")


if __name__ == "__main__":
    main()
