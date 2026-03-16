# Architecture

Web3 Security Scout consists of:

- **Scanner**: polls bounty APIs, filters by reward and severity
- **Analyzer**: uses `web3-security-scout` skill to check contract patterns
- **PoC Generator**: builds minimal exploit proof
- **Submitter**: creates report on Immunefi

All components communicate via OpenClaw hive message bus.

## Data Flow
1. Scanner finds target → broadcast `bounty_found`
2. Developer agent picks up → analyze → return `analysis_report`
3. Hunter composes report → submit via API

## Configuration
Set environment variables: `IMMUNEFI_API_KEY`, `ETHERSCAN_API_KEY`, `OPENROUTER_API_KEY`.