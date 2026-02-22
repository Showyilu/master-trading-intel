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
- Perp-spot basis adapter is live (Binance/Bybit same-venue spot+perp): basis + funding components are normalized and scored under conservative capture assumptions.
- Execution-profile scenario scoring is now built into scanner (`taker_default`, `maker_inventory`, `maker_inventory_vip`) so friction assumptions are explicit and reproducible.
- Scanner now supports hard execution constraints per venue/asset (position cap, available inventory, borrow cap) and includes borrow carry cost in net-edge math.
- Constraint template generation is automated from current candidate universe (`scripts/build_execution_constraints_template.py`), so capacity assumptions are versioned and reproducible.
- Scanner now supports an explicit venue/instrument fee table (`data/execution_fee_table.latest.json`) with profile-aware fee modes (taker/maker/maker_vip) and strategy round-trip multipliers, so fee assumptions are versioned instead of hidden inside candidate builders.
- CEX-DEX candidate builder now consumes a live network-friction model (`data/network_friction.latest.json`) and applies `router_fee_bps + network_fee_bps` for Jupiter legs, reducing static-fee blind spots.
- Fee table pipeline now supports authenticated overlay (`scripts/build_authenticated_fee_table.py`): Binance/Bybit signed endpoints can replace template fee assumptions with account-realized rates while preserving deterministic fallback when auth is missing.

## What We Believe (Needs Validation)
- Funding/basis setups may survive risk gates more often than cross-chain spot dislocations in congested periods.
- Cross-chain routes are highly sensitive to delay penalty assumptions.

## Hard Rules
- Never ignore fees/slippage/latency in arb math.
- No trade without explicit invalidation condition.
- Capital preservation > FOMO.
- No opportunity enters shortlist without `gross edge - fees - slippage - latency/transfer risk` breakdown.
- When constraints file is enabled, candidates must also pass position/inventory/borrow capacity gates before qualification.
- Reject cross-venue quotes when DEX mid deviates too far from trusted CEX reference (depeg/wrapped-token hazard).
- Every scanner run must expose rejection-reason counts so strategy work is guided by the biggest friction bucket, not intuition.

## Lessons
- Gross edge without execution friction data is noise.
- Risk gate should be pass/fail before any manual excitement about potential PnL.
- Cross-exchange top-of-book CEX spread is usually too thin to survive taker+taker fees; either improve fee tier, pre-position inventory, or move to other strategy buckets.
- DEX adapter output must include quote-quality gates (reference deviation / crossed book) before scoring, otherwise scanner will overfit to broken routes.
- Even with depth-aware slippage, dominant drag can still be fees; venue fee tier and inventory location are first-order levers before chasing more symbols.
- Funding-rate differentials can look attractive gross, but round-trip execution costs can fully consume the edge unless fee tier and hold window are tightly controlled.
- Perp-spot basis gross edges (~2-3 bps in this universe) are far below round-trip friction at taker fee assumptions; without true maker/borrow advantages they remain non-executable.
- Even under a softer `maker_inventory` scenario, if `fee_dominated` stays the top rejection reason, the next optimization target is fee/borrow structure—not broader symbol coverage.
- Borrow carry can dominate basis net edge over multi-hour holds; ignoring borrow terms overstates executability.
- Fee assumptions should live in a dedicated fee table with venue/instrument granularity; burying fees inside each adapter makes profile testing opaque and non-reproducible.
- DEX fee modeling also needs a chain-cost input (network congestion + base fee); even when cost is tiny (e.g., Solana), explicit modeling improves reproducibility and avoids silent drift.
- Authenticated adapters should be fail-soft and schema-compatible: if keys are absent, keep template assumptions and continue scoring instead of breaking the pipeline.
