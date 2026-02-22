# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T20:02:59.581840+00:00`
Input: `data/opportunity_candidates.combined.live.json`
Execution profile: `taker_default`
Constraints: `data/execution_constraints.latest.json`
Fee table: `data/execution_fee_table.latest.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk - borrow cost (0.45 bps/min transfer penalty)
- Profile multipliers: fees×1.0, slippage×1.0, latency×1.0, transfer_delay×1.0
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **30**
- Qualified: **0**
- Rejected: **30**
- Fee-model applied: **30**

## Rejection Breakdown
- By reason:
  - `net_edge_below_threshold`: **30**
  - `fee_dominated`: **30**
  - `slippage_dominated`: **27**
  - `latency_transfer_dominated`: **20**
  - `borrow_dominated`: **18**
- Dominant drag:
  - `fees`: **30**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Borrow bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---:|---|:---:|---|
| 1 | SOL/USDT | jupiter -> binance | 3.72 | -22.21 | 0.06 | 0.41 | fees | ❌ | net_edge_below_threshold, fee_dominated, latency_transfer_dominated |
| 2 | SOL/USDT | jupiter -> bybit | 2.52 | -23.51 | 0.06 | 0.41 | fees | ❌ | net_edge_below_threshold, fee_dominated, latency_transfer_dominated |
| 3 | BTC/USDT | bybit -> binance | 0.77 | -23.93 | 0.08 | 0.38 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | ETH/USDT | binance -> bybit | 0.46 | -24.28 | 0.08 | 0.38 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 5 | ADA/USDT | long_bybit_perp -> short_binance_perp | 3.13 | -26.85 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 6 | SOL/USDT | long_bybit_perp -> short_binance_perp | 1.09 | -28.89 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 7 | BTC/USDT | long_bybit_perp -> short_binance_perp | 0.91 | -29.08 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 8 | XRP/USDT | long_binance_perp -> short_bybit_perp | 0.86 | -29.13 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 9 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 0.78 | -29.20 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 10 | AVAX/USDT | long_binance_perp -> short_bybit_perp | 0.76 | -29.22 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 11 | BNB/USDT | long_bybit_perp -> short_binance_perp | 0.59 | -29.39 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 12 | LINK/USDT | long_binance_perp -> short_bybit_perp | 0.58 | -29.41 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 13 | AVAX/USDT | long_binance_perp -> short_binance_spot | 5.48 | -37.02 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, borrow_dominated |
| 14 | SOL/USDT | long_binance_perp -> short_binance_spot | 2.37 | -37.53 | 3.38 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 15 | ETH/USDT | long_binance_perp -> short_binance_spot | 1.39 | -38.47 | 3.38 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 16 | XRP/USDT | long_binance_perp -> short_binance_spot | 3.56 | -38.91 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 17 | SOL/USDT | long_bybit_perp -> short_bybit_spot | 3.20 | -39.08 | 3.38 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 18 | ADA/USDT | long_bybit_perp -> short_bybit_spot | 5.03 | -39.83 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 19 | DOGE/USDT | long_binance_perp -> short_binance_spot | 1.95 | -40.52 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 20 | ADA/USDT | long_binance_perp -> short_binance_spot | 1.90 | -40.56 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 21 | ETH/USDT | long_bybit_perp -> short_bybit_spot | 1.66 | -40.61 | 3.38 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 22 | LTC/USDT | long_binance_perp -> short_binance_spot | 1.62 | -40.89 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 23 | LINK/USDT | long_binance_perp -> short_binance_spot | 1.21 | -41.19 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 24 | BTC/USDT | long_bybit_perp -> short_bybit_spot | 0.91 | -41.33 | 3.38 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 25 | BNB/USDT | long_binance_spot -> short_binance_perp | 0.66 | -41.76 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 26 | XRP/USDT | long_bybit_perp -> short_bybit_spot | 2.71 | -42.17 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 27 | BNB/USDT | long_bybit_perp -> short_bybit_spot | 2.39 | -42.52 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 28 | DOGE/USDT | long_bybit_perp -> short_bybit_spot | 1.40 | -43.49 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 29 | LTC/USDT | long_bybit_perp -> short_bybit_spot | 1.24 | -43.64 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 30 | LINK/USDT | long_bybit_perp -> short_bybit_spot | 0.64 | -44.16 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
