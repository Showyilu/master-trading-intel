# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T03:01:43.845528+00:00`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk (0.45 bps/min)
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **4**
- Qualified: **1**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Risk | Qualified |
|---:|---|---|---:|---:|---:|:---:|
| 1 | BTC-PERP | binance_spot -> bybit_perp | 18.90 | 9.90 | 0.12 | ✅ |
| 2 | BTC/USDT | bybit -> binance | 21.30 | 5.95 | 0.26 | ❌ |
| 3 | ETH/USDC | uniswap-v3 -> binance | 34.80 | 5.80 | 0.44 | ❌ |
| 4 | SOL/USDC | jupiter -> binance | 18.10 | -2.50 | 0.44 | ❌ |

## Notes
- This dashboard is for screening only, not execution advice.
