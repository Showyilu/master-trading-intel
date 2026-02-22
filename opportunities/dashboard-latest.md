# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T14:07:21.218608+00:00`
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
  - `slippage_dominated`: **30**
  - `borrow_dominated`: **19**
  - `latency_transfer_dominated`: **17**
- Dominant drag:
  - `fees`: **30**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Borrow bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---:|---|:---:|---|
| 1 | SOL/USDT | jupiter -> binance | 1.22 | -25.62 | 0.06 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 2 | BTC/USDT | bybit -> binance | 1.45 | -26.67 | 0.08 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 3 | BNB/USDT | binance -> bybit | 0.65 | -28.02 | 0.15 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | BNB/USDT | long_binance_perp -> short_bybit_perp | 0.81 | -28.45 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 5 | LTC/USDT | long_binance_perp -> short_bybit_perp | 0.78 | -28.48 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 6 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 0.62 | -28.63 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 7 | AVAX/USDT | long_binance_perp -> short_bybit_perp | 0.59 | -28.66 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 8 | ADA/USDT | long_binance_perp -> short_bybit_perp | 0.57 | -28.68 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 9 | XRP/USDT | long_binance_perp -> short_bybit_perp | 0.49 | -28.77 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 10 | BTC/USDT | long_bybit_perp -> short_binance_perp | 0.41 | -28.85 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 11 | DOGE/USDT | binance -> bybit | 2.09 | -29.15 | 0.15 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 12 | SOL/USDT | long_binance_perp -> short_binance_spot | 1.87 | -37.56 | 3.38 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 13 | ETH/USDT | long_binance_perp -> short_binance_spot | 1.35 | -38.10 | 3.38 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 14 | ADA/USDT | long_binance_perp -> short_binance_spot | 3.46 | -38.65 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 15 | BTC/USDT | long_binance_perp -> short_binance_spot | 0.68 | -38.75 | 3.38 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 16 | XRP/USDT | long_binance_perp -> short_binance_spot | 2.65 | -39.41 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 17 | DOGE/USDT | long_binance_perp -> short_binance_spot | 2.47 | -39.60 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 18 | LINK/USDT | long_binance_perp -> short_binance_spot | 2.34 | -39.73 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 19 | SOL/USDT | long_bybit_perp -> short_bybit_spot | 1.62 | -40.21 | 3.38 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 20 | ETH/USDT | long_bybit_perp -> short_bybit_spot | 1.64 | -40.22 | 3.38 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 21 | LTC/USDT | long_binance_perp -> short_binance_spot | 1.71 | -40.33 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 22 | BTC/USDT | long_bybit_perp -> short_bybit_spot | 1.05 | -40.78 | 3.38 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 23 | AVAX/USDT | long_binance_perp -> short_binance_spot | 0.64 | -41.36 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 24 | BNB/USDT | long_binance_spot -> short_binance_perp | 0.46 | -41.54 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 25 | XRP/USDT | long_bybit_perp -> short_bybit_spot | 2.08 | -42.38 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 26 | ADA/USDT | long_bybit_perp -> short_bybit_spot | 2.07 | -42.38 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 27 | DOGE/USDT | long_bybit_perp -> short_bybit_spot | 1.84 | -42.63 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 28 | LINK/USDT | long_bybit_perp -> short_bybit_spot | 1.66 | -42.78 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 29 | BNB/USDT | long_bybit_perp -> short_bybit_spot | 1.15 | -43.36 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 30 | LTC/USDT | long_bybit_perp -> short_bybit_spot | 0.52 | -43.89 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
