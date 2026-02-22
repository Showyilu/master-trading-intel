# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T03:17:43.786681+00:00`
Input: `data/opportunity_candidates.combined.live.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk (0.45 bps/min)
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **4**
- Qualified: **0**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Risk | Qualified |
|---:|---|---|---:|---:|---:|:---:|
| 1 | BTC/USDT | bybit -> binance | 0.75 | -21.74 | 0.40 | ❌ |
| 2 | SOL/USDT | bybit -> binance | 1.18 | -22.55 | 0.42 | ❌ |
| 3 | DOGE/USDT | binance -> bybit | 1.03 | -22.55 | 0.42 | ❌ |
| 4 | BNB/USDT | binance -> bybit | 0.48 | -22.99 | 0.42 | ❌ |

## Notes
- This dashboard is for screening only, not execution advice.
