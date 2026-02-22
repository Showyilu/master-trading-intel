# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T10:05:20.542876+00:00`
Input: `data/opportunity_candidates.combined.live.json`
Execution profile: `taker_default`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk (0.45 bps/min)
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
  - `slippage_dominated`: **31**
  - `latency_transfer_dominated`: **18**
- Dominant drag:
  - `fees`: **31**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Risk | Drag | Qualified | Rejection Reasons |
|---:|---|---|---:|---:|---:|---|:---:|---|
| 1 | SOL/USDT | jupiter -> binance | 1.67 | -20.74 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 2 | BTC/USDT | binance -> bybit | 0.42 | -21.70 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 3 | ETH/USDT | binance -> bybit | 0.76 | -21.84 | 0.40 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 4 | BNB/USDT | binance -> bybit | 1.76 | -22.28 | 0.42 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 5 | SOL/USDT | jupiter -> bybit | 0.49 | -24.51 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 6 | LINK/USDT | long_binance_perp -> short_binance_spot | 2.95 | -28.98 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 7 | ADA/USDT | long_binance_perp -> short_binance_spot | 2.81 | -29.07 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 8 | LTC/USDT | long_binance_perp -> short_binance_spot | 2.77 | -29.13 | 0.45 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 9 | AVAX/USDT | long_binance_perp -> short_binance_spot | 2.74 | -29.14 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 10 | DOGE/USDT | long_binance_perp -> short_binance_spot | 2.68 | -29.21 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 11 | AVAX/USDT | long_binance_perp -> short_bybit_perp | 1.30 | -29.37 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 12 | SOL/USDT | long_binance_perp -> short_binance_spot | 2.37 | -29.52 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 13 | BNB/USDT | long_binance_perp -> short_bybit_perp | 0.93 | -29.74 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 14 | XRP/USDT | long_binance_perp -> short_binance_spot | 2.10 | -29.78 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 15 | SOL/USDT | long_bybit_perp -> short_binance_perp | 0.58 | -30.09 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 16 | DOGE/USDT | long_binance_perp -> short_bybit_perp | 0.52 | -30.15 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 17 | BTC/USDT | long_bybit_perp -> short_binance_perp | 0.46 | -30.21 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 18 | LINK/USDT | long_bybit_perp -> short_binance_perp | 0.45 | -30.22 | 0.48 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 19 | BNB/USDT | long_binance_spot -> short_binance_perp | 0.93 | -30.93 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 20 | ETH/USDT | long_binance_perp -> short_binance_spot | 0.64 | -31.21 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 21 | BTC/USDT | long_binance_perp -> short_binance_spot | 0.59 | -31.25 | 0.44 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 22 | LINK/USDT | long_bybit_perp -> short_bybit_spot | 3.15 | -36.16 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 23 | SOL/USDT | long_bybit_perp -> short_bybit_spot | 2.98 | -36.31 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 24 | LTC/USDT | long_bybit_perp -> short_bybit_spot | 2.53 | -36.76 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 25 | XRP/USDT | long_bybit_perp -> short_bybit_spot | 2.47 | -36.84 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 26 | ADA/USDT | long_bybit_perp -> short_bybit_spot | 2.42 | -36.85 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 27 | DOGE/USDT | long_bybit_perp -> short_bybit_spot | 2.25 | -37.04 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated |
| 28 | AVAX/USDT | long_bybit_perp -> short_bybit_spot | 1.68 | -37.62 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 29 | BTC/USDT | long_bybit_perp -> short_bybit_spot | 1.23 | -38.03 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 30 | ETH/USDT | long_bybit_perp -> short_bybit_spot | 1.14 | -38.12 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |
| 31 | BNB/USDT | long_bybit_perp -> short_bybit_spot | 0.66 | -38.64 | 0.46 | fees | ❌ | net_edge_below_threshold, fee_dominated, slippage_dominated, latency_transfer_dominated |

## Notes
- This dashboard is for screening only, not execution advice.
