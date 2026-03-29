# Contributing to OpenClaw

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/openclaw.git`
3. Create a branch: `git checkout -b my-feature-branch`
4. Make changes and test
5. Commit: `git commit -am 'Add some feature'`
6. Push: `git push origin my-feature-branch`
7. Open a Pull Request

## Development Setup

- Install dependencies: `pip install -r requirements.txt` (if applicable)
- Install Node dependencies: `npm install` (if applicable)
- Copy `.env.example` to `.env` and configure as needed
- Run the gateway: `python gateway.py` (or as documented)

## Code Style

- Python: Follow PEP 8, use `black` for formatting, `ruff` for linting
- JavaScript/TypeScript: Prettier, ESLint
- Configuration: YAML files should be properly formatted

## Commit Messages

We follow conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, etc.

## Pull Request Process

1. Ensure all tests pass (CI must be green)
2. Update documentation if needed
3. PR must be reviewed by at least one maintainer
4. Squash merge is preferred

## Branch Protection

The `main` branch is protected. Direct pushes are not allowed. All changes must go through PRs with required reviews and passing CI.

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Questions?

Open an issue with the "question" template or reach out via discussions.

---

Thank you for contributing!