# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T12:05:53.497076+00:00`
Input: `data/opportunity_candidates.combined.live.json`
Execution profile: `taker_default`
Constraints: `data/execution_constraints.latest.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk - borrow cost (0.45 bps/min transfer penalty)
- Profile multipliers: fees×1.0, slippage×1.0, latency×1.0, transfer_delay×1.0
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **31**
- Qualified: **0**
- Rejected: **31**

## Rejection Breakdown
- By reason:
  - `net_edge_below_threshold`: **31**
  - `fee_dominated`: **31**
  - `slippage_dominated`: **28**
  - `borrow_dominated`: **20**
  - `latency_transfer_dominated`: **18**
- Dominant drag:
  - `fees`: **31**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Borrow bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---:|---|:---:|---|
| 1 | SOL/USDT | jupiter -> binance | 3.24 | -18.11 | 0.06 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, latency_transfer_dominated |
| 2 | SOL/USDT | bybit -> binance | 3.53 | -20.12 | 0.08 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated |
| 3 | BNB/USDT | binance -> bybit | 2.73 | -21.53 | 0.15 | 0.38 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | SOL/USDT | bybit -> jupiter | 2.06 | -21.95 | 0.13 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, latency_transfer_dominated |
| 5 | AVAX/USDT | long_binance_perp -> short_bybit_perp | 1.12 | -28.85 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 6 | BNB/USDT | long_binance_perp -> short_bybit_perp | 1.00 | -28.97 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 7 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 0.89 | -29.07 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 8 | LTC/USDT | long_binance_perp -> short_bybit_perp | 0.86 | -29.11 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 9 | ADA/USDT | long_binance_perp -> short_bybit_perp | 0.84 | -29.12 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 10 | XRP/USDT | long_binance_perp -> short_bybit_perp | 0.61 | -29.36 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 11 | BTC/USDT | long_bybit_perp -> short_binance_perp | 0.40 | -29.56 | 0.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 12 | SOL/USDT | long_binance_perp -> short_binance_spot | 2.90 | -32.00 | 3.38 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 13 | ETH/USDT | long_binance_perp -> short_binance_spot | 0.76 | -34.08 | 3.38 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 14 | ADA/USDT | long_binance_perp -> short_binance_spot | 3.39 | -34.10 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 15 | BTC/USDT | long_binance_perp -> short_binance_spot | 0.54 | -34.28 | 3.38 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 16 | XRP/USDT | long_binance_perp -> short_binance_spot | 2.66 | -34.81 | 5.98 | 0.47 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 17 | LTC/USDT | long_binance_perp -> short_binance_spot | 2.37 | -35.07 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 18 | DOGE/USDT | long_binance_perp -> short_binance_spot | 2.33 | -35.11 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 19 | AVAX/USDT | long_binance_perp -> short_binance_spot | 2.04 | -35.40 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 20 | LINK/USDT | long_binance_perp -> short_binance_spot | 1.52 | -35.90 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 21 | BNB/USDT | long_binance_spot -> short_binance_perp | 0.60 | -36.81 | 5.98 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 22 | SOL/USDT | long_bybit_perp -> short_bybit_spot | 1.68 | -40.53 | 3.38 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 23 | BTC/USDT | long_bybit_perp -> short_bybit_spot | 1.12 | -41.12 | 3.38 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 24 | ETH/USDT | long_bybit_perp -> short_bybit_spot | 0.84 | -41.40 | 3.38 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 25 | LTC/USDT | long_bybit_perp -> short_bybit_spot | 2.33 | -42.57 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 26 | XRP/USDT | long_bybit_perp -> short_bybit_spot | 2.21 | -42.67 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 27 | DOGE/USDT | long_bybit_perp -> short_bybit_spot | 2.12 | -42.77 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 28 | ADA/USDT | long_bybit_perp -> short_bybit_spot | 2.06 | -42.79 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 29 | LINK/USDT | long_bybit_perp -> short_bybit_spot | 2.02 | -42.82 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 30 | AVAX/USDT | long_bybit_perp -> short_bybit_spot | 1.66 | -43.23 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 31 | BNB/USDT | long_bybit_perp -> short_bybit_spot | 0.55 | -44.33 | 5.98 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
