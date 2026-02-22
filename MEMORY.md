# MEMORY

Long-term distilled memory for trading/arbitrage work.

## What We Know
- Net-edge screening must include transfer-delay penalty, not only spread and fees.
- A high gross spread can still fail quality gate after fees/slippage/latency adjustments.
- First scanner pass produced 1/4 qualified candidates under strict gates (sample set, not live trading signal).
- First live Binance/Bybit top-of-book scan produced 0/3 qualified after full friction math; raw spread alone is not enough.

## What We Believe (Needs Validation)
- Funding/basis setups may survive risk gates more often than cross-chain spot dislocations in congested periods.
- Cross-chain routes are highly sensitive to delay penalty assumptions.

## Hard Rules
- Never ignore fees/slippage/latency in arb math.
- No trade without explicit invalidation condition.
- Capital preservation > FOMO.
- No opportunity enters shortlist without `gross edge - fees - slippage - latency/transfer risk` breakdown.

## Lessons
- Gross edge without execution friction data is noise.
- Risk gate should be pass/fail before any manual excitement about potential PnL.
- Cross-exchange top-of-book CEX spread is usually too thin to survive taker+taker fees; either improve fee tier, pre-position inventory, or move to other strategy buckets.
