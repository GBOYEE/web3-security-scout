# Roadmap: Web3 Security Scout

## Overview

Web3 Security Scout progresses from a prototype scanner to a comprehensive, CI-ready security analysis tool covering multiple languages andchains with high accuracy.

## Phases

- [ ] **Phase 1: Core Reliability** - Tests, CI, detection accuracy
- [ ] **Phase 2: Languages** - Add Rust and Move support beyond Solidity
- [ ] **Phase 3: Integration** - CI actions, SARIF, PR annotations
- [ ] **Phase 4: Scale** - Parallel scanning, cache results, cloud API

## Phase Details

### Phase 1: Core Reliability
**Goal**: Solidify Solidity scanning with high precision
**Depends on**: None
**Requirements**: REQ-01, REQ-02, REQ-05
**Success Criteria**:
  1. Unit tests for all vulnerability detectors (pytest)
  2. Integration tests on sample vulnerable contracts (80%+ recall)
  3. False positive rate < 20% on real-world contracts
  4. CI pipeline runs tests, coverage, and lint on PRs
  5. Documentation: installation, usage, contributing
**Plans**: 4 plans

Plans:
- [ ] 01-01: Build comprehensive test suite for reentrancy, overflow, access control
- [ ] 01-02: Integrate Slither as baseline, measure delta with LLM findings
- [ ] 01-03: Configure GitHub Actions (test, coverage, markdown-lint)
- [ ] 01-04: Write user guide and example reports

### Phase 2: Languages
**Goal**: Expand support to multiple blockchain languages
**Depends on**: Phase 1
**Requirements**: REQ-03
**Success Criteria**:
  1. Rust analyzer covers common smart contract patterns
  2. Move (Sui/Aptos) basic detection
  3. Unified finding schema across languages
**Plans**: TBD

### Phase 3: Integration
**Goal**: Make the scanner easy to run in CI/CD
**Depends on**: Phase 2
**Success Criteria**:
  1. GitHub Action: `web3-security-scout/action`
  2. SARIF output for GitHub Code Scanning
  3. Automatic PR comments for new findings
**Plans**: TBD

### Phase 4: Scale
**Goal**: Handle large codebases and provide cloud API
**Depends on**: Phase 3
**Success Criteria**:
  1. Parallel scanning of contracts reduces time by 50%
  2. Redis cache for LLM responses
  3. Deployed API at api.web3scout.io (optional)
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Reliability | 0/4 | Not started | - |
| 2. Languages | 0 | Not started | - |
| 3. Integration | 0 | Not started | - |
| 4. Scale | 0 | Not started | - |

---

*This roadmap will evolve as we validate detection quality.*