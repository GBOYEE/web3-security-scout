# Project: Web3 Security Scout

## Project Reference

- Repository: GBOYEE/web3-security-scout
- Branch: main
- Package: web3_scout

## Core Value

AI-augmented smart contract vulnerability scanner that combines static analysis with LLM reasoning to find security issues in Solidity, Rust, and Move contracts.

## Target Users

Smart contract auditors, DeFi developers, security researchers.

## Requirements

### Functional
- Scan Solidity, Rust, and Move codebases
- Detect common vulnerabilities (reentrancy, overflow, oracle manipulation)
- Generate human-readable reports with proof-of-concept
- Support CI integration (GitHub Actions, GitLab CI)
- Differential scanning (compare two commits)

### Non-Functional
- Fast scanning (< 2 min for typical contracts)
- High precision and recall (low false positives)
- Clear explanation of each finding
- Export JSON and SARIF

## Constraints

- Python 3.11+
- No proprietary model lock-in (can use OpenAI or local LLM)
- Minimal external dependencies for easy installation

## Technical Stack

- Python, Slither (static analysis)
- OpenAI API or Ollama for LLM reasoning
- Pydantic models for findings
- FastAPI for scanning service (optional)

## Dependencies

- `slither` for Solidity analysis
- `tree-sitter` for parsing other languages
- LLM client library

## Interfaces

- CLI: `python -m web3_scout scan /path/to/contracts`
- API: `/scan` endpoint accepting file upload or repo URL
- Output: JSON, SARIF, markdown report

## Acceptance Criteria

- Scanner detects at least 80% of known vulnerable patterns in test suite
- False positive rate < 20%
- Report includes line numbers, vulnerability type, severity, and explanation
- CI integration works (example GitHub Action provided)

---

*Last updated: 2026-03-29*