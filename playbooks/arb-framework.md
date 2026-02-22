# Arbitrage Framework

## Opportunity Types
1. CEX-CEX spread
2. CEX-DEX spread
3. Cross-chain token dislocation
4. Funding-rate capture / basis

## Evaluation Formula
Net Edge = Gross Spread - (Trading Fees + Funding + Slippage + Borrow + Transfer + Latency Risk Premium)

## Must-Pass Checks
- Liquidity depth sufficient for target size
- Transfer/settlement path is reliable
- Execution latency does not erase edge
- Counterparty and smart-contract risks acceptable

## Abort Conditions
- Spread compresses below threshold
- Unexpected volatility spike
- API/order route instability
