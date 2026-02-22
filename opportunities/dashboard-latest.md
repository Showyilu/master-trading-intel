# Opportunity Dashboard (Latest)

Generated at: `2026-02-22T03:11:19.342310+00:00`
Input: `data/opportunity_candidates.combined.live.json`

## Rules
- Net edge (bps) = gross - fees - slippage - latency risk - transfer risk (0.45 bps/min)
- Qualified if `net_edge_bps >= 8.0` and `risk_score <= 0.6`

## Summary
- Candidates: **6**
- Qualified: **0**

## Ranked Candidates

| Rank | Pair | Path | Gross bps | Net bps | Risk | Qualified |
|---:|---|---|---:|---:|---:|:---:|
| 1 | SOL/USDT | jupiter -> binance | 2.28 | -20.46 | 0.44 | ❌ |
| 2 | SOL/USDT | bybit -> binance | 2.35 | -21.26 | 0.42 | ❌ |
| 3 | BNB/USDT | binance -> bybit | 1.60 | -21.76 | 0.41 | ❌ |
| 4 | BTC/USDT | binance -> bybit | 0.62 | -21.87 | 0.40 | ❌ |
| 5 | ETH/USDT | binance -> bybit | 0.66 | -21.88 | 0.40 | ❌ |
| 6 | DOGE/USDT | binance -> bybit | 1.03 | -22.55 | 0.42 | ❌ |

## Notes
- This dashboard is for screening only, not execution advice.
