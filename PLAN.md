# Plan: Become the Master of This Domain

## North Star
Use structured knowledge + fast iteration to consistently surface high-quality trading and arbitrage setups.

## Current Sprint (2026-02-22)
1. ✅ Build source inventory + normalization schema (`sources/inventory.yaml`, `schemas/normalized_opportunity_v1.schema.json`).
2. ✅ Build opportunity scoring template and hard risk gates (`playbooks/opportunity-scoring-template.md`).
3. ✅ Build first scanner + dashboard output (`scripts/scan_opportunities.py`, `opportunities/dashboard-latest.md`).
4. ✅ Replaced sample-first flow with live CEX pullers (Binance/Bybit) -> normalized quotes -> live candidate file.
5. ⏭ Next: add DEX quote source + size-aware orderbook/depth slippage model (avoid top-of-book illusion).

## Phase 1 — Foundation (Week 1)
1. Define market coverage: CEX spot/perp, DEX spot/perp, funding, basis, cross-chain.
2. Build source map: exchange APIs, on-chain data, socials/news, calendars.
3. Standardize opportunity template and scoring rubric.

## Phase 2 — Signal Engine (Week 2-3)
1. Track 3 buckets: momentum, mean reversion, structural arb.
2. Add automated checks for: spread, fees, slippage, transfer time, counterparty risk.
3. Rank opportunities by expected value and execution confidence.

## Phase 3 — Execution Discipline (Week 3-4)
1. Position sizing rules and max drawdown limits.
2. Pre-trade checklist + kill-switch conditions.
3. Post-trade review loop: what worked, what failed, why.

## Phase 4 — Compounding Intelligence (Ongoing)
1. Convert repeated wins into SOPs.
2. Convert losses into hard constraints.
3. Weekly strategy review and monthly pruning of bad edges.

## Cadence
- Daily: scan -> shortlist -> validate -> decide
- Weekly: update playbooks + memory
- Monthly: retire weak strategies, double down on proven ones
