# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T06:02:24.328245+00:00`
Input: `data/opportunity_candidates.combined.live.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk (0.45 bps/min)
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **7**
- Qualified: **0**
- Rejected: **7**

## Rejection Breakdown
- By reason:
  - `net_edge_below_threshold`: **7**
  - `fee_dominated`: **7**
  - `latency_transfer_dominated`: **7**
  - `slippage_dominated`: **6**
- Dominant drag:
  - `fees`: **7**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---|:---:|---|
| 1 | SOL/USDT | jupiter -> binance | 2.67 | -19.07 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, latency_transfer_dominated |
| 2 | BTC/USDT | bybit -> binance | 0.77 | -21.31 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 3 | ETH/USDT | bybit -> binance | 0.20 | -21.98 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | BNB/USDT | binance -> bybit | 1.61 | -23.23 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 5 | SOL/USDT | bybit -> binance | 1.18 | -23.32 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 6 | SOL/USDT | jupiter -> bybit | 0.32 | -24.11 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 7 | DOGE/USDT | binance -> bybit | 1.03 | -24.28 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
