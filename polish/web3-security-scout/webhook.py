#!/usr/bin/env python3
"""
AI PR Reviewer — webhook endpoint for GitHub pull requests.
Analyzes diffs and posts comments. Includes HMAC verification and rate limiting.
"""

import os
import time
import hmac
import hashlib
import json
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn

app = FastAPI(title="AI PR Reviewer", version="1.0.0")

# Config
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "changeme")
RATE_LIMIT = int(os.getenv("REVIEW_RATE_LIMIT", "10"))  # per minute

# Rate limiter (in-memory for now; use Redis in production)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def verify_github_signature(request: Request, call_next):
    if request.url.path == "/health":
        return await call_next(request)
    if request.url.path == "/hooks/github":
        signature = request.headers.get("X-Hub-Signature-256")
        payload = await request.body()
        expected = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
        expected_header = f"sha256={expected}"
        if not hmac.compare_digest(expected_header, signature or ""):
            return JSONResponse({"detail": "Invalid signature"}, status_code=401)
    response = await call_next(request)
    return response

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}

@app.post("/hooks/github")
@limiter.limit(f"{RATE_LIMIT}/minute")
async def github_hook(request: Request):
    event = request.headers.get("X-GitHub-Event", "unknown")
    payload = await request.json()
    # Basic validation: we only care about pull_request events
    if event != "pull_request":
        return {"status": "ignored", "reason": f"event {event} not handled"}
    # Extract PR details
    pr = payload.get("pull_request", {})
    pr_url = pr.get("html_url", "")
    # For now, just acknowledge; real implementation would fetch diff and use LLM
    # TODO: enqueue task to xander-operator for analysis
    return {"status": "received", "pr": pr_url, "event": event}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)
