# 🎯 Web3 Security Scout

Automated bug bounty scanner for Web3 protocols. Integrated with OpenClaw hive.

[![Open Issues](https://img.shields.io/github/issues-raw/YOUR_USER/web3-security-scout)](https://github.com/YOUR_USER/web3-security-scout/issues)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/YOUR_USER?label=Sponsor%20%26%20Support)](https://github.com/sponsors/YOUR_USER)

## Features
- Continuous monitoring of Immunefi and HackerOne
- Smart contract analysis using `web3-security-scout` skill
- **Severity scoring** (CVSS‑inspired) with aggregate risk label per scan
- PoC generation for eligible bounties
- Seamless integration with OpenClaw agents

## Quickstart
```bash
pip install -r requirements.txt
export IMMUNEFI_API_KEY=your_key
python -m web3_security_scout.scan
```

## Severity Scoring
The scout assigns a CVSS-inspired 0–10 score to each finding and computes an aggregate severity for the whole scan. Labels:
- **Critical** (≥9.0)
- **High** (7.0–8.9)
- **Medium** (4.0–6.9)
- **Low** (<4.0)

Use `w3-scout --json` for machine-readable output.

## Configuration
See `docs/` for detailed setup.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). We welcome issues, PRs, and community feedback.

## License
MIT

---

*If you find this tool valuable, consider sponsoring its development.*