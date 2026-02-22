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
python3 scripts/build_live_cex_candidates.py
python3 scripts/scan_opportunities.py \
  --input data/opportunity_candidates.live.json \
  --output-json opportunities/shortlist-latest.json \
  --output-md opportunities/dashboard-latest.md
```

### 3) Live CEX + DEX pipeline (Binance/Bybit + Jupiter)
```bash
python3 scripts/build_live_cex_candidates.py
python3 scripts/build_live_cex_dex_candidates.py
python3 scripts/merge_candidate_files.py \
  --inputs data/opportunity_candidates.live.json data/opportunity_candidates.cex_dex.live.json \
  --output data/opportunity_candidates.combined.live.json
python3 scripts/scan_opportunities.py \
  --input data/opportunity_candidates.combined.live.json \
  --output-json opportunities/shortlist-latest.json \
  --output-md opportunities/dashboard-latest.md
```

Outputs:
- `data/normalized_quotes_cex_latest.json`
- `data/normalized_quotes_dex_latest.json`
- `data/opportunity_candidates.live.json`
- `data/opportunity_candidates.cex_dex.live.json`
- `data/opportunity_candidates.combined.live.json`
- `opportunities/shortlist-latest.json`
- `opportunities/dashboard-latest.md`

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

