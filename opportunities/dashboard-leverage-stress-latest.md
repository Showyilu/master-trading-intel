# Opportunity Dashboard (Latest)

Generated at: `2026-02-23T04:02:43.183028+00:00`
Input: `data/opportunity_candidates.combined.live.json`
Execution profile: `maker_inventory`
Constraints: `data/execution_constraints.latest.json`
Fee table: `data/execution_fee_table.latest.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk - borrow cost (0.24 bps/min transfer penalty)
- Profile multipliers: fees×1.0, slippage×0.72, latency×0.95, transfer_delay×0.3
- Qualified if `net_edge_bps >= 4.5` and `risk_score <= 0.62`
- Runtime leverage overrides: `funding_carry_cex_cex=2.5000, perp_spot_basis=1.5000`

## Summary
- Candidates: **30**
- Qualified: **0**
- Rejected: **30**
- Fee-model applied: **30**

## Rejection Breakdown
- By reason:
  - `net_edge_below_threshold`: **30**
  - `fee_dominated`: **30**
  - `leverage_limit_exceeded`: **26**
  - `slippage_dominated`: **24**
  - `borrow_dominated`: **18**
  - `latency_transfer_dominated`: **17**
- Dominant drag:
  - `fees`: **30**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Borrow bps | Lev Notional USD | Lev (used/cap) | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---:|---|---:|---|:---:|---|
| 1 | ADA/USDT | long_bybit_perp -> short_binance_perp | 3.13 | -11.57 | 0.00 | 25000.00 | 7.14/2.50 | 0.29 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, leverage_limit_exceeded |
| 2 | SOL/USDT | long_bybit_perp -> short_binance_perp | 1.09 | -13.61 | 0.00 | 25000.00 | 7.14/3.00 | 0.29 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, leverage_limit_exceeded |
| 3 | BTC/USDT | long_bybit_perp -> short_binance_perp | 0.91 | -13.80 | 0.00 | 25000.00 | 7.14/3.00 | 0.29 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, leverage_limit_exceeded |
| 4 | XRP/USDT | long_binance_perp -> short_bybit_perp | 0.86 | -13.85 | 0.00 | 25000.00 | 7.14/2.50 | 0.29 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, leverage_limit_exceeded |
| 5 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 0.78 | -13.92 | 0.00 | 25000.00 | 7.14/2.50 | 0.29 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, leverage_limit_exceeded |
| 6 | AVAX/USDT | long_binance_perp -> short_bybit_perp | 0.76 | -13.95 | 0.00 | 25000.00 | 7.14/2.50 | 0.29 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, leverage_limit_exceeded |
| 7 | BNB/USDT | long_bybit_perp -> short_binance_perp | 0.59 | -14.11 | 0.00 | 25000.00 | 7.14/2.50 | 0.29 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, leverage_limit_exceeded |
| 8 | LINK/USDT | long_binance_perp -> short_bybit_perp | 0.58 | -14.13 | 0.00 | 25000.00 | 7.14/2.50 | 0.29 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, leverage_limit_exceeded |
| 9 | SOL/USDT | jupiter -> binance | 3.72 | -15.09 | 0.06 | 5000.00 | 1.43/3.00 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated |
| 10 | SOL/USDT | jupiter -> bybit | 2.52 | -16.38 | 0.06 | 5000.00 | 1.43/3.00 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, latency_transfer_dominated |
| 11 | BTC/USDT | bybit -> binance | 0.77 | -17.72 | 0.08 | 10000.00 | 2.86/3.00 | 0.32 | fees | ❌ | net_edge_below_threshold, fee_dominated, latency_transfer_dominated |
| 12 | ETH/USDT | binance -> bybit | 0.46 | -18.07 | 0.08 | 10000.00 | 2.86/3.00 | 0.32 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 13 | AVAX/USDT | long_binance_perp -> short_binance_spot | 5.48 | -25.50 | 5.98 | 15000.00 | 4.29/2.50 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, borrow_dominated, leverage_limit_exceeded |
| 14 | SOL/USDT | long_binance_perp -> short_binance_spot | 2.37 | -26.01 | 3.38 | 15000.00 | 4.29/3.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated, leverage_limit_exceeded |
| 15 | SOL/USDT | long_bybit_perp -> short_bybit_spot | 3.20 | -26.17 | 3.38 | 15000.00 | 4.29/3.00 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated, leverage_limit_exceeded |
| 16 | ADA/USDT | long_bybit_perp -> short_bybit_spot | 5.03 | -26.92 | 5.98 | 15000.00 | 4.29/2.50 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, borrow_dominated, leverage_limit_exceeded |
| 17 | ETH/USDT | long_binance_perp -> short_binance_spot | 1.39 | -26.95 | 3.38 | 15000.00 | 4.29/3.00 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated, leverage_limit_exceeded |
| 18 | XRP/USDT | long_binance_perp -> short_binance_spot | 3.56 | -27.40 | 5.98 | 15000.00 | 4.29/2.50 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, borrow_dominated, leverage_limit_exceeded |
| 19 | ETH/USDT | long_bybit_perp -> short_bybit_spot | 1.66 | -27.70 | 3.38 | 15000.00 | 4.29/3.00 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated, leverage_limit_exceeded |
| 20 | BTC/USDT | long_bybit_perp -> short_bybit_spot | 0.91 | -28.43 | 3.38 | 15000.00 | 4.29/3.00 | 0.43 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated, leverage_limit_exceeded |
| 21 | DOGE/USDT | long_binance_perp -> short_binance_spot | 1.95 | -29.00 | 5.98 | 15000.00 | 4.29/2.50 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated, leverage_limit_exceeded |
| 22 | ADA/USDT | long_binance_perp -> short_binance_spot | 1.90 | -29.05 | 5.98 | 15000.00 | 4.29/2.50 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated, leverage_limit_exceeded |
| 23 | XRP/USDT | long_bybit_perp -> short_bybit_spot | 2.71 | -29.26 | 5.98 | 15000.00 | 4.29/2.50 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated, leverage_limit_exceeded |
| 24 | LTC/USDT | long_binance_perp -> short_binance_spot | 1.62 | -29.37 | 5.98 | 15000.00 | 4.29/2.50 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated, leverage_limit_exceeded |
| 25 | BNB/USDT | long_bybit_perp -> short_bybit_spot | 2.39 | -29.60 | 5.98 | 15000.00 | 4.29/2.50 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, borrow_dominated, leverage_limit_exceeded |
| 26 | LINK/USDT | long_binance_perp -> short_binance_spot | 1.21 | -29.67 | 5.98 | 15000.00 | 4.29/2.50 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated, leverage_limit_exceeded |
| 27 | BNB/USDT | long_binance_spot -> short_binance_perp | 0.66 | -30.25 | 5.98 | 15000.00 | 4.29/2.50 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated, leverage_limit_exceeded |
| 28 | DOGE/USDT | long_bybit_perp -> short_bybit_spot | 1.40 | -30.58 | 5.98 | 15000.00 | 4.29/2.50 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated, leverage_limit_exceeded |
| 29 | LTC/USDT | long_bybit_perp -> short_bybit_spot | 1.24 | -30.73 | 5.98 | 15000.00 | 4.29/2.50 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated, leverage_limit_exceeded |
| 30 | LINK/USDT | long_bybit_perp -> short_bybit_spot | 0.64 | -31.26 | 5.98 | 15000.00 | 4.29/2.50 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated, borrow_dominated, leverage_limit_exceeded |

## Notes
- This dashboard is for screening only, not execution advice.
