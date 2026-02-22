# Plan: Become the Master of This Domain

## North Star
Use structured knowledge + fast iteration to consistently surface high-quality trading and arbitrage setups.

## Current Sprint (2026-02-22)
1. ✅ Build source inventory + normalization schema (`sources/inventory.yaml`, `schemas/normalized_opportunity_v1.schema.json`).
2. ✅ Build opportunity scoring template and hard risk gates (`playbooks/opportunity-scoring-template.md`).
3. ✅ Build first scanner + dashboard output (`scripts/scan_opportunities.py`, `opportunities/dashboard-latest.md`).
4. ✅ Replaced sample-first flow with live CEX pullers (Binance/Bybit) -> normalized quotes -> live candidate file.
5. ✅ Added live DEX adapter (Jupiter) + CEX-DEX candidate builder + merged dashboard flow (`scripts/build_live_cex_dex_candidates.py`, `scripts/merge_candidate_files.py`).
6. ✅ Added sanity guards to block false edges (reference deviation + crossed-book checks for DEX quotes).
7. ✅ Added rejection-reason aggregation + dominant-friction breakdown in scanner outputs (`opportunities/rejection-summary-latest.json`).
8. ✅ Added size-aware orderbook/depth slippage model (1k/5k/10k USD tiers) for Binance/Bybit (`data/cex_depth_slippage_latest.json`).
9. ✅ Added funding live adapter (Binance/Bybit perp) + carry candidate builder (`scripts/build_live_funding_candidates.py`).
10. ✅ Added perp-spot basis live adapter (Binance/Bybit) + candidate builder (`scripts/build_live_basis_candidates.py`).
11. ✅ Added execution profile scenarios in scanner (`taker_default` / `maker_inventory` / `maker_inventory_vip`) and profile playbook (`playbooks/execution-profiles.md`).
12. ✅ Added execution-constraint layer (`data/execution_constraints.latest.json`) + template builder (`scripts/build_execution_constraints_template.py`) and wired scanner hard gates for position cap / inventory / borrow capacity with borrow carry cost in net-edge math.
13. ✅ Added venue/instrument fee-table layer (`data/execution_fee_table.latest.json`) + template builder (`scripts/build_execution_fee_table_template.py`) and wired scanner to consume explicit taker/maker/vip bps instead of only embedded candidate fees.
14. ⏭ Next: replace template constraints + fee table with authenticated venue inputs (account balances, margin limits, borrow books, real fee tiers/rebates) so hard gates and fee math use live capacity, not heuristics.

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
