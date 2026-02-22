# How Others Find Arbitrage Edge (Practical Notes)

_Last updated: 2026-02-22 UTC_

## 1) Common playbooks used by profitable teams

### A. Funding-rate carry (spot ↔ perp)
- Core structure: hold **delta-neutral** inventory (long spot + short perp, or reverse when funding flips)
- PnL source: periodic funding payments, not directional price bet
- Why it works: structural imbalance in long/short demand
- Key fail mode: funding flips fast; borrow costs / fees eat carry

### B. Cross-exchange funding basis
- Core structure: long perp on lower funding venue + short perp on higher funding venue
- PnL source: spread in funding rates across venues
- Key fail mode: capital fragmentation + liquidation risk if leverage too high

### C. CEX-CEX top-of-book spread
- Core structure: buy low venue, sell high venue
- Reality check: this edge usually dies after taker+taker fees and latency
- Survivable only if one of:
  1) better fee tier / maker rebates
  2) pre-positioned inventory on both venues
  3) very fast execution + strict filters

### D. CEX-DEX dislocation
- Core structure: use DEX quote mispricing vs CEX fair reference
- Key fail mode: false edge from bad routes/wrapped-token depeg, gas and route impact not modeled
- Needed guardrails: reference deviation filter, crossed-quote filter, route quality + size-aware impact

---

## 2) What separates “real edge” from fake signals

1. **Net edge first**
   - gross edge is meaningless alone
   - must score: gross - fees - slippage - latency risk - transfer risk

2. **Execution feasibility**
   - depth-aware slippage by size bucket (1k / 5k / 10k)
   - transfer path + settlement latency modeled

3. **Positioning design**
   - pre-position inventory to reduce transfer dependency
   - avoid over-reliance on one venue/router

4. **Risk discipline**
   - leverage caps
   - hard invalidation conditions before entry
   - fail closed when data quality degrades

---

## 3) How we apply this to master-trading-intel (immediate)

### Immediate (next 24-48h)
- Add depth snapshots for Binance/Bybit and build size-aware slippage curve
- Add rejection-reason aggregation dashboard:
  - fee-dominated
  - slippage-dominated
  - latency/transfer-dominated
- Keep strict quote sanity guards for DEX routes

### Next (48-96h)
- Add funding-rate data adapters and implement first delta-neutral carry scanner
- Split shortlist into two books:
  1) execution-now (high-confidence)
  2) monitor-list (near-threshold)

### Goal
- Move from “find spreads” to “find executable net-positive opportunities”.

---

## Sources consulted
- Amberdata blog: funding-rate arbitrage mechanics and operational requirements
- CoinGlass learn: spot-perp and cross-exchange funding examples + practical caveats
