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

Outputs:
- `data/normalized_quotes_cex_latest.json`
- `data/opportunity_candidates.live.json`
- `opportunities/shortlist-latest.json`
- `opportunities/dashboard-latest.md`

