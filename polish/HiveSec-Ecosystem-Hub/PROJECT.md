# HiveSec Ecosystem Hub

## Vision

Streamlit dashboard for multi‑agent security operations: visualize agent status, task queues, results, and system health. Central control panel for Xander Operator and security scanners.

## Goals (v1)

- Real‑time task status display
- Agent health metrics
- Result explorer (browse logs, outputs)
- Manual task injection (for ad‑hoc runs)

## Non‑Goals

- Not a full-blown SIEM
- Not a persistent storage backend (uses SQLite behind agents)

## Tech Stack

- Streamlit (Python)
- Plotly/Altair for charts
- SQLite queries directly against operator DB
- Optional: Redis pub/sub for live updates

## Current State

Code exists but may be outdated. Needs:
- Connection to current operator schema (tasks.db)
- Auth (simple shared secret or integrate with OpenClaw gateway)
- Polish UI and error handling

## Immediate Next Steps

1. Update queries to match current TaskStore schema
2. Add simple authentication (password or token)
3. Deploy behind Nginx with password protection
4. Add auto‑refresh and sound alerts for task completion
5. Document usage and deployment
