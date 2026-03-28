#!/usr/bin/env python3
"""
UI Designer Skill — generates UI components using LLM (Ollama).
"""

import os
import sys
import json
import time
from pathlib import Path

# ------------------ Locate workspace and load .env ------------------
workspace = Path(__file__).resolve().parent.parent.parent
env_path = workspace / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            k, _, v = line.partition("=")
            os.environ[k.strip()] = v.strip()
else:
    sys.stderr.write("Warning: .env not found\n")

# ------------------ Ensure venv and operator are on path ------------------
# Re-exec with venv python if needed
venv_py = workspace / "polish" / "xander-operator" / ".venv" / "bin" / "python"
if venv_py.exists() and sys.executable != str(venv_py):
    os.execv(str(venv_py), [str(venv_py)] + sys.argv)

# Add venv site-packages and operator source
site_pkgs = workspace / "polish" / "xander-operator" / ".venv" / "lib" / "python3.12" / "site-packages"
if site_pkgs.exists() and str(site_pkgs) not in sys.path:
    sys.path.insert(0, str(site_pkgs))
operator_src = str(workspace / "polish" / "xander-operator")
if operator_src not in sys.path:
    sys.path.insert(0, operator_src)

# ------------------ Import LLM client ------------------
try:
    from xander_operator.llm import generate_response
except ImportError as e:
    sys.stderr.write(f"Failed to import xander_operator.llm: {e}\n")
    sys.exit(1)

# ------------------ Generation logic with retry ------------------
def generate_ui(prompt: str, retries: int = 2, delay: float = 2.0) -> str:
    system = """You are an expert UI/UX designer and frontend engineer.
You produce clean, accessible, responsive HTML with Tailwind CSS.
When asked for a component, output only the code (no extra commentary).
When asked for colors or suggestions, output in plain text.
Always follow modern best practices."""
    full_prompt = f"{system}\n\nUser request: {prompt}\n\nResponse:"
    model = os.getenv("OPENAI_MODEL", "codellama:7b")
    for attempt in range(1, retries + 1):
        try:
            resp = generate_response(
                full_prompt,
                model=model,
                max_tokens=4000,
                temperature=0.3,
                use_cache=True
            )
            if resp:
                # Strip code fences if present
                if resp.startswith("```"):
                    lines = resp.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    resp = "\n".join(lines)
                return resp.strip()
        except Exception as e:
            sys.stderr.write(f"LLM attempt {attempt} failed: {e}\n")
            if attempt < retries:
                time.sleep(delay)
            else:
                raise
    return ""

def handle_message(message: str) -> str:
    """Entry point for OpenClaw agent calls."""
    lower = message.lower()
    if any(kw in lower for kw in ["button", "card", "form", "navbar", "hero", "component", "html", "page", "site"]):
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
    result = handle_message(msg)
    print(result)
