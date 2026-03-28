# Xander Maintainer — Manual Fulfillment Guide

## Overview

You sell AI PR reviews. When a customer pays, you receive the PR URL. You run the review and send them the Markdown report within 2 hours.

## Prerequisites

- Server with `gh` CLI authenticated (repo scope)
- OpenRouter/OpenAI key set in environment (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`)
- Python dependencies: `xander-operator` installed (already done)

## Step-by-Step Fulfillment

1. **Receive PR URL** (via email, Telegram, etc.)

2. **Run the review**
   ```bash
   cd /root/.openclaw/workspace
   python3 products/xander-maintainer/review_pr.py <PR_URL> --output report.md
   ```
   - Wait for completion (usually 30–90 seconds).
   - If error: retry once. If still fails, notify customer and refund.

3. **Verify report**
   - Open `report.md` in an editor.
   - Ensure it contains sections: Summary, Bugs, Security, Suggestions, Test Coverage, Verdict.
   - If content seems off, regenerate with `--json` flag to debug.

4. **Send to customer**
   - Copy the entire Markdown content.
   - Send via email or chat.
   - Include a short note:
     ```
     Here’s your AI PR review from Xander Maintainer. Let me know if you have questions.
     Next steps: apply suggestions, request changes, or merge if approved.
     ```

5. **Log the sale**
   - Append to `products/xander-maintainer/sales_log.md`:
     ```markdown
     - 2026-03-28 PR https://github.com/owner/repo/pull/123 — customer@example.com — $19 (single)
     ```
   - Keep for taxes and support.

6. **For monthly subscriptions**
   - Store customer email and date.
   - At month end, send a thank you + offer to continue.

## Pricing Options

- Single PR review: $19 (one-time)
- Monthly unlimited: $79 (cap at X repos to avoid abuse; track per customer)

## Refund Policy

- If review fails to generate (technical error on our side) → full refund.
- If customer unsatisfied → discretionary refund within 7 days.

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `gh: command not found` | Install GitHub CLI (`apt install gh`) and `gh auth login` |
| `gh: not authenticated` | Run `gh auth refresh -h github.com -s repo` or re-login |
| LLM timeout/error | Check OpenRouter quota; retry; if persistent, switch to backup model |
| Diff too large | Large diffs may exceed LLM context; advise customer to split PR |

## Scaling

When you have >5 reviews/week:
- Automate ingestion (email → queue)
- Use GitHub App instead of PAT for better rate limits
- Add a simple dashboard (Flask + SQLite)
- Outsource delivery to a script

---

**Keep this guide open while fulfilling.** Questions? Update this doc.
