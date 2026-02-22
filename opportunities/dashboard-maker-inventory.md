# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T14:07:42.385086+00:00`
Input: `data/opportunity_candidates.combined.live.json`
Execution profile: `maker_inventory`
Constraints: `data/execution_constraints.latest.json`
Fee table: `data/execution_fee_table.latest.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk - borrow cost (0.24 bps/min transfer penalty)
- Profile multipliers: fees×1.0, slippage×0.72, latency×0.95, transfer_delay×0.3
- Qualified if `net_edge_bps >= 4.5` and `risk_score <= 0.62`

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
  - `latency_transfer_dominated`: **16**
- Dominant drag:
  - `fees`: **30**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Borrow bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---:|---|:---:|---|
| 1 | BNB/USDT | long_binance_perp -> short_bybit_perp | 0.81 | -13.21 | 0.00 | 0.28 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 2 | LTC/USDT | long_binance_perp -> short_bybit_perp | 0.78 | -13.24 | 0.00 | 0.28 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 3 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 0.62 | -13.39 | 0.00 | 0.28 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | AVAX/USDT | long_binance_perp -> short_bybit_perp | 0.59 | -13.42 | 0.00 | 0.28 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 5 | ADA/USDT | long_binance_perp -> short_bybit_perp | 0.57 | -13.44 | 0.00 | 0.28 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 6 | XRP/USDT | long_binance_perp -> short_bybit_perp | 0.49 | -13.53 | 0.00 | 0.28 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 7 | BTC/USDT | long_bybit_perp -> short_binance_perp | 0.41 | -13.61 | 0.00 | 0.28 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 8 | SOL/USDT | jupiter -> binance | 1.22 | -18.29 | 0.06 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 9 | BTC/USDT | bybit -> binance | 1.45 | -19.49 | 0.08 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 10 | BNB/USDT | binance -> bybit | 0.65 | -20.73 | 0.15 | 0.35 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 11 | DOGE/USDT | binance -> bybit | 2.09 | -21.10 | 0.15 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 12 | SOL/USDT | long_binance_perp -> short_binance_spot | 1.87 | -26.07 | 3.38 | 0.41 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 13 | ETH/USDT | long_binance_perp -> short_binance_spot | 1.35 | -26.60 | 3.38 | 0.41 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 14 | ADA/USDT | long_binance_perp -> short_binance_spot | 3.46 | -27.15 | 5.98 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 15 | BTC/USDT | long_binance_perp -> short_binance_spot | 0.68 | -27.26 | 3.38 | 0.41 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 16 | SOL/USDT | long_bybit_perp -> short_bybit_spot | 1.62 | -27.32 | 3.38 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 17 | ETH/USDT | long_bybit_perp -> short_bybit_spot | 1.64 | -27.33 | 3.38 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 18 | BTC/USDT | long_bybit_perp -> short_bybit_spot | 1.05 | -27.89 | 3.38 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 19 | XRP/USDT | long_binance_perp -> short_binance_spot | 2.65 | -27.91 | 5.98 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 20 | DOGE/USDT | long_binance_perp -> short_binance_spot | 2.47 | -28.11 | 5.98 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 21 | LINK/USDT | long_binance_perp -> short_binance_spot | 2.34 | -28.23 | 5.98 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 22 | LTC/USDT | long_binance_perp -> short_binance_spot | 1.71 | -28.83 | 5.98 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 23 | XRP/USDT | long_bybit_perp -> short_bybit_spot | 2.08 | -29.49 | 5.98 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 24 | ADA/USDT | long_bybit_perp -> short_bybit_spot | 2.07 | -29.49 | 5.98 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 25 | DOGE/USDT | long_bybit_perp -> short_bybit_spot | 1.84 | -29.74 | 5.98 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 26 | AVAX/USDT | long_binance_perp -> short_binance_spot | 0.64 | -29.86 | 5.98 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 27 | LINK/USDT | long_bybit_perp -> short_bybit_spot | 1.66 | -29.89 | 5.98 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 28 | BNB/USDT | long_binance_spot -> short_binance_perp | 0.46 | -30.04 | 5.98 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 29 | BNB/USDT | long_bybit_perp -> short_bybit_spot | 1.15 | -30.47 | 5.98 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 30 | LTC/USDT | long_bybit_perp -> short_bybit_spot | 0.52 | -31.01 | 5.98 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
