# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T03:05:54.901370+00:00`
Input: `data/opportunity_candidates.live.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk (0.45 bps/min)
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **3**
- Qualified: **0**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Risk | Qualified |
|---:|---|---|---:|---:|---:|:---:|
| 1 | BNB/USDT | binance -> bybit | 2.24 | -21.05 | 0.41 | ❌ |
| 2 | ETH/USDT | binance -> bybit | 0.56 | -21.99 | 0.40 | ❌ |
| 3 | BTC/USDT | binance -> bybit | 0.48 | -22.03 | 0.40 | ❌ |

## Notes
- This dashboard is for screening only, not execution advice.
