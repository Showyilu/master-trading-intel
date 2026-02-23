#!/usr/bin/env python3
"""Opportunity scanner with net-edge math and risk gating.

Formula (bps):
net_edge = gross_edge - fees - slippage - latency_risk - transfer_risk - borrow_cost
transfer_risk = transfer_delay_min * transfer_penalty_bps_per_min
borrow_cost = borrow_rate_bps_per_hour * hold_hours * (borrow_used_usd / size_usd)

Supports execution profiles (taker/maker/inventory assumptions) so the same
candidate set can be stress-tested under different execution realities.
Also supports leverage hard gates via execution constraints (`max_leverage`)
with strategy-specific notional multipliers (e.g., funding carry ~= 2-leg exposure).
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = ROOT / "data" / "opportunity_candidates.sample.json"
DEFAULT_OUTPUT_JSON = ROOT / "opportunities" / "shortlist-latest.json"
DEFAULT_OUTPUT_MD = ROOT / "opportunities" / "dashboard-latest.md"
DEFAULT_OUTPUT_SUMMARY = ROOT / "opportunities" / "rejection-summary-latest.json"
DEFAULT_CONSTRAINTS_PATH = ROOT / "data" / "execution_constraints.latest.json"
DEFAULT_FEE_TABLE_PATH = ROOT / "data" / "execution_fee_table.latest.json"

DEFAULT_TRANSFER_PENALTY_BPS_PER_MIN = 0.45
DEFAULT_MIN_NET_EDGE_BPS = 8.0
DEFAULT_MAX_RISK_SCORE = 0.60
UNBOUNDED_USD = 10**18

DEFAULT_STRATEGY_HOLD_HOURS: dict[str, float] = {
    "cex_cex": 0.20,
    "cex_dex": 0.30,
    "funding_carry_cex_cex": 8.0,
    "perp_spot_basis": 8.0,
}

# Strategy-specific leverage notional multipliers.
# required_notional_usd = size_usd * multiplier
# Rationale:
# - cex_cex / cex_dex: one directional notional against available inventory.
# - funding_carry_cex_cex: two perp legs (long + short) consume margin on both sides.
# - perp_spot_basis: spot + hedge leg typically requires >1x capital intensity.
DEFAULT_STRATEGY_LEVERAGE_NOTIONAL_MULTIPLIER: dict[str, float] = {
    "cex_cex": 1.0,
    "cex_dex": 1.0,
    "funding_carry_cex_cex": 2.0,
    "perp_spot_basis": 1.25,
}

INVENTORY_REQUIRED_STRATEGIES = {
    "cex_cex",
    "cex_dex",
    "perp_spot_basis",
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

EXECUTION_PROFILES: dict[str, dict[str, float]] = {
    "taker_default": {
        "fee_multiplier": 1.0,
        "slippage_multiplier": 1.0,
        "latency_multiplier": 1.0,
        "transfer_delay_multiplier": 1.0,
        "transfer_penalty_bps_per_min": 0.45,
        "min_net_edge_bps": 8.0,
        "max_risk_score": 0.60,
    },
    "maker_inventory": {
        "fee_multiplier": 0.42,
        "slippage_multiplier": 0.72,
        "latency_multiplier": 0.95,
        "transfer_delay_multiplier": 0.30,
        "transfer_penalty_bps_per_min": 0.24,
        "min_net_edge_bps": 4.5,
        "max_risk_score": 0.62,
    },
    "maker_inventory_vip": {
        "fee_multiplier": 0.25,
        "slippage_multiplier": 0.60,
        "latency_multiplier": 0.90,
        "transfer_delay_multiplier": 0.20,
        "transfer_penalty_bps_per_min": 0.18,
        "min_net_edge_bps": 3.0,
        "max_risk_score": 0.65,
    },
}


@dataclass
class ScoredOpportunity:
    detected_at: str
    strategy_type: str
    symbol: str
    buy_venue: str
    sell_venue: str
    execution_profile: str
    constraints_enabled: bool
    gross_edge_bps: float
    source_fees_bps: float
    fee_model_base_fees_bps: float
    fee_mode: str
    fee_model_used: bool
    source_slippage_bps: float
    source_latency_risk_bps: float
    source_transfer_delay_min: float
    fees_bps: float
    slippage_bps: float
    latency_risk_bps: float
    transfer_delay_min: float
    transfer_risk_bps: float
    hold_hours: float
    inventory_available_usd: float
    max_position_usd: float
    borrow_required_usd: float
    borrow_capacity_usd: float
    borrow_rate_bps_per_hour: float
    max_leverage: float
    leverage_notional_multiplier: float
    leverage_notional_usd: float
    leverage_used: float
    borrow_cost_bps: float
    net_edge_bps: float
    risk_score: float
    size_usd: float
    dominant_drag: str
    is_qualified: bool
    rejection_reasons: list[str]
    notes: str = ""


class ConstraintBook:
    def __init__(self, payload: dict[str, Any] | None = None, path: Path | None = None):
        payload = payload or {}
        self.path = str(path) if path else ""
        self.enabled = bool(payload)

        defaults = payload.get("defaults", {}) if isinstance(payload, dict) else {}
        self.defaults = defaults if isinstance(defaults, dict) else {}

        self.strategy_hold_hours = dict(DEFAULT_STRATEGY_HOLD_HOURS)
        custom_hold_hours = payload.get("strategy_hold_hours", {}) if isinstance(payload, dict) else {}
        if isinstance(custom_hold_hours, dict):
            for k, v in custom_hold_hours.items():
                try:
                    self.strategy_hold_hours[str(k)] = max(0.0, float(v))
                except (TypeError, ValueError):
                    continue

        self.strategy_leverage_notional_multiplier = dict(
            DEFAULT_STRATEGY_LEVERAGE_NOTIONAL_MULTIPLIER
        )
        custom_leverage_multiplier = (
            payload.get("strategy_leverage_notional_multiplier", {})
            if isinstance(payload, dict)
            else {}
        )
        if isinstance(custom_leverage_multiplier, dict):
            for k, v in custom_leverage_multiplier.items():
                try:
                    self.strategy_leverage_notional_multiplier[str(k)] = max(0.0, float(v))
                except (TypeError, ValueError):
                    continue

        self.rules: dict[tuple[str, str], dict[str, Any]] = {}
        rules = payload.get("rules", []) if isinstance(payload, dict) else []
        if isinstance(rules, list):
            for row in rules:
                if not isinstance(row, dict):
                    continue
                venue = str(row.get("venue", "")).strip().lower()
                asset = str(row.get("asset", "")).strip().upper()
                if not venue or not asset:
                    continue
                self.rules[(venue, asset)] = row

        self.known_venues = {venue for venue, _ in self.rules.keys()}

    @classmethod
    def from_path(cls, path: Path | None) -> "ConstraintBook":
        if path is None or not path.exists():
            return cls(payload=None, path=path)
        try:
            payload = json.loads(path.read_text())
        except Exception:
            payload = None
        if not isinstance(payload, dict):
            payload = None
        return cls(payload=payload, path=path)

    @staticmethod
    def _as_non_negative(value: Any, fallback: float) -> float:
        try:
            return max(0.0, float(value))
        except (TypeError, ValueError):
            return fallback

    def hold_hours(self, strategy_type: str) -> float:
        return self._as_non_negative(self.strategy_hold_hours.get(strategy_type), 1.0)

    def leverage_notional_multiplier(self, strategy_type: str) -> float:
        return self._as_non_negative(
            self.strategy_leverage_notional_multiplier.get(strategy_type),
            1.0,
        )

    @staticmethod
    def asset_from_symbol(symbol: str) -> str:
        raw = str(symbol).strip().upper()
        if not raw:
            return "UNKNOWN"
        if "/" in raw:
            return raw.split("/")[0].strip() or "UNKNOWN"
        parts = [p for p in re.split(r"[^A-Z0-9]+", raw) if p]
        return parts[0] if parts else "UNKNOWN"

    def canonical_venue(self, raw_venue: str) -> str:
        lowered = str(raw_venue).strip().lower()
        if not lowered:
            return "unknown"

        if lowered in self.known_venues:
            return lowered

        for venue in sorted(self.known_venues, key=len, reverse=True):
            if venue and venue in lowered:
                return venue

        tokens = [t for t in re.split(r"[^a-z0-9]+", lowered) if t]
        for token in tokens:
            if token not in VENUE_STOPWORDS:
                return token

        return lowered

    def _read_limit(self, row: dict[str, Any], key: str, default_unbounded: bool = False) -> float:
        if key in row:
            return self._as_non_negative(row.get(key), 0.0)
        if key in self.defaults:
            return self._as_non_negative(self.defaults.get(key), 0.0)
        return UNBOUNDED_USD if default_unbounded else 0.0

    def _read_value(self, row: dict[str, Any], key: str, fallback: float = 0.0) -> float:
        if key in row:
            return self._as_non_negative(row.get(key), fallback)
        if key in self.defaults:
            return self._as_non_negative(self.defaults.get(key), fallback)
        return fallback

    def constraints_for(self, raw_venue: str, asset: str) -> dict[str, float | str]:
        venue_key = self.canonical_venue(raw_venue)
        asset_key = str(asset).strip().upper() or "UNKNOWN"
        row = self.rules.get((venue_key, asset_key), {})

        max_position = self._read_limit(row, "max_position_usd", default_unbounded=True)
        inventory = self._read_limit(row, "available_inventory_usd", default_unbounded=False)
        borrow_cap = self._read_limit(row, "max_borrow_usd", default_unbounded=False)
        borrow_rate = self._read_value(row, "borrow_rate_bps_per_hour", fallback=0.0)
        max_leverage = self._read_value(row, "max_leverage", fallback=0.0)

        return {
            "venue_key": venue_key,
            "asset": asset_key,
            "max_position_usd": max_position,
            "available_inventory_usd": inventory,
            "max_borrow_usd": borrow_cap,
            "borrow_rate_bps_per_hour": borrow_rate,
            "max_leverage": max_leverage,
        }


class FeeTable:
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

    INSTRUMENT_KEYWORDS = {
        "perp": {"perp", "future", "futures", "swap"},
        "dex": {"dex", "jupiter", "uniswap", "raydium", "0x", "orca"},
        "spot": {"spot"},
    }

    def __init__(self, payload: dict[str, Any] | None = None, path: Path | None = None):
        payload = payload or {}
        self.path = str(path) if path else ""
        self.enabled = bool(payload)

        defaults = payload.get("defaults", {}) if isinstance(payload, dict) else {}
        defaults = defaults if isinstance(defaults, dict) else {}

        self.default_fees: dict[str, dict[str, float]] = {}
        for instrument in ["spot", "perp", "dex", "unknown"]:
            bucket = defaults.get(instrument, {}) if isinstance(defaults.get(instrument), dict) else {}
            self.default_fees[instrument] = {
                "taker_bps": self._as_non_negative(bucket.get("taker_bps"), 10.0),
                "maker_bps": self._as_non_negative(bucket.get("maker_bps"), 8.0),
                "maker_vip_bps": self._as_non_negative(bucket.get("maker_vip_bps"), 4.0),
            }

        self.profile_fee_mode = dict(self.DEFAULT_PROFILE_FEE_MODE)
        payload_profile_mode = payload.get("profile_fee_mode", {}) if isinstance(payload, dict) else {}
        if isinstance(payload_profile_mode, dict):
            for profile, mode in payload_profile_mode.items():
                mode_key = str(mode).strip().lower()
                if mode_key in {"taker", "maker", "maker_vip"}:
                    self.profile_fee_mode[str(profile)] = mode_key

        self.strategy_roundtrip_side_multiplier = dict(self.DEFAULT_STRATEGY_ROUNDTRIP_SIDE_MULTIPLIER)
        strategy_map = defaults.get("strategy_roundtrip_side_multiplier", {}) if isinstance(defaults, dict) else {}
        if isinstance(strategy_map, dict):
            for strategy, mult in strategy_map.items():
                try:
                    self.strategy_roundtrip_side_multiplier[str(strategy)] = max(0.0, float(mult))
                except (TypeError, ValueError):
                    continue

        self.rules: dict[tuple[str, str], dict[str, float | str]] = {}
        rules = payload.get("rules", []) if isinstance(payload, dict) else []
        if isinstance(rules, list):
            for row in rules:
                if not isinstance(row, dict):
                    continue
                venue = str(row.get("venue", "")).strip().lower()
                instrument = str(row.get("instrument", "")).strip().lower() or "unknown"
                if not venue:
                    continue
                self.rules[(venue, instrument)] = {
                    "taker_bps": self._as_non_negative(row.get("taker_bps"), self.default_fees["unknown"]["taker_bps"]),
                    "maker_bps": self._as_non_negative(row.get("maker_bps"), self.default_fees["unknown"]["maker_bps"]),
                    "maker_vip_bps": self._as_non_negative(row.get("maker_vip_bps"), self.default_fees["unknown"]["maker_vip_bps"]),
                }

        self.known_venues = {venue for venue, _ in self.rules.keys()}

    @classmethod
    def from_path(cls, path: Path | None) -> "FeeTable":
        if path is None or not path.exists():
            return cls(payload=None, path=path)
        try:
            payload = json.loads(path.read_text())
        except Exception:
            payload = None
        if not isinstance(payload, dict):
            payload = None
        return cls(payload=payload, path=path)

    @staticmethod
    def _as_non_negative(value: Any, fallback: float) -> float:
        try:
            return max(0.0, float(value))
        except (TypeError, ValueError):
            return fallback

    def canonical_venue(self, raw_venue: str) -> str:
        lowered = str(raw_venue).strip().lower()
        if not lowered:
            return "unknown"

        if lowered in self.known_venues:
            return lowered

        for venue in sorted(self.known_venues, key=len, reverse=True):
            if venue and venue in lowered:
                return venue

        tokens = [t for t in re.split(r"[^a-z0-9]+", lowered) if t]
        for token in tokens:
            if token not in VENUE_STOPWORDS:
                return token

        return lowered

    def instrument_from_venue(self, raw_venue: str) -> str:
        lowered = str(raw_venue).strip().lower()
        if not lowered:
            return "unknown"

        tokens = [t for t in re.split(r"[^a-z0-9]+", lowered) if t]
        token_set = set(tokens)

        if token_set & self.INSTRUMENT_KEYWORDS["perp"]:
            return "perp"
        if token_set & self.INSTRUMENT_KEYWORDS["dex"]:
            return "dex"
        if token_set & self.INSTRUMENT_KEYWORDS["spot"]:
            return "spot"

        if "jupiter" in lowered or "uniswap" in lowered:
            return "dex"
        return "spot"

    def _default_bucket(self, instrument: str) -> dict[str, float]:
        if instrument in self.default_fees:
            return self.default_fees[instrument]
        return self.default_fees["unknown"]

    def side_fee_bps(self, raw_venue: str, fee_mode: str) -> float:
        venue_key = self.canonical_venue(raw_venue)
        instrument = self.instrument_from_venue(raw_venue)

        row = self.rules.get((venue_key, instrument)) or self.rules.get((venue_key, "unknown"))
        if not isinstance(row, dict):
            row = self._default_bucket(instrument)

        key = f"{fee_mode}_bps"
        fallback = self._default_bucket(instrument).get(key, self.default_fees["unknown"].get(key, 10.0))
        return self._as_non_negative(row.get(key), float(fallback))

    def estimate_total_fee_bps(self, item: dict[str, Any], execution_profile: str) -> tuple[float, str] | None:
        if not self.enabled:
            return None

        fee_mode = self.profile_fee_mode.get(execution_profile, "taker")
        if fee_mode not in {"taker", "maker", "maker_vip"}:
            fee_mode = "taker"

        buy_fee = self.side_fee_bps(item.get("buy_venue", ""), fee_mode)
        sell_fee = self.side_fee_bps(item.get("sell_venue", ""), fee_mode)

        strategy_type = str(item.get("strategy_type", "")).strip()
        side_multiplier = self.strategy_roundtrip_side_multiplier.get(strategy_type, 1.0)

        total = (buy_fee + sell_fee) * max(0.0, float(side_multiplier))
        return round(total, 6), fee_mode


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _risk_score(item: dict[str, Any], net_edge_bps: float, transfer_risk_bps: float) -> float:
    fee_component = _clamp(item["fees_bps"] / 20)
    slip_component = _clamp(item["slippage_bps"] / 20)
    latency_component = _clamp(item["latency_risk_bps"] / 12)
    transfer_component = _clamp(transfer_risk_bps / 12)
    borrow_component = _clamp(item["borrow_cost_bps"] / 12)
    edge_buffer_component = _clamp((10 - max(net_edge_bps, 0)) / 10)

    return round(
        0.18 * fee_component
        + 0.22 * slip_component
        + 0.16 * latency_component
        + 0.16 * transfer_component
        + 0.14 * borrow_component
        + 0.14 * edge_buffer_component,
        4,
    )


def _dominant_drag(item: dict[str, Any], transfer_risk_bps: float) -> str:
    components = {
        "fees": item["fees_bps"],
        "slippage": item["slippage_bps"],
        "latency": item["latency_risk_bps"],
        "transfer": transfer_risk_bps,
        "borrow": item["borrow_cost_bps"],
    }
    return max(components.items(), key=lambda kv: kv[1])[0]


def _rejection_reasons(
    item: dict[str, Any],
    net_edge_bps: float,
    risk_score: float,
    transfer_risk_bps: float,
    min_net_edge_bps: float,
    max_risk_score: float,
    constraints_enabled: bool,
    position_limit_exceeded: bool,
    inventory_unavailable: bool,
    borrow_limit_exceeded: bool,
    leverage_limit_exceeded: bool,
) -> list[str]:
    reasons: list[str] = []

    if net_edge_bps < min_net_edge_bps:
        reasons.append("net_edge_below_threshold")
    if risk_score > max_risk_score:
        reasons.append("risk_score_above_threshold")

    gross = item["gross_edge_bps"]
    if item["fees_bps"] >= gross:
        reasons.append("fee_dominated")
    if item["slippage_bps"] >= gross:
        reasons.append("slippage_dominated")
    if (item["latency_risk_bps"] + transfer_risk_bps) >= gross:
        reasons.append("latency_transfer_dominated")
    if item["borrow_cost_bps"] > 0 and item["borrow_cost_bps"] >= gross:
        reasons.append("borrow_dominated")

    if constraints_enabled:
        if position_limit_exceeded:
            reasons.append("position_limit_exceeded")
        if inventory_unavailable:
            reasons.append("inventory_unavailable")
        if borrow_limit_exceeded:
            reasons.append("borrow_limit_exceeded")
        if leverage_limit_exceeded:
            reasons.append("leverage_limit_exceeded")

    return reasons


def _render_limit(limit: float) -> float:
    if limit >= UNBOUNDED_USD / 2:
        return 0.0
    return round(limit, 4)


def score_item(
    item: dict[str, Any],
    execution_profile: str,
    fee_multiplier: float,
    slippage_multiplier: float,
    latency_multiplier: float,
    transfer_delay_multiplier: float,
    transfer_penalty_bps_per_min: float,
    min_net_edge_bps: float,
    max_risk_score: float,
    constraint_book: ConstraintBook,
    fee_table: FeeTable,
) -> ScoredOpportunity:
    source_fees_bps = float(item["fees_bps"])
    source_slippage_bps = float(item["slippage_bps"])
    source_latency_risk_bps = float(item["latency_risk_bps"])
    source_transfer_delay_min = float(item["transfer_delay_min"])
    size_usd = float(item["size_usd"])

    fee_model_base_fees_bps = source_fees_bps
    fee_mode = "candidate_source"
    fee_model_used = False
    fee_estimate = fee_table.estimate_total_fee_bps(item, execution_profile=execution_profile)
    if fee_estimate is not None:
        fee_model_base_fees_bps, fee_mode = fee_estimate
        fee_model_used = True

    fees_bps = round(fee_model_base_fees_bps * fee_multiplier, 6)
    slippage_bps = round(source_slippage_bps * slippage_multiplier, 6)
    latency_risk_bps = round(source_latency_risk_bps * latency_multiplier, 6)
    transfer_delay_min = round(source_transfer_delay_min * transfer_delay_multiplier, 6)

    transfer_risk_bps = round(transfer_delay_min * transfer_penalty_bps_per_min, 4)

    strategy_type = str(item.get("strategy_type", "")).strip()
    hold_hours = constraint_book.hold_hours(strategy_type)
    leverage_notional_multiplier = constraint_book.leverage_notional_multiplier(strategy_type)
    leverage_notional_usd = round(size_usd * leverage_notional_multiplier, 6)

    inventory_available_usd = 0.0
    max_position_usd = 0.0
    borrow_required_usd = 0.0
    borrow_capacity_usd = 0.0
    borrow_rate_bps_per_hour = 0.0
    max_leverage = 0.0
    leverage_used = 0.0
    borrow_cost_bps = 0.0
    position_limit_exceeded = False
    inventory_unavailable = False
    borrow_limit_exceeded = False
    leverage_limit_exceeded = False

    if constraint_book.enabled:
        asset = constraint_book.asset_from_symbol(item.get("symbol", ""))
        buy_constraints = constraint_book.constraints_for(item.get("buy_venue", ""), asset)
        sell_constraints = constraint_book.constraints_for(item.get("sell_venue", ""), asset)

        effective_max_position = min(
            float(buy_constraints["max_position_usd"]),
            float(sell_constraints["max_position_usd"]),
        )
        max_position_usd = _render_limit(effective_max_position)
        position_limit_exceeded = size_usd > effective_max_position + 1e-9

        inventory_available_usd = float(sell_constraints["available_inventory_usd"])
        borrow_capacity_usd = float(sell_constraints["max_borrow_usd"])
        borrow_rate_bps_per_hour = float(sell_constraints["borrow_rate_bps_per_hour"])

        buy_max_leverage = float(buy_constraints.get("max_leverage", 0.0))
        sell_max_leverage = float(sell_constraints.get("max_leverage", 0.0))
        leverage_caps = [v for v in [buy_max_leverage, sell_max_leverage] if v > 0]
        max_leverage = min(leverage_caps) if leverage_caps else 0.0

        inventory_required_usd = (
            size_usd if strategy_type in INVENTORY_REQUIRED_STRATEGIES else 0.0
        )
        borrow_required_usd = max(0.0, inventory_required_usd - inventory_available_usd)
        inventory_unavailable = (
            inventory_required_usd > 0
            and inventory_available_usd <= 0.0
            and borrow_capacity_usd <= 0.0
        )
        borrow_limit_exceeded = borrow_required_usd > borrow_capacity_usd + 1e-9

        equity_base_usd = max(0.0, inventory_available_usd)
        if leverage_notional_usd > 0 and equity_base_usd > 0:
            leverage_used = round(leverage_notional_usd / equity_base_usd, 6)

        if max_leverage > 0 and leverage_notional_usd > 0:
            leverage_limit_exceeded = (
                equity_base_usd <= 0.0
                or leverage_used > max_leverage + 1e-9
            )

        borrow_used_usd = min(borrow_required_usd, borrow_capacity_usd)
        if size_usd > 0 and borrow_used_usd > 0:
            borrow_cost_bps = round(
                (borrow_used_usd / size_usd) * borrow_rate_bps_per_hour * hold_hours,
                6,
            )

    net_edge_bps = round(
        float(item["gross_edge_bps"])
        - fees_bps
        - slippage_bps
        - latency_risk_bps
        - transfer_risk_bps
        - borrow_cost_bps,
        4,
    )

    scoring_view = {
        "gross_edge_bps": float(item["gross_edge_bps"]),
        "fees_bps": fees_bps,
        "slippage_bps": slippage_bps,
        "latency_risk_bps": latency_risk_bps,
        "borrow_cost_bps": borrow_cost_bps,
    }

    risk_score = _risk_score(scoring_view, net_edge_bps, transfer_risk_bps)

    constraint_blocked = (
        position_limit_exceeded
        or borrow_limit_exceeded
        or inventory_unavailable
        or leverage_limit_exceeded
    )
    is_qualified = (
        net_edge_bps >= min_net_edge_bps
        and risk_score <= max_risk_score
        and not constraint_blocked
    )

    dominant_drag = _dominant_drag(scoring_view, transfer_risk_bps)
    rejection_reasons = []
    if not is_qualified:
        rejection_reasons = _rejection_reasons(
            scoring_view,
            net_edge_bps=net_edge_bps,
            risk_score=risk_score,
            transfer_risk_bps=transfer_risk_bps,
            min_net_edge_bps=min_net_edge_bps,
            max_risk_score=max_risk_score,
            constraints_enabled=constraint_book.enabled,
            position_limit_exceeded=position_limit_exceeded,
            inventory_unavailable=inventory_unavailable,
            borrow_limit_exceeded=borrow_limit_exceeded,
            leverage_limit_exceeded=leverage_limit_exceeded,
        )

    return ScoredOpportunity(
        detected_at=item["detected_at"],
        strategy_type=item["strategy_type"],
        symbol=item["symbol"],
        buy_venue=item["buy_venue"],
        sell_venue=item["sell_venue"],
        execution_profile=execution_profile,
        constraints_enabled=constraint_book.enabled,
        gross_edge_bps=float(item["gross_edge_bps"]),
        source_fees_bps=source_fees_bps,
        fee_model_base_fees_bps=fee_model_base_fees_bps,
        fee_mode=fee_mode,
        fee_model_used=fee_model_used,
        source_slippage_bps=source_slippage_bps,
        source_latency_risk_bps=source_latency_risk_bps,
        source_transfer_delay_min=source_transfer_delay_min,
        fees_bps=fees_bps,
        slippage_bps=slippage_bps,
        latency_risk_bps=latency_risk_bps,
        transfer_delay_min=transfer_delay_min,
        transfer_risk_bps=transfer_risk_bps,
        hold_hours=hold_hours,
        inventory_available_usd=round(inventory_available_usd, 4),
        max_position_usd=max_position_usd,
        borrow_required_usd=round(borrow_required_usd, 4),
        borrow_capacity_usd=round(borrow_capacity_usd, 4),
        borrow_rate_bps_per_hour=round(borrow_rate_bps_per_hour, 6),
        max_leverage=round(max_leverage, 6),
        leverage_notional_multiplier=round(leverage_notional_multiplier, 6),
        leverage_notional_usd=round(leverage_notional_usd, 6),
        leverage_used=round(leverage_used, 6),
        borrow_cost_bps=borrow_cost_bps,
        net_edge_bps=net_edge_bps,
        risk_score=risk_score,
        size_usd=size_usd,
        dominant_drag=dominant_drag,
        is_qualified=is_qualified,
        rejection_reasons=rejection_reasons,
        notes=item.get("notes", ""),
    )


def _build_summary(
    scored: list[ScoredOpportunity],
    input_path: Path,
    constraints_path: Path | None,
    fee_table_path: Path | None,
    execution_profile: str,
    fee_multiplier: float,
    slippage_multiplier: float,
    latency_multiplier: float,
    transfer_delay_multiplier: float,
    transfer_penalty_bps_per_min: float,
    min_net_edge_bps: float,
    max_risk_score: float,
) -> dict[str, Any]:
    rejected = [s for s in scored if not s.is_qualified]
    reason_counter = Counter(reason for s in rejected for reason in s.rejection_reasons)
    drag_counter = Counter(s.dominant_drag for s in rejected)

    return {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "input": str(input_path),
        "constraints": str(constraints_path) if constraints_path else None,
        "fee_table": str(fee_table_path) if fee_table_path else None,
        "execution_profile": execution_profile,
        "rules": {
            "fee_multiplier": fee_multiplier,
            "slippage_multiplier": slippage_multiplier,
            "latency_multiplier": latency_multiplier,
            "transfer_delay_multiplier": transfer_delay_multiplier,
            "transfer_penalty_bps_per_min": transfer_penalty_bps_per_min,
            "min_net_edge_bps": min_net_edge_bps,
            "max_risk_score": max_risk_score,
        },
        "counts": {
            "candidates": len(scored),
            "qualified": len(scored) - len(rejected),
            "rejected": len(rejected),
            "fee_model_applied": sum(1 for s in scored if s.fee_model_used),
        },
        "rejection_reason_counts": dict(sorted(reason_counter.items())),
        "dominant_drag_counts": dict(sorted(drag_counter.items())),
        "top_rejected": [
            {
                "symbol": s.symbol,
                "path": f"{s.buy_venue}->{s.sell_venue}",
                "net_edge_bps": s.net_edge_bps,
                "risk_score": s.risk_score,
                "dominant_drag": s.dominant_drag,
                "borrow_cost_bps": s.borrow_cost_bps,
                "max_leverage": s.max_leverage,
                "leverage_notional_multiplier": s.leverage_notional_multiplier,
                "leverage_notional_usd": s.leverage_notional_usd,
                "leverage_used": s.leverage_used,
                "rejection_reasons": s.rejection_reasons,
            }
            for s in sorted(rejected, key=lambda x: x.net_edge_bps, reverse=True)[:10]
        ],
    }


def render_markdown(
    scored: list[ScoredOpportunity],
    input_path: Path,
    constraints_path: Path | None,
    fee_table_path: Path | None,
    execution_profile: str,
    fee_multiplier: float,
    slippage_multiplier: float,
    latency_multiplier: float,
    transfer_delay_multiplier: float,
    transfer_penalty_bps_per_min: float,
    min_net_edge_bps: float,
    max_risk_score: float,
) -> str:
    run_at = datetime.now(tz=timezone.utc).isoformat()
    qualified = [s for s in scored if s.is_qualified]
    rejected = [s for s in scored if not s.is_qualified]
    reason_counter = Counter(reason for s in rejected for reason in s.rejection_reasons)
    dominant_drag_counter = Counter(s.dominant_drag for s in rejected)

    lines = [
        "# Opportunity Dashboard (Latest)",
        "",
        f"Generated at: `{run_at}`",
        f"Input: `{input_path}`",
        f"Execution profile: `{execution_profile}`",
        (
            f"Constraints: `{constraints_path}`"
            if constraints_path
            else "Constraints: `disabled`"
        ),
        (
            f"Fee table: `{fee_table_path}`"
            if fee_table_path
            else "Fee table: `candidate embedded fees`"
        ),
        "",
        "## Rules",
        (
            "- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk - borrow cost "
            f"({transfer_penalty_bps_per_min} bps/min transfer penalty)"
        ),
        (
            "- Profile multipliers: "
            f"fees×{fee_multiplier}, slippage×{slippage_multiplier}, "
            f"latency×{latency_multiplier}, transfer_delay×{transfer_delay_multiplier}"
        ),
        f"- Qualified if `net_edge_bps >= {min_net_edge_bps}` and `risk_score <= {max_risk_score}`",
        "",
        (
            f"## Summary\n- Candidates: **{len(scored)}**\n- Qualified: **{len(qualified)}**\n"
            f"- Rejected: **{len(rejected)}**\n"
            f"- Fee-model applied: **{sum(1 for s in scored if s.fee_model_used)}**"
        ),
        "",
        "## Rejection Breakdown",
    ]

    if not rejected:
        lines.append("- No rejected candidates this run.")
    else:
        if reason_counter:
            lines.append("- By reason:")
            for reason, count in sorted(reason_counter.items(), key=lambda kv: kv[1], reverse=True):
                lines.append(f"  - `{reason}`: **{count}**")
        if dominant_drag_counter:
            lines.append("- Dominant drag:")
            for drag, count in sorted(dominant_drag_counter.items(), key=lambda kv: kv[1], reverse=True):
                lines.append(f"  - `{drag}`: **{count}**")

    lines.extend(
        [
            "",
            "## Ranked Candidates",
            "",
            "| Rank | Pair | Path | Gross bps | Net bps | Borrow bps | Lev Notional USD | Lev (used/cap) | Risk | Drag | Qualified | Rejection Reasons |",
            "|---:|---|---|---:|---:|---:|---:|---|---:|---|:---:|---|",
        ]
    )

    ranked = sorted(scored, key=lambda x: (x.is_qualified, x.net_edge_bps), reverse=True)
    for i, item in enumerate(ranked, start=1):
        reasons = ", ".join(item.rejection_reasons) if item.rejection_reasons else "-"
        leverage_cell = "-"
        if item.max_leverage > 0 and (
            item.leverage_used > 0
            or "leverage_limit_exceeded" in item.rejection_reasons
        ):
            leverage_cell = f"{item.leverage_used:.2f}/{item.max_leverage:.2f}"

        lines.append(
            f"| {i} | {item.symbol} | {item.buy_venue} -> {item.sell_venue} | {item.gross_edge_bps:.2f} | {item.net_edge_bps:.2f} | {item.borrow_cost_bps:.2f} | {item.leverage_notional_usd:.2f} | {leverage_cell} | {item.risk_score:.2f} | {item.dominant_drag} | {'✅' if item.is_qualified else '❌'} | {reasons} |"
        )

    lines.extend(["", "## Notes", "- This dashboard is for screening only, not execution advice."])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Score opportunity candidates with risk gates.")
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="Input opportunity JSON list")
    p.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON, help="Output scored JSON")
    p.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD, help="Output dashboard markdown")
    p.add_argument("--output-summary", type=Path, default=DEFAULT_OUTPUT_SUMMARY, help="Output rejection summary JSON")

    p.add_argument(
        "--execution-profile",
        choices=sorted(EXECUTION_PROFILES.keys()),
        default="taker_default",
        help="Execution friction profile for scenario scoring.",
    )

    p.add_argument(
        "--constraints",
        type=Path,
        default=DEFAULT_CONSTRAINTS_PATH,
        help="Execution constraints JSON (inventory/borrow/position).",
    )
    p.add_argument(
        "--fee-table",
        type=Path,
        default=DEFAULT_FEE_TABLE_PATH,
        help="Execution fee table JSON (venue/instrument taker-maker-vip bps).",
    )

    p.add_argument("--fee-multiplier", type=float, default=None)
    p.add_argument("--slippage-multiplier", type=float, default=None)
    p.add_argument("--latency-multiplier", type=float, default=None)
    p.add_argument("--transfer-delay-multiplier", type=float, default=None)

    p.add_argument("--transfer-penalty-bps-per-min", type=float, default=None)
    p.add_argument("--min-net-edge-bps", type=float, default=None)
    p.add_argument("--max-risk-score", type=float, default=None)

    return p.parse_args()


def main() -> None:
    args = parse_args()
    data = json.loads(args.input.read_text())

    profile = EXECUTION_PROFILES[args.execution_profile]
    fee_table = FeeTable.from_path(args.fee_table)

    fee_multiplier = (
        float(args.fee_multiplier)
        if args.fee_multiplier is not None
        else (1.0 if fee_table.enabled else float(profile["fee_multiplier"]))
    )
    slippage_multiplier = (
        float(args.slippage_multiplier)
        if args.slippage_multiplier is not None
        else float(profile["slippage_multiplier"])
    )
    latency_multiplier = (
        float(args.latency_multiplier)
        if args.latency_multiplier is not None
        else float(profile["latency_multiplier"])
    )
    transfer_delay_multiplier = (
        float(args.transfer_delay_multiplier)
        if args.transfer_delay_multiplier is not None
        else float(profile["transfer_delay_multiplier"])
    )

    transfer_penalty_bps_per_min = (
        float(args.transfer_penalty_bps_per_min)
        if args.transfer_penalty_bps_per_min is not None
        else float(profile.get("transfer_penalty_bps_per_min", DEFAULT_TRANSFER_PENALTY_BPS_PER_MIN))
    )
    min_net_edge_bps = (
        float(args.min_net_edge_bps)
        if args.min_net_edge_bps is not None
        else float(profile.get("min_net_edge_bps", DEFAULT_MIN_NET_EDGE_BPS))
    )
    max_risk_score = (
        float(args.max_risk_score)
        if args.max_risk_score is not None
        else float(profile.get("max_risk_score", DEFAULT_MAX_RISK_SCORE))
    )

    constraint_book = ConstraintBook.from_path(args.constraints)
    constraints_path = args.constraints if constraint_book.enabled else None
    fee_table_path = args.fee_table if fee_table.enabled else None

    scored = [
        score_item(
            item,
            execution_profile=args.execution_profile,
            fee_multiplier=fee_multiplier,
            slippage_multiplier=slippage_multiplier,
            latency_multiplier=latency_multiplier,
            transfer_delay_multiplier=transfer_delay_multiplier,
            transfer_penalty_bps_per_min=transfer_penalty_bps_per_min,
            min_net_edge_bps=min_net_edge_bps,
            max_risk_score=max_risk_score,
            constraint_book=constraint_book,
            fee_table=fee_table,
        )
        for item in data
    ]

    scored_sorted = sorted(scored, key=lambda x: (x.is_qualified, x.net_edge_bps), reverse=True)
    summary = _build_summary(
        scored_sorted,
        input_path=args.input,
        constraints_path=constraints_path,
        fee_table_path=fee_table_path,
        execution_profile=args.execution_profile,
        fee_multiplier=fee_multiplier,
        slippage_multiplier=slippage_multiplier,
        latency_multiplier=latency_multiplier,
        transfer_delay_multiplier=transfer_delay_multiplier,
        transfer_penalty_bps_per_min=transfer_penalty_bps_per_min,
        min_net_edge_bps=min_net_edge_bps,
        max_risk_score=max_risk_score,
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_summary.parent.mkdir(parents=True, exist_ok=True)

    args.output_json.write_text(json.dumps([asdict(item) for item in scored_sorted], indent=2))
    args.output_md.write_text(
        render_markdown(
            scored_sorted,
            input_path=args.input,
            constraints_path=constraints_path,
            fee_table_path=fee_table_path,
            execution_profile=args.execution_profile,
            fee_multiplier=fee_multiplier,
            slippage_multiplier=slippage_multiplier,
            latency_multiplier=latency_multiplier,
            transfer_delay_multiplier=transfer_delay_multiplier,
            transfer_penalty_bps_per_min=transfer_penalty_bps_per_min,
            min_net_edge_bps=min_net_edge_bps,
            max_risk_score=max_risk_score,
        )
    )
    args.output_summary.write_text(json.dumps(summary, indent=2))

    print(f"Scored {len(scored)} candidates.")
    print(f"Qualified: {sum(1 for item in scored if item.is_qualified)}")
    print(f"Execution profile: {args.execution_profile}")
    print(f"Constraints enabled: {constraint_book.enabled}")
    if constraint_book.enabled:
        print(f"Constraints path: {args.constraints}")
    print(f"Fee table enabled: {fee_table.enabled}")
    if fee_table.enabled:
        print(f"Fee table path: {args.fee_table}")
    print(f"Wrote: {args.output_json}")
    print(f"Wrote: {args.output_md}")
    print(f"Wrote: {args.output_summary}")


if __name__ == "__main__":
    main()
