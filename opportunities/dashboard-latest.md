# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T04:01:38.435459+00:00`
Input: `data/opportunity_candidates.combined.live.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk (0.45 bps/min)
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **3**
- Qualified: **0**
- Rejected: **3**

## Rejection Breakdown
- By reason:
  - `net_edge_below_threshold`: **3**
  - `fee_dominated`: **3**
  - `latency_transfer_dominated`: **3**
  - `slippage_dominated`: **2**
- Dominant drag:
  - `fees`: **3**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---|:---:|---|
| 1 | SOL/USDT | jupiter -> binance | 3.15 | -18.21 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, latency_transfer_dominated |
| 2 | SOL/USDT | bybit -> binance | 2.35 | -21.26 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 3 | BNB/USDT | binance -> bybit | 0.97 | -22.46 | 0.41 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
