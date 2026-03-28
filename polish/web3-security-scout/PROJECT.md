# AI PR Reviewer (web3-security-scout)

## Vision

Autonomous GitHub PR review agent that fetches diffs, analyzes code with an LLM, and posts structured comments (bugs, security issues, suggestions) within ~2 hours. Includes webhook validation and rate limiting.

## Goals (v1)

- Receive GitHub webhook events (pull_request)
- Fetch PR diff
- Analyze using local LLM (Ollama) or OpenAI
- Post structured review comments
- Landing page for signup/beta

## Non‑Goals

- Not a full SAST scanner (focus on PR review)
- Not a multi‑repo scanner (single repo per instance)

## Tech Stack

- Python (FastAPI for webhook endpoint)
- GitHub App or PAT authentication
- Ollama / OpenAI API
- Nginx reverse proxy
- sqlite for simple state (optional)

## Current State

CLI tool and basic webhook receiver exist in this repo; needs:
- Proper webhook signature verification (HMAC)
- Rate limiting
- Robust error handling and retry
- Deployment configuration
- Landing page integration

## Immediate Next Steps

1. Harden webhook endpoint (validate signatures)
2. Add rate limiting (slowapi or similar)
3. Implement diff extraction and LLM prompt engineering
4. Create landing page (HTML) with signup form
5. Deploy to VPS behind Nginx + SSL
