# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T12:05:34.577107+00:00`
Input: `data/opportunity_candidates.combined.live.json`
Execution profile: `maker_inventory`
Constraints: `data/execution_constraints.latest.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk - borrow cost (0.24 bps/min transfer penalty)
- Profile multipliers: fees×0.42, slippage×0.72, latency×0.95, transfer_delay×0.3
- Qualified if `net_edge_bps >= 4.5` and `risk_score <= 0.62`

## Summary
- Candidates: **31**
- Qualified: **0**
- Rejected: **31**

## Rejection Breakdown
- By reason:
  - `net_edge_below_threshold`: **31**
  - `fee_dominated`: **31**
  - `slippage_dominated`: **31**
  - `borrow_dominated`: **20**
  - `latency_transfer_dominated`: **17**
- Dominant drag:
  - `fees`: **31**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Borrow bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---:|---|:---:|---|
| 1 | SOL/USDT | jupiter -> binance | 1.67 | -8.76 | 0.06 | 0.25 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 2 | ETH/USDT | binance -> bybit | 0.76 | -9.43 | 0.08 | 0.24 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 3 | BTC/USDT | binance -> bybit | 0.42 | -9.44 | 0.08 | 0.24 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | BNB/USDT | binance -> bybit | 1.76 | -9.51 | 0.15 | 0.25 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 5 | SOL/USDT | jupiter -> bybit | 0.49 | -11.07 | 0.06 | 0.26 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 6 | AVAX/USDT | long_binance_perp -> short_bybit_perp | 1.30 | -14.88 | 0.00 | 0.31 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 7 | BNB/USDT | long_binance_perp -> short_bybit_perp | 0.93 | -15.25 | 0.00 | 0.31 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 8 | SOL/USDT | long_bybit_perp -> short_binance_perp | 0.58 | -15.60 | 0.00 | 0.31 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 9 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 0.52 | -15.65 | 0.00 | 0.31 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 10 | BTC/USDT | long_bybit_perp -> short_binance_perp | 0.46 | -15.72 | 0.00 | 0.31 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 11 | LINK/USDT | long_bybit_perp -> short_binance_perp | 0.45 | -15.73 | 0.00 | 0.31 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 12 | SOL/USDT | long_binance_perp -> short_binance_spot | 2.37 | -16.87 | 3.38 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 13 | ETH/USDT | long_binance_perp -> short_binance_spot | 0.64 | -18.56 | 3.38 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 14 | BTC/USDT | long_binance_perp -> short_binance_spot | 0.59 | -18.60 | 3.38 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 15 | LINK/USDT | long_binance_perp -> short_binance_spot | 2.95 | -18.92 | 5.98 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 16 | ADA/USDT | long_binance_perp -> short_binance_spot | 2.81 | -19.01 | 5.98 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 17 | LTC/USDT | long_binance_perp -> short_binance_spot | 2.77 | -19.07 | 5.98 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 18 | AVAX/USDT | long_binance_perp -> short_binance_spot | 2.74 | -19.08 | 5.98 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 19 | DOGE/USDT | long_binance_perp -> short_binance_spot | 2.68 | -19.15 | 5.98 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 20 | XRP/USDT | long_binance_perp -> short_binance_spot | 2.10 | -19.72 | 5.98 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 21 | SOL/USDT | long_bybit_perp -> short_bybit_spot | 2.98 | -19.78 | 3.38 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 22 | BNB/USDT | long_binance_spot -> short_binance_perp | 0.93 | -20.88 | 5.98 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 23 | BTC/USDT | long_bybit_perp -> short_bybit_spot | 1.23 | -21.50 | 3.38 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 24 | ETH/USDT | long_bybit_perp -> short_bybit_spot | 1.14 | -21.59 | 3.38 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 25 | LINK/USDT | long_bybit_perp -> short_bybit_spot | 3.15 | -22.23 | 5.98 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 26 | LTC/USDT | long_bybit_perp -> short_bybit_spot | 2.53 | -22.83 | 5.98 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 27 | XRP/USDT | long_bybit_perp -> short_bybit_spot | 2.47 | -22.91 | 5.98 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 28 | ADA/USDT | long_bybit_perp -> short_bybit_spot | 2.42 | -22.92 | 5.98 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 29 | DOGE/USDT | long_bybit_perp -> short_bybit_spot | 2.25 | -23.11 | 5.98 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated |
| 30 | AVAX/USDT | long_bybit_perp -> short_bybit_spot | 1.68 | -23.69 | 5.98 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |
| 31 | BNB/USDT | long_bybit_perp -> short_bybit_spot | 0.66 | -24.71 | 5.98 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
