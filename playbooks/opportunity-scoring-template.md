# Opportunity Scoring + Risk Template (v1)

## 1) Required Inputs (per opportunity)
- `gross_edge_bps`
- `fees_bps` (taker/maker + borrowing + funding where relevant)
- `slippage_bps` (size-aware)
- `latency_risk_bps`
- `transfer_delay_min`
- `size_usd`
- `borrow_rate_bps_per_hour`, `hold_hours`, `borrow_used_usd`
- `available_inventory_usd`, `max_leverage`
- `strategy_leverage_notional_multiplier`

## 2) Net Edge Formula

`net_edge_bps = gross_edge_bps - fees_bps - slippage_bps - latency_risk_bps - transfer_risk_bps - borrow_cost_bps`

`transfer_risk_bps = transfer_delay_min * penalty_bps_per_min`

`borrow_cost_bps = borrow_rate_bps_per_hour * hold_hours * (borrow_used_usd / size_usd)`

Default transfer penalty: `0.45 bps/min` (profile-adjustable).

## 3) Hard Risk Gates
- Minimum edge gate: `net_edge_bps >= threshold_by_profile`
- Maximum risk gate: `risk_score <= threshold_by_profile`
- Position cap: `size_usd <= max_position_usd`
- Borrow cap: `borrow_required_usd <= max_borrow_usd`
- Leverage cap:
  - `required_notional_usd = size_usd * strategy_leverage_notional_multiplier`
  - `leverage_used = required_notional_usd / available_inventory_usd`
  - Require `leverage_used <= max_leverage`
- If any gate fails: **not executable**.

## 4) Risk Score Components (0-1)
- Fee pressure (18%)
- Slippage pressure (22%)
- Latency pressure (16%)
- Transfer uncertainty (16%)
- Borrow pressure (14%)
- Edge buffer fragility (14%)

## 5) Execution Checklist
- Confirm depth at target size (not just top-of-book).
- Confirm transfer route + fallback route.
- Recompute net edge immediately before order submission.
- Validate leverage headroom and borrow room on actual account snapshot.
- Define stop/abort condition before first leg.

## 6) Hard Rules
- No fee/slippage/latency estimate => no trade.
- No invalidation condition => no trade.
- Missing leverage/borrow constraints => no trade.
- Preserve capital first; skip marginal setups.
