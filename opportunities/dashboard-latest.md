# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T16:05:06.491092+00:00`
Input: `data/opportunity_candidates.combined.live.json`
Execution profile: `taker_default`
Constraints: `data/execution_constraints.latest.json`
Fee table: `data/execution_fee_table.latest.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk - borrow cost (0.45 bps/min transfer penalty)
- Profile multipliers: fees×1.0, slippage×1.0, latency×1.0, transfer_delay×1.0
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **34**
- Qualified: **0**
- Rejected: **34**
- Fee-model applied: **34**

## Rejection Breakdown
- By reason:
  - `net_edge_below_threshold`: **34**
  - `fee_dominated`: **34**
  - `slippage_dominated`: **34**
  - `latency_transfer_dominated`: **29**
  - `borrow_dominated`: **20**
- Dominant drag:
  - `fees`: **34**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Borrow bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---:|---|:---:|---|
| 1 | BTC/USDT | binance -> bybit | 0.42 | -24.28 | 0.08 | 0.38 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 2 | SOL/USDT | jupiter -> binance | 1.39 | -24.80 | 0.06 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 3 | SOL/USDT | jupiter -> bybit | 1.39 | -24.80 | 0.06 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | ETH/USDT | binance -> bybit | 0.41 | -25.06 | 0.08 | 0.39 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 5 | AVAX/USDT | long_bybit_perp -> short_binance_perp | 5.45 | -25.92 | 0.00 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 6 | BNB/USDT | binance -> bybit | 0.81 | -26.93 | 0.15 | 0.41 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 7 | DOGE/USDT | binance -> bybit | 1.04 | -27.50 | 0.15 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 8 | LINK/USDT | long_binance_perp -> short_bybit_perp | 1.33 | -30.04 | 0.00 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 9 | ADA/USDT | long_bybit_perp -> short_binance_perp | 0.79 | -30.58 | 0.00 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 10 | LTC/USDT | long_binance_perp -> short_bybit_perp | 0.71 | -30.66 | 0.00 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 11 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 0.48 | -30.89 | 0.00 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 12 | SOL/USDT | long_bybit_perp -> short_binance_perp | 0.48 | -30.89 | 0.00 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 13 | BTC/USDT | long_bybit_perp -> short_binance_perp | 0.45 | -30.92 | 0.00 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 14 | BNB/USDT | long_binance_perp -> short_bybit_perp | 0.43 | -30.94 | 0.00 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 15 | AVAX/USDT | long_binance_perp -> short_binance_spot | 4.41 | -39.00 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 16 | SOL/USDT | long_binance_perp -> short_binance_spot | 1.57 | -39.07 | 3.38 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 17 | ETH/USDT | long_binance_perp -> short_binance_spot | 1.53 | -39.12 | 3.38 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 18 | BTC/USDT | long_binance_perp -> short_binance_spot | 0.27 | -40.36 | 3.38 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 19 | SOL/USDT | long_bybit_perp -> short_bybit_spot | 2.57 | -40.50 | 3.38 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 20 | XRP/USDT | long_binance_perp -> short_binance_spot | 2.35 | -40.90 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 21 | AVAX/USDT | long_bybit_perp -> short_bybit_spot | 4.67 | -40.94 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 22 | ETH/USDT | long_bybit_perp -> short_bybit_spot | 1.91 | -41.15 | 3.38 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 23 | ADA/USDT | long_binance_perp -> short_binance_spot | 2.06 | -41.20 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 24 | DOGE/USDT | long_binance_perp -> short_binance_spot | 1.86 | -41.39 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 25 | LTC/USDT | long_binance_perp -> short_binance_spot | 1.81 | -41.49 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 26 | BTC/USDT | long_bybit_perp -> short_bybit_spot | 1.07 | -41.98 | 3.38 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 27 | LINK/USDT | long_binance_perp -> short_binance_spot | 1.09 | -42.13 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 28 | BNB/USDT | long_binance_spot -> short_binance_perp | 0.62 | -42.60 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 29 | XRP/USDT | long_bybit_perp -> short_bybit_spot | 2.72 | -42.95 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 30 | ADA/USDT | long_bybit_perp -> short_bybit_spot | 1.87 | -43.79 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 31 | DOGE/USDT | long_bybit_perp -> short_bybit_spot | 1.44 | -44.25 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 32 | LTC/USDT | long_bybit_perp -> short_bybit_spot | 1.22 | -44.43 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 33 | BNB/USDT | long_bybit_perp -> short_bybit_spot | 1.17 | -44.51 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 34 | LINK/USDT | long_bybit_perp -> short_bybit_spot | 0.35 | -45.28 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
