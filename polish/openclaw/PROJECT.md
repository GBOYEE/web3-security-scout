# OpenClaw — Secure AI Gateway

## Vision

Provide a production‑grade, secure front door for AI agents: rate limiting, HMAC validation, health checks, and routing. Acts as the control plane for autonomous systems.

## Goals (v1)

- Public API endpoint for agent webhooks
- Strong authentication (HMAC signatures)
- Rate limiting per client
- Health and metrics endpoints
- Easy deploy (Docker + Nginx)

## Non‑Goals

- Not an agent itself (it’s a gateway)
- Not a database or long‑term storage

## Tech Stack

- Python (FastAPI)
- Uvicorn/Gunicorn
- Redis (optional for rate limiting)
- Nginx (TLS termination)
- Docker

## Current State

Code exists under `polish/openclaw/` but not deployed. Need to:
- Create systemd service or Docker Compose
- Configure Nginx upstream and TLS
- Wire to xander-operator backend
- Test with sample webhook

## Immediate Next Steps

1. Write `main.py` FastAPI app (reference existing code)
2. Dockerize: Dockerfile + docker-compose.yml
3. Deploy behind Nginx with SSL
4. Document configuration (ports, secrets)
5. Add Prometheus metrics endpoint (optional)
