# Execution Profiles (Scanner)

用于把同一批候选在不同执行现实下重算净边际：

`net_edge_bps = gross - fees - slippage - latency - transfer_risk`

## Profiles

### 1) `taker_default`（默认，最严格）
- fee multiplier: `1.00`
- slippage multiplier: `1.00`
- latency multiplier: `1.00`
- transfer delay multiplier: `1.00`
- transfer penalty: `0.45 bps/min`
- gate: `min_net_edge_bps >= 8.0`

### 2) `maker_inventory`
- 假设：有预置库存，部分 maker 执行
- fee multiplier: `0.42`
- slippage multiplier: `0.72`
- latency multiplier: `0.95`
- transfer delay multiplier: `0.30`
- transfer penalty: `0.24 bps/min`
- gate: `min_net_edge_bps >= 4.5`

### 3) `maker_inventory_vip`
- 假设：低费等级 + 更优执行
- fee multiplier: `0.25`
- slippage multiplier: `0.60`
- latency multiplier: `0.90`
- transfer delay multiplier: `0.20`
- transfer penalty: `0.18 bps/min`
- gate: `min_net_edge_bps >= 3.0`

## Usage

```bash
python3 scripts/scan_opportunities.py \
  --input data/opportunity_candidates.combined.live.json \
  --execution-profile maker_inventory \
  --output-json opportunities/shortlist-maker-inventory.json \
  --output-md opportunities/dashboard-maker-inventory.md \
  --output-summary opportunities/rejection-summary-maker-inventory.json
```

> 硬规则：任何 profile 都不能跳过 fee/slippage/latency/transfer 风险项。
