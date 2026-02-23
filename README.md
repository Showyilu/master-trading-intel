# Master Trading Intel

This repository is the AI's long-term knowledge base and execution workspace for finding:

- Trading opportunities
- Arbitrage opportunities
- Repeatable edges in crypto and adjacent markets

## Mission
Build a compounding research engine: detect signals fast, validate rigorously, execute only when risk/reward is clear.

## Repo Structure
- `PLAN.md` — roadmap and operating plan
- `MEMORY.md` — distilled long-term learning
- `playbooks/` — strategy frameworks and SOPs
- `opportunities/` — live opportunities and post-mortems
- `journal/` — timestamped daily research logs
- `sources/` — trusted data sources and monitoring list
- `schemas/` — normalization schemas
- `scripts/` — scanner and scoring utilities
- `data/` — local sample inputs / fixtures

## Quickstart

### 1) Sample pipeline
```bash
python3 scripts/scan_opportunities.py
```

### 2) Live CEX snapshot pipeline (Binance + Bybit)
```bash
python3 scripts/build_live_cex_candidates.py \
  --size-usd 10000 \
  --size-tiers-usd 1000 5000 10000
python3 scripts/scan_opportunities.py \
  --input data/opportunity_candidates.live.json \
  --output-json opportunities/shortlist-latest.json \
  --output-md opportunities/dashboard-latest.md
```

`build_live_cex_candidates.py` now includes orderbook depth modeling and writes per-symbol slippage curves by notional tier.

### 3) Live CEX + DEX + funding + perp-spot basis pipeline (Binance/Bybit + Jupiter)
```bash
python3 scripts/build_live_cex_candidates.py
python3 scripts/build_network_friction.py
python3 scripts/build_live_cex_dex_candidates.py
python3 scripts/build_live_funding_candidates.py
python3 scripts/build_live_basis_candidates.py
python3 scripts/merge_candidate_files.py \
  --inputs \
    data/opportunity_candidates.live.json \
    data/opportunity_candidates.cex_dex.live.json \
    data/opportunity_candidates.funding.live.json \
    data/opportunity_candidates.basis.live.json \
  --output data/opportunity_candidates.combined.live.json
python3 scripts/build_execution_constraints_template.py \
  --input data/opportunity_candidates.combined.live.json \
  --output data/execution_constraints.latest.json
python3 scripts/build_authenticated_constraints.py \
  --constraints data/execution_constraints.latest.json \
  --quotes data/normalized_quotes_cex_latest.json
python3 scripts/build_execution_fee_table_template.py \
  --input data/opportunity_candidates.combined.live.json \
  --output data/execution_fee_table.latest.json
python3 scripts/build_authenticated_fee_table.py \
  --input-candidates data/opportunity_candidates.combined.live.json \
  --fee-table data/execution_fee_table.latest.json
python3 scripts/scan_opportunities.py \
  --input data/opportunity_candidates.combined.live.json \
  --constraints data/execution_constraints.latest.json \
  --fee-table data/execution_fee_table.latest.json \
  --execution-profile taker_default \
  --output-json opportunities/shortlist-latest.json \
  --output-md opportunities/dashboard-latest.md
```

Outputs:
- `data/normalized_quotes_cex_latest.json`
- `data/normalized_quotes_dex_latest.json`
- `data/normalized_funding_latest.json`
- `data/normalized_basis_latest.json`
- `data/opportunity_candidates.live.json`
- `data/cex_depth_slippage_latest.json`
- `data/network_friction.latest.json`
- `data/opportunity_candidates.cex_dex.live.json`
- `data/opportunity_candidates.funding.live.json`
- `data/opportunity_candidates.basis.live.json`
- `data/opportunity_candidates.combined.live.json`
- `data/execution_constraints.latest.json` (venue/asset inventory, borrow, leverage and position-cap template)
- `data/execution_fee_table.latest.json` (venue/instrument taker-maker-vip fee table; template first, then authenticated overlay when API keys exist)
- `opportunities/shortlist-latest.json`
- `opportunities/dashboard-latest.md`
- `opportunities/rejection-summary-latest.json` (rejection reason / friction-drag aggregation)

