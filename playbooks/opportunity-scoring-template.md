# Opportunity Scoring + Risk Template (v1)

## 1) Required Inputs (per opportunity)
- `gross_edge_bps`
- `fees_bps` (taker/maker + borrowing + funding where relevant)
- `slippage_bps` (size-aware)
- `latency_risk_bps`
- `transfer_delay_min`
- `size_usd`

## 2) Net Edge Formula

`net_edge_bps = gross_edge_bps - fees_bps - slippage_bps - latency_risk_bps - transfer_risk_bps`

`transfer_risk_bps = transfer_delay_min * penalty_bps_per_min`

Default penalty: `0.45 bps/min` (adjust by venue reliability and chain congestion).

## 3) Risk Gate
- Minimum edge gate: `net_edge_bps >= 8`
- Maximum risk gate: `risk_score <= 0.60`
- If either fails: do **not** enter execution queue.

## 4) Risk Score Components (0-1)
- Fee pressure (20%)
- Slippage pressure (25%)
- Latency pressure (20%)
- Transfer uncertainty (20%)
- Edge buffer fragility (15%)

## 5) Execution Checklist
- Confirm depth at target size (not just top-of-book).
- Confirm transfer route + fallback route.
- Recompute net edge immediately before order submission.
- Define stop/abort condition before first leg.

## 6) Hard Rules
- No fee/slippage/latency estimate => no trade.
- No invalidation condition => no trade.
- Preserve capital first; skip marginal setups.
