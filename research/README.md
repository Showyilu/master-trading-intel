# Research Workspace

## Uniswap Upstream Source

- Path: `research/uniswap-ai-upstream`
- Type: git submodule (tracks upstream repository directly)
- Upstream: `https://github.com/Uniswap/uniswap-ai`

Why submodule instead of copying files:
1. Keeps our main repo lightweight
2. Preserves upstream commit history cleanly
3. Easy to pin/upgrade to a specific version for reproducible research

Current focus for extraction:
- `uniswap-trading` plugin patterns
- `uniswap-viem` integration flows
- Quote/routing logic we can adapt for arbitrage signal validation
