#!/usr/bin/env python3
"""
OpenClaw Gateway — secure front door for AI agents.
Provides rate limiting, HMAC validation, health checks, and routing.
"""

import os
import time
import hmac
import hashlib
import json
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="OpenClaw Gateway", version="1.0.0")

# Configuration
SECRET_KEY = os.getenv("OPENCLAW_SECRET", "changeme-secret-key")
RATE_LIMIT = int(os.getenv("OPENCLAW_RATE_LIMIT", "60"))  # requests per minute

# Simple in-memory rate limiter (for production use Redis)
rate_store = {}  # {identifier: [timestamps...]}

def verify_signature(payload: bytes, signature: Optional[str]) -> bool:
    """Verify HMAC-SHA256 signature of incoming webhook."""
    if not signature:
        return False
    expected = hmac.new(SECRET_KEY.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def rate_limiter(identifier: str) -> bool:
    """Allow up to RATE_LIMIT requests per minute per identifier."""
    now = time.time()
    window_start = now - 60
    times = rate_store.get(identifier, [])
    # Keep only recent timestamps
    times = [t for t in times if t > window_start]
    if len(times) >= RATE_LIMIT:
        return False
    times.append(now)
    rate_store[identifier] = times
    return True

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Skip verification for health endpoint
    if request.url.path == "/health":
        return await call_next(request)

    # Check rate limit by IP or identifier
    client_ip = request.client.host
    if not rate_limiter(client_ip):
        return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)

    response = await call_next(request)
    return response

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}

@app.post("/hooks/github")
async def github_webhook(request: Request, x_hub_signature_256: Optional[str] = Header(None)):
    payload = await request.body()
    if not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    # Parse event
    event = request.headers.get("X-GitHub-Event", "unknown")
    data = json.loads(payload.decode())
    # For now, just acknowledge
    # TODO: enqueue task for xander-operator via SQLite or message queue
    return {"status": "received", "event": event}

# Additional agent-specific endpoints can be added here

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
