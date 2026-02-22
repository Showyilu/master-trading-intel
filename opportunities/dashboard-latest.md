# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T08:03:50.405003+00:00`
Input: `data/opportunity_candidates.combined.live.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk (0.45 bps/min)
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **13**
- Qualified: **0**
- Rejected: **13**

## Rejection Breakdown
- By reason:
  - `net_edge_below_threshold`: **13**
  - `fee_dominated`: **13**
  - `latency_transfer_dominated`: **13**
  - `slippage_dominated`: **12**
- Dominant drag:
  - `fees`: **13**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---|:---:|---|
| 1 | SOL/USDT | jupiter -> binance | 2.21 | -19.33 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, latency_transfer_dominated |
| 2 | ETH/USDT | binance -> bybit | 0.91 | -21.47 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 3 | BTC/USDT | binance -> bybit | 0.47 | -21.64 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | BNB/USDT | binance -> bybit | 0.80 | -22.39 | 0.41 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 5 | SOL/USDT | jupiter -> bybit | 1.03 | -23.10 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 6 | DOGE/USDT | binance -> bybit | 2.06 | -24.30 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 7 | LINK/USDT | long_binance_perp -> short_bybit_perp | 1.99 | -29.39 | 0.50 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 8 | BNB/USDT | long_binance_perp -> short_bybit_perp | 1.00 | -30.38 | 0.50 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 9 | AVAX/USDT | long_bybit_perp -> short_binance_perp | 0.98 | -30.40 | 0.50 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 10 | LTC/USDT | long_binance_perp -> short_bybit_perp | 0.87 | -30.50 | 0.50 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 11 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 0.71 | -30.67 | 0.50 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 12 | SOL/USDT | long_bybit_perp -> short_binance_perp | 0.62 | -30.76 | 0.50 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 13 | BTC/USDT | long_binance_perp -> short_bybit_perp | 0.48 | -30.90 | 0.50 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
