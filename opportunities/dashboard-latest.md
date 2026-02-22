# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T18:03:16.984879+00:00`
Input: `data/opportunity_candidates.combined.live.json`
Execution profile: `taker_default`
Constraints: `data/execution_constraints.latest.json`
Fee table: `data/execution_fee_table.latest.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk - borrow cost (0.45 bps/min transfer penalty)
- Profile multipliers: fees×1.0, slippage×1.0, latency×1.0, transfer_delay×1.0
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **31**
- Qualified: **0**
- Rejected: **31**
- Fee-model applied: **31**

## Rejection Breakdown
- By reason:
  - `net_edge_below_threshold`: **31**
  - `fee_dominated`: **31**
  - `slippage_dominated`: **29**
  - `latency_transfer_dominated`: **22**
  - `borrow_dominated`: **18**
- Dominant drag:
  - `fees`: **31**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Borrow bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---:|---|:---:|---|
| 1 | SOL/USDT | jupiter -> binance | 2.05 | -24.22 | 0.06 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, latency_transfer_dominated |
| 2 | BTC/USDT | binance -> bybit | 0.27 | -24.44 | 0.08 | 0.38 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 3 | ETH/USDT | binance -> bybit | 0.46 | -25.12 | 0.08 | 0.39 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | SOL/USDT | jupiter -> bybit | 0.84 | -25.52 | 0.06 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 5 | SOL/USDT | bybit -> binance | 1.20 | -26.59 | 0.08 | 0.41 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 6 | DOGE/USDT | binance -> bybit | 1.05 | -28.57 | 0.15 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 7 | ADA/USDT | long_bybit_perp -> short_binance_perp | 1.83 | -28.85 | 0.00 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 8 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 1.17 | -29.51 | 0.00 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 9 | BNB/USDT | long_bybit_perp -> short_binance_perp | 1.02 | -29.67 | 0.00 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 10 | SOL/USDT | long_bybit_perp -> short_binance_perp | 1.01 | -29.67 | 0.00 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 11 | AVAX/USDT | long_bybit_perp -> short_binance_perp | 0.90 | -29.79 | 0.00 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 12 | BTC/USDT | long_bybit_perp -> short_binance_perp | 0.66 | -30.02 | 0.00 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 13 | LINK/USDT | long_binance_perp -> short_bybit_perp | 0.46 | -30.22 | 0.00 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 14 | AVAX/USDT | long_binance_perp -> short_binance_spot | 5.78 | -37.21 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, borrow_dominated |
| 15 | SOL/USDT | long_binance_perp -> short_binance_spot | 2.16 | -38.13 | 3.38 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 16 | ETH/USDT | long_binance_perp -> short_binance_spot | 1.43 | -38.82 | 3.38 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 17 | XRP/USDT | long_binance_perp -> short_binance_spot | 3.23 | -39.65 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 18 | SOL/USDT | long_bybit_perp -> short_bybit_spot | 2.69 | -39.97 | 3.38 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 19 | LINK/USDT | long_binance_perp -> short_binance_spot | 2.87 | -40.07 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 20 | ETH/USDT | long_bybit_perp -> short_bybit_spot | 1.94 | -40.73 | 3.38 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 21 | DOGE/USDT | long_binance_perp -> short_binance_spot | 1.76 | -41.09 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 22 | ADA/USDT | long_bybit_perp -> short_bybit_spot | 4.15 | -41.17 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 23 | ADA/USDT | long_binance_perp -> short_binance_spot | 1.42 | -41.44 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 24 | LTC/USDT | long_binance_perp -> short_binance_spot | 1.40 | -41.48 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 25 | BTC/USDT | long_bybit_perp -> short_bybit_spot | 0.89 | -41.76 | 3.38 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 26 | BNB/USDT | long_binance_spot -> short_binance_perp | 0.54 | -42.28 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 27 | XRP/USDT | long_bybit_perp -> short_bybit_spot | 2.97 | -42.32 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 28 | BNB/USDT | long_bybit_perp -> short_bybit_spot | 2.60 | -42.69 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 29 | LINK/USDT | long_bybit_perp -> short_bybit_spot | 2.15 | -43.17 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 30 | DOGE/USDT | long_bybit_perp -> short_bybit_spot | 1.28 | -44.02 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 31 | LTC/USDT | long_bybit_perp -> short_bybit_spot | 1.08 | -44.18 | 5.98 | 0.49 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
