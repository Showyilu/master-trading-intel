# MEMORY

Long-term distilled memory for trading/arbitrage work.

## What We Know
- Net-edge screening must include transfer-delay penalty, not only spread and fees.
- A high gross spread can still fail quality gate after fees/slippage/latency adjustments.
- First scanner pass produced 1/4 qualified candidates under strict gates (sample set, not live trading signal).
- First live Binance/Bybit top-of-book scan produced 0/3 qualified after full friction math; raw spread alone is not enough.
- Jupiter DEX integration works for live quotes, but wrapped-token routes can produce massive false edges without reference-price sanity checks.
- After adding DEX reference-deviation guard and crossed-quote guard, false BTC route signals were filtered out and shortlist returned to 0 qualified (expected under strict friction model).
- Rejection-reason aggregation is now part of baseline output: every rejected candidate tags explicit causes (fee/slippage/latency/threshold) plus dominant friction drag.
- CEX scanner now uses orderbook depth-derived slippage curves (1k/5k/10k USD tiers) instead of spread-only heuristic when depth data is available.
- Funding carry adapter is live (Binance/Bybit perp): cross-venue funding deltas are now normalized and scored with explicit round-trip fees/slippage/hold-time risk.

## What We Believe (Needs Validation)
- Funding/basis setups may survive risk gates more often than cross-chain spot dislocations in congested periods.
- Cross-chain routes are highly sensitive to delay penalty assumptions.

## Hard Rules
- Never ignore fees/slippage/latency in arb math.
- No trade without explicit invalidation condition.
- Capital preservation > FOMO.
- No opportunity enters shortlist without `gross edge - fees - slippage - latency/transfer risk` breakdown.
- Reject cross-venue quotes when DEX mid deviates too far from trusted CEX reference (depeg/wrapped-token hazard).
- Every scanner run must expose rejection-reason counts so strategy work is guided by the biggest friction bucket, not intuition.

## Lessons
- Gross edge without execution friction data is noise.
- Risk gate should be pass/fail before any manual excitement about potential PnL.
- Cross-exchange top-of-book CEX spread is usually too thin to survive taker+taker fees; either improve fee tier, pre-position inventory, or move to other strategy buckets.
- DEX adapter output must include quote-quality gates (reference deviation / crossed book) before scoring, otherwise scanner will overfit to broken routes.
- Even with depth-aware slippage, dominant drag can still be fees; venue fee tier and inventory location are first-order levers before chasing more symbols.
- Funding-rate differentials can look attractive gross, but round-trip execution costs can fully consume the edge unless fee tier and hold window are tightly controlled.
