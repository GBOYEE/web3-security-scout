#!/usr/bin/env python3
"""
Proactive Coach — XANDER takes initiative.
Scheduled check-ins, mood tracking, goal nudges, therapeutic support.
"""

import os
import sys
import json
import yaml
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Add xander-operator to path
sys.path.insert(0, '/root/.openclaw/workspace/polish/xander-operator')

WORKSPACE = Path('/root/.openclaw/workspace')
MEMORY_DIR = WORKSPACE / "memory"
PERSONAL_FILE = WORKSPACE / "PERSONAL.md"
GOALS_FILE = WORKSPACE / "goals.yaml"

def load_config() -> Dict:
    cfg_path = WORKSPACE / "skills" / "proactive-coach" / "skill-config.yaml"
    if cfg_path.exists():
        with open(cfg_path) as f:
            return yaml.safe_load(f)
    return {}

config = load_config()
timezone_offset = 1  # Europe/Berlin = UTC+1 (simplified)

def now_local():
    return datetime.now()  # TODO: handle timezone properly

def should_send_checkin() -> tuple[bool, str]:
    """Check if it's time for a scheduled check-in. Returns (should_send, which)."""
    schedule = config.get("schedule", {})
    t = now_local().time()
    for kind, hhmm in schedule.items():
        h, m = map(int, hhmm.split(":"))
        check_time = time(h, m)
        # Compute minutes difference
        now_minutes = t.hour * 60 + t.minute
        check_minutes = h * 60 + m
        diff = abs(now_minutes - check_minutes)
        if diff <= 30:  # within 30 minutes
            last_file = MEMORY_DIR / f"last_{kind}_checkin.txt"
            if not last_file.exists() or (now_local() - datetime.fromtimestamp(last_file.stat().st_mtime)) > timedelta(hours=20):
                return True, kind
    return False, ""

def mark_checkin(kind: str):
    MEMORY_DIR.mkdir(exist_ok=True)
    flag = MEMORY_DIR / f"last_{kind}_checkin.txt"
    flag.write_text(datetime.now().isoformat())

def get_prompt(kind: str) -> str:
    prompts_dir = WORKSPACE / "skills" / "proactive-coach" / "prompts"
    file = prompts_dir / f"{kind}.md"
    if file.exists():
        return file.read_text()
    # Fallback built-in
    texts = {
        "morning": "Good morning! What's your #1 priority today? 🎯",
        "midday": "Quick pulse: energy level 1–5? Any blockers? Need a break strategy? 💡",
        "evening": "Reflection time: What drained you? What energized you? One win today? 🌅"
    }
    return texts.get(kind, "Check-in:")

def detect_therapist_mode(message: str) -> bool:
    phrases = config.get("therapist_phrases", [])
    lower = message.lower()
    return any(phrase in lower for phrase in phrases)

def log_mood_energy(message: str):
    """Parse mood/energy from reply and append to daily log."""
    # Look for tags like 🧘 or "energy: 3" or "mood: stressed"
    log_file = MEMORY_DIR / f"{datetime.now():%Y-%m-%d}.md"
    if not log_file.exists():
        return
    entry = f"\n- Mood/Energy log: {message}"
    with open(log_file, "a") as f:
        f.write(entry)

def generate_proactive_message() -> str:
    should, kind = should_send_checkin()
    if should:
        mark_checkin(kind)
        prompt = get_prompt(kind)
        return f"[XANDER {kind.title()} Check-in] {prompt}"
    return ""

def handle_user_message(message: str) -> str:
    """Main entry point for OpenClaw skill invoked by chat."""
    # 1. Therapist mode?
    if detect_therapist_mode(message):
        return therapist_response(message)

    # 2. Mood/energy logging?
    if any(tag in message for tag in config.get("mood_tags", [])) or "energy:" in message.lower():
        log_mood_energy(message)
        return "Noted. 💙"

    # 3. Goals check?
    if "goals" in message.lower():
        return goals_status()

    # 4. Default: maybe a scheduled check-in
    proactive = generate_proactive_message()
    if proactive:
        return proactive
    return ""  # no response

def maybe_check_in() -> str:
    """For heartbeat: if it's time for a check-in, return message; else empty."""
    should, kind = should_send_checkin()
    if should:
        mark_checkin(kind)
        prompt = get_prompt(kind)
        return f"[XANDER {kind.title()} Check-in] {prompt}"
    return ""

def therapist_response(user_msg: str) -> str:
    """Simple therapeutic responses (will be replaced by LLM later)."""
    return (
        "I'm here. Let's talk.\n\n"
        "What's weighing on your mind?\n"
        "You can share freely — no judgment."
    )

def goals_status() -> str:
    if not GOALS_FILE.exists():
        return "No goals set. Create goals.yaml with your OKRs."
    with open(GOALS_FILE) as f:
        goals = yaml.safe_load(f)
    # Summarize
    lines = ["📊 Goals Overview:\n"]
    for obj in goals.get("objectives", []):
        lines.append(f"**{obj['title']}**")
        for kr in obj.get("key_results", []):
            lines.append(f"- {kr}")
        lines.append("")
    return "\n".join(lines)

def weekly_report():
    """Generate weekly insights HTML (run via cron or manual)."""
    # Collect daily logs for past week
    # Count mood tags, task completion from xander-operator DB
    # Output to memory/reports/weekly-YYYY-MM-DD.html
    pass

# OpenClaw webhook handler entry point
def webhook_handler(body: bytes, headers: dict) -> str:
    # Not a webhook skill, runs in chat context
    return ""

if __name__ == "__main__":
    if "--maybe-check-in" in sys.argv:
        print(maybe_check_in())
    elif len(sys.argv) > 1:
        print(handle_user_message(" ".join(sys.argv[1:])))
    else:
        print("Usage: coach.py [message] | --maybe-check-in")
