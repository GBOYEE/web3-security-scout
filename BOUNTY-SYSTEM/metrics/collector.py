#!/usr/bin/env python3
"""Collect resource and cost metrics for the bounty system."""

import psutil
import time
import json
from pathlib import Path

METRICS_FILE = Path("../memory/metrics.json")  # relative to BOUNTY-SYSTEM

def collect():
    data = {
        "timestamp": time.time(),
        "ram_mb": psutil.Process().memory_info().rss // 1024 // 1024,
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "llm_calls_today": 0,  # TODO: from cache DB
        "llm_cost_usd": 0.0,
    }
    if METRICS_FILE.exists():
        try:
            existing = json.loads(METRICS_FILE.read_text())
        except:
            existing = []
    else:
        existing = []
    existing.append(data)
    # keep last 1000 points
    METRICS_FILE.write_text(json.dumps(existing[-1000:], indent=2))

if __name__ == "__main__":
    collect()