Execution profile scenarios (scanner):
- `taker_default` (strict baseline)
- `maker_inventory` (pre-positioned inventory + partial maker execution)
- `maker_inventory_vip` (best-case low-fee profile)

Scanner now also enforces hard execution constraints when `--constraints` is provided:
- venue/asset `max_position_usd`
- sell-side `available_inventory_usd`
- `max_borrow_usd` + borrow carry cost (`borrow_rate_bps_per_hour × hold_hours`)
- leverage hard gate via `max_leverage` (`leverage_limit_exceeded` will reject candidate)
- strategy-level leverage notional multipliers (`strategy_leverage_notional_multiplier`) so required leverage is explicit per strategy (e.g. funding carry default 2.0x notional)
- runtime leverage stress-test overrides via repeated `--strategy-leverage-override STRATEGY=MULTIPLIER` (e.g. `funding_carry_cex_cex=2.5`)

Example stress-test run:
```bash
python3 scripts/scan_opportunities.py \
  --input data/opportunity_candidates.combined.live.json \
  --constraints data/execution_constraints.latest.json \
  --fee-table data/execution_fee_table.latest.json \
  --execution-profile maker_inventory \
  --strategy-leverage-override funding_carry_cex_cex=2.5 \
  --strategy-leverage-override perp_spot_basis=1.5 \
  --output-json opportunities/shortlist-leverage-stress-latest.json \
  --output-md opportunities/dashboard-leverage-stress-latest.md \
  --output-summary opportunities/rejection-summary-leverage-stress-latest.json
```

Scanner can load explicit fee assumptions with `--fee-table`:
- per-venue + per-instrument `taker_bps` / `maker_bps` / `maker_vip_bps`
- profile-to-fee-mode mapping (`taker_default` / `maker_inventory` / `maker_inventory_vip`)
- strategy round-trip side multipliers (e.g. funding/basis open+close cost)

`build_authenticated_constraints.py` can overlay template constraints with authenticated account data:
- `available_inventory_usd` becomes account-realized inventory value (Binance/Bybit wallet snapshots)
- Binance margin overlay also updates:
  - `max_borrow_usd` from signed `maxBorrowable`
  - `borrow_rate_bps_per_hour` from signed next-hour interest endpoint
- `max_position_usd` is clipped conservatively to `min(existing_cap, inventory + max_borrow, inventory × max_leverage)` when leverage cap is configured
- credentials: `BINANCE_API_KEY` / `BINANCE_API_SECRET` / `BYBIT_API_KEY` / `BYBIT_API_SECRET`

If auth is unavailable (or endpoint calls fail), it fails soft and keeps template constraints.

`build_authenticated_fee_table.py` can overlay account-realized fees for Binance/Bybit when credentials are present:
- `BINANCE_API_KEY` / `BINANCE_API_SECRET`
- `BYBIT_API_KEY` / `BYBIT_API_SECRET`

If auth is unavailable, it fails soft and keeps template fees (still reproducible).

DEX fee model now supports a live network-friction input (`scripts/build_network_friction.py`):
- pulls Solana recent priority-fee data + base tx fee to estimate Jupiter network fee bps at current notional
- writes `data/network_friction.latest.json`
- `build_live_cex_dex_candidates.py` auto-loads this file and adds `router_fee_bps + network_fee_bps` into candidate fee math

## GitHub Pages Dashboard

A live static dashboard is deployed by GitHub Actions every 2 hours:

- Workflow: `.github/workflows/pages-dashboard.yml`
- Expected URL: `https://showyilu.github.io/master-trading-intel/`

If market APIs fail temporarily, the workflow falls back to the latest committed/sample candidates so the page remains available.

## Vercel Deployment

This repo is also ready for Vercel:

- Config: `vercel.json`
- Build entrypoint: `python3 scripts/build_for_web.py`
- Static output: `site/`

One-click import:

- `https://vercel.com/new/clone?repository-url=https://github.com/Showyilu/master-trading-intel`

