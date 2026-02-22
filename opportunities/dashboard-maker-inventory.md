# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T10:05:20.587312+00:00`
Input: `data/opportunity_candidates.combined.live.json`
Execution profile: `maker_inventory`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk (0.24 bps/min)
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
  - `latency_transfer_dominated`: **17**
- Dominant drag:
  - `fees`: **31**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---|:---:|---|
| 1 | SOL/USDT | jupiter -> binance | 1.67 | -8.70 | 0.28 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 2 | ETH/USDT | binance -> bybit | 0.76 | -9.35 | 0.27 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 3 | BTC/USDT | binance -> bybit | 0.42 | -9.35 | 0.26 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | BNB/USDT | binance -> bybit | 1.76 | -9.36 | 0.28 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 5 | SOL/USDT | jupiter -> bybit | 0.49 | -11.01 | 0.30 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 6 | LINK/USDT | long_binance_perp -> short_binance_spot | 2.95 | -12.94 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 7 | ADA/USDT | long_binance_perp -> short_binance_spot | 2.81 | -13.03 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 8 | LTC/USDT | long_binance_perp -> short_binance_spot | 2.77 | -13.09 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 9 | AVAX/USDT | long_binance_perp -> short_binance_spot | 2.74 | -13.10 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 10 | DOGE/USDT | long_binance_perp -> short_binance_spot | 2.68 | -13.17 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 11 | SOL/USDT | long_binance_perp -> short_binance_spot | 2.37 | -13.49 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 12 | XRP/USDT | long_binance_perp -> short_binance_spot | 2.10 | -13.74 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 13 | AVAX/USDT | long_binance_perp -> short_bybit_perp | 1.30 | -14.88 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 14 | BNB/USDT | long_binance_spot -> short_binance_perp | 0.93 | -14.90 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 15 | ETH/USDT | long_binance_perp -> short_binance_spot | 0.64 | -15.18 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 16 | BTC/USDT | long_binance_perp -> short_binance_spot | 0.59 | -15.22 | 0.33 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 17 | BNB/USDT | long_binance_perp -> short_bybit_perp | 0.93 | -15.25 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 18 | SOL/USDT | long_bybit_perp -> short_binance_perp | 0.58 | -15.60 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 19 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 0.52 | -15.65 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 20 | BTC/USDT | long_bybit_perp -> short_binance_perp | 0.46 | -15.72 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 21 | LINK/USDT | long_bybit_perp -> short_binance_perp | 0.45 | -15.73 | 0.34 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 22 | LINK/USDT | long_bybit_perp -> short_bybit_spot | 3.15 | -16.25 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 23 | SOL/USDT | long_bybit_perp -> short_bybit_spot | 2.98 | -16.40 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 24 | LTC/USDT | long_bybit_perp -> short_bybit_spot | 2.53 | -16.85 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 25 | XRP/USDT | long_bybit_perp -> short_bybit_spot | 2.47 | -16.93 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 26 | ADA/USDT | long_bybit_perp -> short_bybit_spot | 2.42 | -16.94 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 27 | DOGE/USDT | long_bybit_perp -> short_bybit_spot | 2.25 | -17.13 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 28 | AVAX/USDT | long_bybit_perp -> short_bybit_spot | 1.68 | -17.71 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 29 | BTC/USDT | long_bybit_perp -> short_bybit_spot | 1.23 | -18.12 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 30 | ETH/USDT | long_bybit_perp -> short_bybit_spot | 1.14 | -18.21 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 31 | BNB/USDT | long_bybit_perp -> short_bybit_spot | 0.66 | -18.73 | 0.37 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
