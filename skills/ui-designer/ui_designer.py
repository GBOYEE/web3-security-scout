#!/usr/bin/env python3
"""
UI Designer Skill — generates UI components using LLM.
"""

import os
import sys
import json
from pathlib import Path

# Add xander-operator to path
sys.path.insert(0, str(Path(__file__).parent.parent / "polish" / "xander-operator"))

from xander_operator.llm import generate_response

def generate_ui(prompt: str) -> str:
    """Generate UI code or design advice using LLM."""
    system = """You are an expert UI/UX designer and frontend engineer.
You produce clean, accessible, responsive HTML with Tailwind CSS.
When asked for a component, output only the code (no extra commentary).
When asked for colors or suggestions, output in plain text.
Always follow modern best practices."""
    full_prompt = f"{system}\n\nUser request: {prompt}\n\nResponse:"
    resp = generate_response(full_prompt, max_tokens=2000, temperature=0.3)
    return resp or "Failed to generate UI."

def handle_message(message: str) -> str:
    """Entry point for OpenClaw agent calls."""
    # Simple routing based on keywords
    lower = message.lower()
    if any(kw in lower for kw in ["button", "card", "form", "navbar", "hero", "component", "html"]):
        return generate_ui(message)
    elif any(kw in lower for kw in ["color", "palette", "scheme"]):
        return generate_ui(message)
    elif any(kw in lower for kw in ["review", "accessibility", "responsive"]):
        return generate_ui(message)
    else:
        return "I can generate UI components, suggest palettes, or review designs. What do you need?"

if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not msg:
        print("Usage: ui_designer.py <prompt>")
        sys.exit(1)
    print(handle_message(msg))
