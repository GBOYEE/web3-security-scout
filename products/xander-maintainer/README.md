# Xander Maintainer

AI-powered Pull Request review service. Fast, thorough, autonomous.

## Quick Start (for you, the seller)

1. Ensure prerequisites:
   - `gh` CLI authenticated with `repo` scope
   - Environment variables set:
     ```bash
     export OPENAI_API_KEY=sk-or-...
     export OPENAI_BASE_URL=https://openrouter.ai/api/v1
     export OPENAI_MODEL=stepfun/step-1-flash
     ```
   - xander-operator installed: `cd polish/xander-operator && .venv/bin/pip install -e .`

2. Run a review:
   ```bash
   python3 products/xander-maintainer/review_pr.py https://github.com/owner/repo/pull/123 --output report.md
   ```

3. Fulfill:
   - Send `report.md` to customer
   - Log sale in `products/xander-maintainer/sales_log.md`

See `FULFILLMENT.md` for complete guide.

## Pricing

- Single PR: $19
- Monthly unlimited: $79/mo

## Tech Stack

- OpenRouter (StepFlash) for LLM
- GitHub CLI for PR data
- xander-operator core (reuse existing install)
- Simple manual fulfillment (initially)

## Roadmap

- [ ] GitHub App integration (no PAT)
- [ ] Automated delivery webhook
- [ ] Customer dashboard
- [ ] Stripe/LemonSqueezy auto-provision

---

**Ship it.** Get first customer within 48h.
